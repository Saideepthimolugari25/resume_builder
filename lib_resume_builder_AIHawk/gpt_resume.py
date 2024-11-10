import json
import os
import tempfile
import textwrap
import time
from datetime import datetime
from typing import Dict, List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

import logging

import openai
from dotenv import load_dotenv
from langchain_core.prompt_values import StringPromptValue
from requests.exceptions import HTTPError as HTTPStatusError

from langchain_core.messages.ai import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import TokenTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.gpt import AIAdapter, GPT

load_dotenv()

log_folder = 'log'
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, 'app.log')

# Configura il logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file, encoding='utf-8')]
)
logger = logging.getLogger(__name__)

class LLMLogger:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    @staticmethod
    def log_request(prompts, parsed_reply: Dict[str, Dict]):
        calls_log = os.path.join(global_config.LOG_OUTPUT_FILE_PATH, "open_ai_calls.json")
        if isinstance(prompts, StringPromptValue):
            prompts = prompts.text
        elif isinstance(prompts, Dict):
            prompts = {f"prompt_{i + 1}": prompt.content for i, prompt in enumerate(prompts.messages)}

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Extract token usage details from the response
        token_usage = parsed_reply["usage_metadata"]
        output_tokens = token_usage["output_tokens"]
        input_tokens = token_usage["input_tokens"]
        total_tokens = token_usage["total_tokens"]

        # Extract model details from the response
        model_name = parsed_reply["response_metadata"]["model_name"]
        prompt_price_per_token = 0.00000015
        completion_price_per_token = 0.0000006
        total_cost = (input_tokens * prompt_price_per_token) + (output_tokens * completion_price_per_token)

        log_entry = {
            "model": model_name,
            "time": current_time,
            "prompts": prompts,
            "replies": parsed_reply["content"],
            "total_tokens": total_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_cost": total_cost,
        }

        # Write the log entry to the log file in JSON format
        with open(calls_log, "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=4)
            f.write("\n")

class LoggerChatModel:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        max_retries = 15
        retry_delay = 10

        for attempt in range(max_retries):
            try:
                reply = self.llm(messages)
                parsed_reply = self.parse_llmresult(reply)
                LLMLogger.log_request(prompts=messages, parsed_reply=parsed_reply)
                return reply
            except (openai.RateLimitError, HTTPStatusError) as err:
                if isinstance(err, HTTPStatusError) and err.response.status_code == 429:
                    logger.warning(f"HTTP 429 Too Many Requests: Waiting for {retry_delay} seconds before retrying (Attempt {attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    wait_time = self.parse_wait_time_from_error_message(str(err))
                    logger.warning(f"Rate limit exceeded or API error. Waiting for {wait_time} seconds before retrying (Attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Unexpected error occurred: {str(e)}, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2

        logger.critical("Failed to get a response from the model after multiple attempts.")
        raise Exception("Failed to get a response from the model after multiple attempts.")

    def parse_llmresult(self, llmresult: AIMessage) -> Dict[str, Dict]:
        content = llmresult.content
        response_metadata = llmresult.response_metadata
        id_ = llmresult.id
        usage_metadata = llmresult.usage_metadata

        parsed_result = {
            "content": content,
            "response_metadata": {
                "model_name": response_metadata.get("model_name", ""),
                "system_fingerprint": response_metadata.get("system_fingerprint", ""),
                "finish_reason": response_metadata.get("finish_reason", ""),
                "logprobs": response_metadata.get("logprobs", None),
            },
            "id": id_,
            "usage_metadata": {
                "input_tokens": usage_metadata.get("input_tokens", 0),
                "output_tokens": usage_metadata.get("output_tokens", 0),
                "total_tokens": usage_metadata.get("total_tokens", 0),
            },
        }
        return parsed_result

class LLMResumer:
    def __init__(self, openai_api_key, strings):
        self.llm_cheap = LoggerChatModel(
            ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0.4)
        )
        self.strings = strings

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        # Preprocess a template string to remove unnecessary indentation.
        return textwrap.dedent(template)

    def set_resume(self, resume):
        self.resume = resume

    def generate_section(self, prompt_template: str, input_data: Dict[str, any]) -> str:
        prompt = ChatPromptTemplate.from_template(self._preprocess_template_string(prompt_template))
        chain = prompt | self.llm_cheap | StrOutputParser()
        return chain.invoke(input_data)

    def generate_html_resume(self) -> str:
        functions = {
            "header": lambda: self.generate_section(self.strings.prompt_header, {"personal_information": self.resume.personal_information}),
            "education": lambda: self.generate_section(self.strings.prompt_education, {"education_details": self.resume.education_details}),
            "work_experience": lambda: self.generate_section(self.strings.prompt_working_experience, {"experience_details": self.resume.experience_details}),
            "side_projects": lambda: self.generate_section(self.strings.prompt_side_projects, {"projects": self.resume.projects}),
            "achievements": lambda: self.generate_section(self.strings.prompt_achievements, {
                "achievements": self.resume.achievements,
                "certifications": self.resume.certifications,
                "job_description": self.job_description}),
            "certifications": lambda: self.generate_section(self.strings.prompt_certifications, {
                "certifications": self.resume.certifications,
                "job_description": self.job_description}),
            "additional_skills": lambda: self.generate_section(self.strings.prompt_additional_skills, {
                "languages": self.resume.languages,
                "interests": self.resume.interests,
                "skills": self._collect_skills()}),
        }

        # Use ThreadPoolExecutor to run the functions in parallel
        with ThreadPoolExecutor() as executor:
            future_to_section = {executor.submit(fn): section for section, fn in functions.items()}
            results = {}
            for future in as_completed(future_to_section):
                section = future_to_section[future]
                try:
                    result = future.result()
                    if result:
                        results[section] = result
                except Exception as exc:
                    logger.error(f'{section} generated an exception: {exc}')

        full_resume = "<body>\n"
        full_resume += f"  {results.get('header', '')}\n"
        full_resume += "  <main>\n"
        full_resume += f"    {results.get('education', '')}\n"
        full_resume += f"    {results.get('work_experience', '')}\n"
        full_resume += f"    {results.get('side_projects', '')}\n"
        full_resume += f"    {results.get('achievements', '')}\n"
        full_resume += f"    {results.get('certifications', '')}\n"
        full_resume += f"    {results.get('additional_skills', '')}\n"
        full_resume += "  </main>\n"
        full_resume += "</body>"
        return full_resume

    def _collect_skills(self) -> set:
        skills = set()
        if self.resume.experience_details:
            for exp in self.resume.experience_details:
                if exp.skills_acquired:
                    skills.update(exp.skills_acquired)
        if self.resume.education_details:
            for edu in self.resume.education_details:
                if edu.exam:
                    for exam in edu.exam:
                        skills.update(exam.keys())
        return skills

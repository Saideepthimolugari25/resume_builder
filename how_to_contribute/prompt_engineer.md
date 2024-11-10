
# How to Contribute: Prompt Engineers

Welcome to **Resume_Builder_AIHawk**! As a prompt engineer, your expertise is essential in refining the AI-powered resume builder prompts, ensuring high-quality, ATS-friendly resumes for users. This guide provides step-by-step instructions on how to create, test, and contribute your custom prompts.

Once your prompts are merged, they will also be included in the main repository at [feder-cr/linkedIn_auto_jobs_applier_with_AI](https://github.com/feder-cr/linkedIn_auto_jobs_applier_with_AI), giving your work significant visibility.

Thank you for contributing and helping to improve our resume-building prompts!

## Creating and Adding Your Custom Prompts

### 1. **Design Your Custom Prompt**

Create a new prompt that enhances or expands the resume creation capabilities. Below are examples of key areas to cover:

- **Header Prompt**:
  Ensures contact information is formatted clearly, including full name, location, phone, email, LinkedIn, and GitHub links. Omit fields if data is `None`.

- **Education Prompt**:
  Describes educational background, including institution, degree, grade, and coursework, if relevant to the job description.

- **Work Experience Prompt**:
  Details work experience, aligning responsibilities, achievements, and skills with the job description. Uses keywords, quantifies results where possible, and achieves high alignment with the user’s existing experience.

- **Side Projects Prompt**:
  Highlights notable projects with links, recognition, and technical contributions.

- **Achievements and Certifications Prompts**:
  Lists significant achievements, awards, and certifications relevant to the job, including brief descriptions and relevance.

- **Additional Skills Prompt**:
  Lists specific skills or technologies, including proficiency levels and experience.

### **Example Prompts:**

Use these as a starting point for writing your own:
```python
from lib_resume_builder_AIHawk.template_base import *

prompt_header = """
Act as an HR expert specializing in ATS-friendly resumes. Your task is to create a professional resume header with:
- Contact Information: Include name, location, phone, email, LinkedIn, GitHub.
- Formatting: Ensure details are clear and readable.

If a field is missing (e.g., LinkedIn), omit it.

- **My information:**  
  {personal_information}
""" + prompt_header_template
```

### 2. **Fork the Repository**

- Visit the [Resume_Builder_AIHawk GitHub repository](https://github.com/feder-cr/lib_resume_builder_AIHawk).
- Click the **Fork** button to create a copy under your GitHub account.

### 3. **Clone Your Fork**

Clone the forked repository to your local machine:

git clone https://github.com/yourusername/lib_resume_builder_AIHawk.git
cd lib_resume_builder_AIHawk


### 4. **Create a New Branch (Optional but Recommended)**

Create a new branch to work on your prompt enhancements:

git checkout -b feature/custom-prompt


## Implementing Your Prompt

5. **Add Your Prompt to the Template Base**

- Navigate to the `template_base` directory:

cd lib_resume_builder_AIHawk/template_base


- Create a new prompt file (e.g., `custom_prompt.py`) or edit an existing one, ensuring your prompt includes all necessary information and follows the structure guidelines.

6. **Test Your Prompts**

- Test the prompt to ensure it generates accurate, high-quality outputs aligned with job descriptions.
- Verify consistency, clarity, and adaptability across diverse resume data.

## Submitting Your Contribution

7. **Commit Your Changes**

- Add and commit your changes:

git add lib_resume_builder_AIHawk/template_base/custom_prompt.py
git commit -m "Add custom resume prompt"


8. **Push Your Changes**

- Push your changes to your forked repository:

git push origin feature/custom-prompt


9. **Create a Pull Request**

- Go to your forked repository on GitHub.
- Click on the **Compare & pull request** button.
- Provide a description of your changes, emphasizing how they improve the resume prompts.
- Click **Create pull request** to submit for review.

---

## Need Assistance?

If you have questions or need help with your contribution, join our [Telegram community](https://t.me/AIhawkCommunity). We’re here to support you!

Thank you for helping to enhance **Resume_Builder_AIHawk**! Your contributions make our resume tool more robust and impactful for all users. 🚀

import importlib.util
import sys
import os

def load_module(module_path: str, module_name: str):
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"The file at {module_path} does not exist.")

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(f"Could not load specification for module '{module_name}' from {module_path}.")

    if module_name in sys.modules:
        return sys.modules[module_name]

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        del sys.modules[module_name]
        raise ImportError(f"Failed to load module '{module_name}' due to error: {e}") from e

    return module

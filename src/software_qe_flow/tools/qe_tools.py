from crewai.tools import tool
from dotenv import load_dotenv
import requests
import json
import asyncio
from pydantic import SecretStr
import os
import sys
import io
import contextlib

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

@tool("Invoke API Tool")
def invoke_api_tool(url:str, http_method:str, path_params:dict, request_body: dict, query_params: dict) -> dict:
    """Useful for invoking an API with the given input."""
    # Implementation goes here
    baseUri = "http://petstore.swagger.io/v2/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer"
    }

    url = url.format(**path_params)

    print(f"Invoking API with URL: {url}")
    print(f"HTTP method: {http_method}")
    print(f"Request body with values: {request_body}")
    print(f"Query params: {query_params}")
    print(f"Path params: {path_params}")

    try:
        if http_method.upper() == "GET":
            print(f"URL was: {baseUri}{url}")
            response = requests.get(f"{baseUri}{url}", headers=headers, params=query_params)
            print(f"URL was: {response.request.url}")
        elif http_method.upper() == "POST":
            response = requests.post(f"{baseUri}{url}", headers=headers, json=request_body)
        elif http_method.upper() == "PUT":
            response = requests.put(f"{baseUri}{url}", headers=headers, json=request_body)
        elif http_method.upper() == "DELETE":
            response = requests.delete(f"{baseUri}{url}", headers=headers, json=request_body)
        else:
            raise Exception("Invalid HTTP method")
    except Exception as e:
        return {"response": "Error invoking API"}
    return response.json()


# @tool("Execute Python Script")
# def execute_python_file(script: str) -> dict:
#     """Executes a Python script in the current environment and returns the output or error."""

#     output = io.StringIO()
#     error = None
#     with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
#         try:
#             exec(script, {})
#         except Exception as e:
#             error = str(e)
#     return {
#         "output": output.getvalue(),
#         "error": error
#     }

@tool("Execute Python Script")
def execute_python_file(file_name: str) -> dict:
    """Executes a Python file in the current environment and returns the output or error."""
    import subprocess
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = f'{current_dir}/../../../output/cat_api_tests.py'
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('```python', '')
    content = content.replace('```', '')
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    subprocess.run(['python', full_path], check=True)
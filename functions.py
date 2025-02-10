import subprocess
import json
import requests

# AIProxy URL (assuming it's running locally)

AI_PROXY_URL = "http://aiproxy.sanand.workers.dev/openai/v1"

# Define function schemas

functions = [
    {
        "name": "install_library",
        "description": "Installs a Python library using pip.",
        "parameters": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "The name of the package to install."}
            },
            "required": ["package_name"],
        },
    },
    {
        "name": "run_python_file",
        "description": "Executes a Python script and returns the output.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the Python script file."}
            },
            "required": ["file_path"],
        },
    }
]

# Function to install a library
def install_library(package_name):
    try:
        result = subprocess.run(["pip", "install", package_name], capture_output=True, text=True)
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)

# Function to execute a Python file
def run_python_file(file_path):
    try:
        result = subprocess.run(["python", file_path], capture_output=True, text=True)
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)

# Function to process user input and call AIProxy
def chat_with_aiproxy(user_input):
    payload = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "user", "content": user_input}],
        "functions": functions,
        "function_call": "auto",  # Let OpenAI decide
    }

    response = requests.post(AI_PROXY_URL, json=payload)
    response_data = response.json()

    # Extract model's response
    response_message = response_data["choices"][0]["message"]

    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        function_args = json.loads(response_message["function_call"]["arguments"])

        # Call the appropriate function
        if function_name == "install_library":
            result = install_library(**function_args)
        elif function_name == "run_python_file":
            result = run_python_file(**function_args)
        else:
            result = "Unknown function."

        return result

    return response_message["content"]  # If no function call, return normal AI response

# Run chatbot loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    response = chat_with_aiproxy(user_input)
    print(f"Bot: {response}")

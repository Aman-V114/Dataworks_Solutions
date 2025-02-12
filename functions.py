import subprocess
import json
from unittest import result
import requests
import pydantic
import os
from config import Config_API
import requests

class DataworksSolutions(pydantic.BaseModel):
    messages: list
    functions: list
    function_call: str


# AIProxy URL (assuming it's running locally)
# Define function schemas


functions = [
    {
        "name": "A1",
        "description": "Installs uv if not present and runs datagen.py file on the github repo link provided",
        "parameters": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "The name of the package to install."}
            },
            "required": ["package_name"],
        },
    },
]


config_obj=Config_API()

print(config_obj.ChatEndpoint)

# Set the API endpoint
url = config_obj.ChatEndpoint

# Set the headers
auth_token = config_obj.AIPROXY_TOKEN  # Retrieve the token from environment variable



def chat_with_aiproxy(user_input):
    
    print("here")
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config_obj.AIPROXY_TOKEN}"
    }

    # Define the payloadcle
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": user_input}]
    }

    # Make the POST request
    data["functions"] = functions
    
    
    response = requests.post(url, json=data, headers=headers)
    
    
    response_data = response.json()

    # Extract model's response
    # Check if 'choices' key is present in the response data
    
    if "choices" not in response_data:
        raise ValueError("Invalid response from AIProxy API: 'choices' key not found")

    response_message = response_data["choices"][0]["message"]

    # Check if there is a function call
    
    if response_message.get("function_call"):
        
        function_name = response_message["function_call"]["name"]
        
        function_args = json.loads(response_message["function_call"]["arguments"])

        # Call the appropriate function
        
        if function_name == "A1":
            result = run_datagen(**function_args)
        
        elif function_name == "run_python_file":
            result = run_python_file(**function_args)
        
        else:
            result = "Unknown function."

        return result

    return response_message["content"]  # If no function call, return normal AI response


def run_datagen(email):
    
    try:
        
        result = subprocess.run(["python3", "datagen.py", email], capture_output=True, text=True)
        
        if result.returncode == 0:
        
            return json.dumps({"message": "Datagen files created Successfully"})
        
        else:
        
            return json.dumps({"error": result.stderr})
        
    except Exception as e:
        
        return json.dumps({"error": str(e)})


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


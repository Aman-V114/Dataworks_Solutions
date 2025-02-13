import subprocess
import json
import requests
import pydantic
import os
from config import Config_API
import tempfile
import aiohttp
import asyncio
import aiofiles


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
                "email": {"type": "string", "description": "The email to be passed to the script."}
            },
            "required": ["email"],
        },
    },
]


config_obj = Config_API()

print(config_obj.ChatEndpoint)

# Set the API endpoint
url = config_obj.ChatEndpoint

# Set the headers
auth_token = config_obj.AIPROXY_TOKEN  # Retrieve the token from environment variable


async def chat_with_aiproxy(user_input):
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

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            response_data = await response.json()

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
            result = await run_datagen("uv", "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", **function_args)
        else:
            result = "Unknown function."

        return result

    return response_message["content"]  # If no function call, return normal AI response


async def run_datagen(package_name, repo_link, email):
    """
    Checks if the specified package is installed.
    If not, installs it, then downloads the Python file from repo_link 
    and runs it with the email as parameter.
    """
    # Check if package is installed (using pip show)
    check_result = await asyncio.create_subprocess_exec("pip", "show", package_name, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await check_result.communicate()

    if check_result.returncode != 0:
        # Package not found, install it
        install_result = await asyncio.create_subprocess_exec("pip", "install", package_name, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await install_result.communicate()
        # Log installation outcome; do not return early.
        print(f"Installed {package_name}: {stdout or stderr}")
    else:
        # Optional: Log installed package version information.
        for line in stdout.decode().splitlines():
            if line.startswith("Version:"):
                print(f"{package_name} version {line.split('Version:')[1].strip()} is installed")
                break

    # Download the file from the provided repo link
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(repo_link) as response:
                response.raise_for_status()
                content = await response.read()
    except Exception as e:
        return json.dumps({"error": f"Failed to download file: {str(e)}"})

    # Write the downloaded content to a temporary Python file
    async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        await temp_file.write(content)
        temp_file_path = temp_file.name

    # Execute the downloaded file with the provided email parameter
    run_result = await asyncio.create_subprocess_exec("python3", temp_file_path, email, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await run_result.communicate()
    if run_result.returncode == 0:
        return json.dumps({"message": "Script executed successfully", "output": stdout.decode()})
    else:
        return json.dumps({"error": stderr.decode()})


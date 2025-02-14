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
    {
        "name": "A2",
        "description": "Formats the provided document using prettier@3.4.2",
        "parameters": {
            "type": "object",
            "properties": {
                "document_name": {"type": "string", "description": "The Name of the document to be formatted."}
            },
            "required": ["document_name"],
        }
    },
    {
        "name": "A3",
        "description": "Counts the number of wednesdays in the text document which has one date per line and stores the count in a file named dates-wednesdays.txt",
        "parameters": {
            "type": "object",
            "properties": {
                "document_name": {"type": "string", "description": "The Name of the document to be formatted."}
            },
            "required": ["document_name"],
        }
    },
    {
        "name": "A4",
        "description": "Takes a json file and sorts the list of json objects on first_name and last_name parameter",
        "parameters": {
            "type": "object",
            "properties": {
                "document_name": {"type": "string", "description": "The Name of the document to be formatted."}
            },
            "required": ["document_name"],
        }
    }
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
            try:
                response_data = await response.json()
            except Exception as e:
                html_content = await response.text()
                print("HTML response:", html_content)
                raise e  # or handle the error as needed

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
        elif function_name=="A2":
            result = await format_document(**function_args)
        elif function_name=="A3":
            result = await count_wednesdays(**function_args)
        else:
            result = "Unknown function."

        return result

    return response_message["content"]  # If no function call, return normal AI response

#done
#need to adjust for user input
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
    run_result = await asyncio.create_subprocess_exec("uv", "run", temp_file_path, email, "--root", "./data", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await run_result.communicate()
    
    if run_result.returncode == 0:
        return json.dumps({"message": "Script executed successfully", "output": stdout.decode()})
    else:
        return json.dumps({"error": stderr.decode()})
#done
#need to adjust for user input
async def format_document(document_name):
    # Construct the file path
    file_path = os.path.join("./data", document_name)
    print(file_path)
    print(document_name)
    # Read the document content from the data directory
    try:
        
        async with aiofiles.open(file_path, 'r') as file:
            document_content = await file.read()

    except FileNotFoundError:
        
        return json.dumps({"error": "File not found"})
    
    except Exception as e:
        
        return json.dumps({"error": str(e)})

    # Write the document content to a temporary file
    async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_file:
        
        await temp_file.write(document_content.encode())
        temp_file_path = temp_file.name

    # Run prettier to format the document
    run_result = await asyncio.create_subprocess_exec("npx", "prettier@3.4.2", "--write", temp_file_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await run_result.communicate()

    # Check if the command was successful

    if run_result.returncode != 0:
        return json.dumps({"error": stderr.decode()})


    # Read the formatted content from the temporary file
    async with aiofiles.open(temp_file_path, mode='r') as temp_file:
        formatted_content = await temp_file.read()


    # Write the formatted content back to the original document
    async with aiofiles.open(file_path, mode='w') as file:
        await file.write(formatted_content)

    return json.dumps({"message": "Document formatted successfully", "formatted_document": formatted_content})

#done
#need to adjust for user input
async def count_wednesdays(document_name):

    # Construct the file path
    file_path = os.path.join("./data", document_name)

    # Read the document content from the data directory
    try:
    
        async with aiofiles.open(file_path, 'r') as file:
            document_content = await file.read()
    
    except FileNotFoundError:
    
        return json.dumps({"error": "File not found"})
    
    except Exception as e:
    
        return json.dumps({"error": str(e)})

    # Split the document content into lines
    lines = document_content.splitlines()

    # Count the number of Wednesdays in the document
    from dateutil import parser
    from datetime import datetime

    wednesday_count = 0

    for line in lines:
        try:
            date = parser.parse(line.strip(), fuzzy=True)
            if date.weekday() == 2:  # Monday is 0, so Wednesday is 2
                wednesday_count += 1
        except (ValueError, OverflowError):
            continue

    # Write the count to a file
    output_file_path = os.path.join("./data", "dates-wednesdays.txt")
    async with aiofiles.open(output_file_path, mode='w') as output_file:
        await output_file.write(str(wednesday_count))

    return json.dumps({"message": "Counted Wednesdays successfully", "wednesday_count": wednesday_count})

    async def sort_contacts(filename):
        # Construct the file path
        file_path = os.path.join("./data", filename)

        # Read the JSON content from the file
        try:
            async with aiofiles.open(file_path, 'r') as file:
                content = await file.read()
                contacts = json.loads(content)
        except FileNotFoundError:
            return json.dumps({"error": "File not found"})
        except Exception as e:
            return json.dumps({"error": str(e)})

        # Sort the contacts first by last_name, then by first_name
        sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

        # Write the sorted contacts to a new file
        output_file_path = os.path.join("./data", "contacts-sorted.json")
        async with aiofiles.open(output_file_path, mode='w') as output_file:
            await output_file.write(json.dumps(sorted_contacts, indent=4))

        return json.dumps({"message": "Contacts sorted successfully", "output_file": "contacts-sorted.json"})
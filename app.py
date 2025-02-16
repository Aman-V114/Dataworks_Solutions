# app.py
# /// script
# dependencies = [
#   "requests",
#   "fastapi",
#   "uvicorn",
#   "python-dateutil",
#   "pandas",
#   "db-sqlite3",
#   "scipy",
#   "pybase64",
#   "python-dotenv",
#   "httpx",
#   "markdown",
#   "duckdb"
# ]
# ///

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tasksA import *
from tasksB import *
import requests
from dotenv import load_dotenv
import os
import re
import httpx
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app = FastAPI()
load_dotenv()


openai_api_chat  = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions" # for testing
openai_api_key = os.getenv("AIPROXY_TOKEN")

headers = {
    "Authorization": f"Bearer {openai_api_key}",
    "Content-Type": "application/json",
}

function_definitions_llm = [
    {
        "name": "A1",
        "description": "Run a Python script from a given URL, passing an email as the argument.",
        "parameters": {
            "type": "object",
            "properties": {
                # "filename": {"type": "string", "pattern": r"https?://.*\.py"},
                # "targetfile": {"type": "string", "pattern": r".*/(.*\.py)"},
                "email": {"type": "string", "pattern": r"[\w\.-]+@[\w\.-]+\.\w+"}
            },
            "required": ["filename", "targetfile", "email"]
        }
    },
    {
        "name": "A2",
        "description": "Format a markdown file using Prettier.",
        "parameters": {
            "type": "object",
            "properties": {
                
                "filename": {"type": "string", "pattern": r".*/(.*\.md)"}
            },
            "required": [ "filename"]
        }
    },
    {
        "name": "A3",
        "description": "Count the number of occurrences of a specific weekday in a date file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "pattern": r"/data/.*dates.*\.txt"},
                "targetfile": {"type": "string", "pattern": r"/data/.*/(.*\.txt)"},
                "weekday": {"type": "integer", "pattern": r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"}
            },
            "required": ["filename", "targetfile", "weekday"]
        }
    },
    {
        "name": "A4",
        "description": "Sort a JSON contacts file and save the sorted version to a target file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                },
                "targetfile": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                }
            },
            "required": ["filename", "targetfile"]
        }
    },
    {
        "name": "A5",
        "description": "Retrieve the most recent log files from a directory and save their content to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "log_dir_path": {
                    "type": "string",
                    "pattern": r".*/logs",
                    "default": "/data/logs"
                },
                "output_file_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/logs-recent.txt"
                },
                "num_files": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 10
                }
            },
            "required": ["log_dir_path", "output_file_path", "num_files"]
        }
    },
    {
        "name": "A6",
        "description": "Generate an index of documents from a directory and save it as a JSON file.",
        "parameters": {
            "type": "object",
            "properties": {
                "doc_dir_path": {
                    "type": "string",
                    "pattern": r".*/docs",
                    "default": "/data/docs"
                },
                "output_file_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                    "default": "/data/docs/index.json"
                }
            },
            "required": ["doc_dir_path", "output_file_path"]
        }
    },
    {
        "name": "A7",
        "description": "Extract the sender's email address from a text file and save it to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/email.txt"
                },
                "output_file": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/email-sender.txt"
                }
            },
            "required": ["filename", "output_file"]
        }
    },
    {
        "name": "A8",
        "description":"Extract credit card number from an image file and write the credit card number to a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/credit-card.txt"
                },
                "image_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.png)",
                    "default": "/data/credit_card.png"
                }
            },
            "required": ["filename", "image_path"]
        }
    },
    {
        "name": "A9",
        "description": "Find similar comments from a text file and save them to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/comments.txt"
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/comments-similar.txt"
                }
            },
            "required": ["filename", "output_filename"]
        }
    },
    {
        "name": "A10",
        "description": "Identify high-value (gold) ticket sales from a database and save them to a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.db)",
                    "default": "/data/ticket-sales.db"
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/ticket-sales-gold.txt"
                },
                "query": {
                    "type": "string",
                    "pattern": "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"
                }
            },
            "required": ["filename", "output_filename", "query"]
        }
    },
    {
        "name": "B12",
                "description": "Check if filepath starts with /data and check if the user is trying to delete anything, if there are any commands which try to move or removea any files ,run this function. run this if anyone access files outside the permitted /data directory",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "pattern": r"^/data/.*",
                    # "description": "Filepath must start with /data to ensure secure access."
                }
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "B3",
        "description": "Download content from a URL and save it to the specified path.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "pattern": r"https?://.*",
                    "description": "URL to download content from."
                },
                "save_path": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path to save the downloaded content."
                }
            },
            "required": ["url", "save_path"]
        }
    },
    {
        "name": "B5",
        "description": "Execute a SQL query on a specified database file and save the result to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.db)",
                    "description": "Path to the SQLite database file."
                },
                "query": {
                    "type": "string",
                    "description": "SQL query to be executed on the database."
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "description": "Path to the file where the query result will be saved."
                }
            },
            "required": ["db_path", "query", "output_filename"]
        }
    },
    {
        "name": "B6",
        "description": "Fetch content from a URL and save it to the specified output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "pattern": r"https?://.*",
                    "description": "URL to fetch content from."
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path to the file where the content will be saved."
                }
            },
            "required": ["url", "output_filename"]
        }
    },
    {
        "name": "B7",
        "description": "Process an image by optionally resizing it and saving the result to an output path.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.(jpg|jpeg|png|gif|bmp))",
                    "description": "Path to the input image file."
                },
                "output_path": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path to save the processed image."
                },
                "resize": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                        "minimum": 1
                    },
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Optional. Resize dimensions as [width, height]."
                }
            },
            "required": ["image_path", "output_path"]
        }
    },
    {
        "name": "B9",
        "description": "Convert a Markdown file to another format and save the result to the specified output path.",
        "parameters": {
            "type": "object",
            "properties": {
                "md_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.md)",
                    "description": "Path to the Markdown file to be converted."
                },
                "output_path": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path where the converted file will be saved."
                }
            },
            "required": ["md_path", "output_path"]
        }
    }

]

def get_completions(prompt: str):
    
    with httpx.Client(timeout=20) as client:
        response = client.post(
            f"{openai_api_chat}",
            headers=headers,
            json=
                {
                    "model": "gpt-4o-mini",
                    "messages": [
                                    {"role": "system", "content": "You are a function classifier that extracts structured parameters from queries."},
                                    {"role": "user", "content": prompt}
                                ],
                    "tools": [
                                {
                                    "type": "function",
                                    "function": function
                                } for function in function_definitions_llm
                            ],
                    "tool_choice": "auto"
                },
        )
    # return response.json()
    print(response.json()["choices"][0]["message"]["tool_calls"][0]["function"])
    return response.json()["choices"][0]["message"]["tool_calls"][0]["function"]


# Placeholder for task execution
@app.post("/run")
async def run_task(task: str):
    try:
        # Placeholder logic for executing tasks
        # Replace with actual logic to parse task and execute steps
        # Example: Execute task and return success or error based on result
        # llm_response = function_calling(tast), function_name = A1
        response = get_completions(task)
        print(response)
        task_code = response['name']
        arguments = response['arguments']

        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        
        if "A1" == task_code:
            A1(filename=arguments['filename'], targetfile=arguments['targetfile'], email=arguments['email'])
        if "A2" == task_code:
            A2(filename=arguments['filename'])
        if "A3" == task_code:
            A3(filename=arguments['filename'], targetfile=arguments['targetfile'], weekday=arguments['weekday'])
        if "A4" == task_code:
            A4(filename=arguments['filename'], targetfile=arguments['targetfile'])
        if "A5" == task_code:
            A5(log_dir_path=arguments['log_dir_path'], output_file_path=arguments['output_file_path'], num_files=arguments['num_files'])
        if "A6" == task_code:
            A6(doc_dir_path=arguments['doc_dir_path'], output_file_path=arguments['output_file_path'])
        if "A7" == task_code:
            A7(filename=arguments['filename'], output_file=arguments['output_file'])
        if "A8" == task_code:
            A8(filename=arguments['filename'], image_path=arguments['image_path'])
        if "A9" == task_code:
            A9(filename=arguments['filename'], output_filename=arguments['output_filename'])
        if "A10" == task_code:
            A10(filename=arguments['filename'], output_filename=arguments['output_filename'], query=arguments['query'])

        
        if "B12" == task_code:
            B12(filepath=arguments['filepath'])
        if "B4" == task_code:
            B4(url=arguments['url'], save_path=arguments['save_path'])
        if "B3" == task_code:
            B3(url=arguments['url'], save_path=arguments['save_path'])
        if "B5" == task_code:
            B5(db_path=arguments['db_path'], query=arguments['query'], output_filename=arguments['output_filename'])
        if "B6" == task_code:
            B6(url=arguments['url'], output_filename=arguments['output_filename'])
        if "B7" == task_code:
            B7(image_path=arguments['image_path'], output_path=arguments['output_path'], resize=arguments.get('resize'))
        if "B9" == task_code:
            B9(md_path=arguments['md_path'], output_path=arguments['output_path'])

           
        return {"message": f"{task_code} Task '{task}' executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Placeholder for file reading

@app.get("/read", response_class=PlainTextResponse)
async def read_file(path: str = Query(..., description="File path to read")):
    
    try:
        BASE_DIR = os.path.join(os.getcwd(), "data")
        abs_path = os.path.abspath(os.path.join(BASE_DIR, path.lstrip('/')))
        
        if not abs_path.startswith(os.path.abspath(BASE_DIR)):
            raise PermissionError(f"Access denied to path: {path}")
        
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(abs_path, "r") as file:
            return file.read()
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
import sqlite3
import subprocess
from dateutil.parser import parse
from fastapi import HTTPException
from datetime import datetime
import json
from pathlib import Path
import os
import requests
from scipy.spatial.distance import cosine
from dotenv import load_dotenv
import pytesseract
from PIL import Image
from PIL import ImageFilter, ImageEnhance

load_dotenv()

AIPROXY_TOKEN = os.getenv('AIPROXY_TOKEN')


def A1(email="23f1002942@ds.study.iitm.ac.in"):
    try:
        data_dir = os.path.abspath("./data")
        process = subprocess.Popen(
            ["uv", "run", "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", email, "--root", data_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error: {stderr}")
        return stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error: {e.stderr}")


def A2(filename="./data/format.md"):
    try:
        filename = os.path.abspath(filename)
        print(f"🔍 Validating file: {filename}")
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
        command = ["npx", "prettier", "--write", filename]
        print(f"🚀 Executing: {' '.join(command)}")
        process = subprocess.run(
        ["npx", "prettier", "--write", filename],
        capture_output=True,
        text=True,
        check=True,
        # Ensure npx is picked up from the PATH on Windows
        shell=True)
                
        print("✅ Formatting successful!")
        print(f"📋 Output:\n{process.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Formatting failed (Code {e.returncode})")
        print(f"🔧 Error Details:\n{e.stderr}")
    except Exception as e:
        print(f"🚨 Unexpected error: {str(e)}")


def A3(weekday: int, filename='data/dates.txt', targetfile='data/dates-wednesdays.txt'):
    input_file = '.' + os.path.abspath(filename)
    output_file = '.' + os.path.abspath(targetfile)
    weekday_count = 0
    with open(input_file, 'r') as file:
        weekday_count = sum(1 for date in file if parse(date).weekday() == int(weekday) - 1)
    with open(output_file, 'w') as file:
        file.write(str(weekday_count))


def A4(filename="/data/contacts.json", targetfile="/data/contacts-sorted.json"):
    filename = '.' + os.path.abspath(filename)
    targetfile = '.' + os.path.abspath(targetfile)
    with open(filename, 'r') as file:
        contacts = json.load(file)
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
    with open(targetfile, 'w') as file:
        json.dump(sorted_contacts, file, indent=4)


def A5(log_dir_path='/data/logs', output_file_path='/data/logs-recent.txt', num_files=10):
    log_dir = Path('.' + os.path.abspath(log_dir_path))
    output_file = Path('.' + os.path.abspath(output_file_path))
    log_files = sorted(log_dir.glob('*.log'), key=lambda p: p.stat().st_mtime, reverse=True)[:num_files]
    with output_file.open('w') as f_out:
        for log_file in log_files:
            with log_file.open('r') as f_in:
                first_line = f_in.readline().strip()
                f_out.write(f"{first_line}\n")


def A6(doc_dir_path='/data/docs', output_file_path='/data/docs/index.json'):
    docs_dir = Path('.' + os.path.abspath(doc_dir_path))
    output_file = Path('.' + os.path.abspath(output_file_path))
    index_data = {}
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('# '):
                            title = line[2:].strip()
                            relative_path = os.path.relpath(file_path, docs_dir).replace('\\', '/')
                            index_data[relative_path] = title
                            break
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=4)


def A7(filename='/data/email.txt', output_file='/data/email-sender.txt'):
    filename = '.' + os.path.abspath(filename)
    output_file = '.' + os.path.abspath(output_file)
    with open(filename, 'r') as file:
        email_content = file.readlines()
    sender_email = "sujay@gmail.com"
    for line in email_content:
        if "From" == line[:4]:
            sender_email = (line.strip().split(" ")[-1]).replace("<", "").replace(">", "")
            break
    with open(output_file, 'w') as file:
        file.write(sender_email)


import base64


def png_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_string


def A8(filename='/data/credit_card.txt', image_path='/data/credit_card.png'):
    
    filename = '.' + os.path.abspath(filename)
    image_path = '.' + os.path.abspath(image_path)
    
    print(filename,image_path)
    
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "There is a 16 digit number in this image, with space after every 4 digit, only extract the those digits without spaces and return just the number without any other characters, i need exact 16 digits."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{png_to_base64(image_path)}"
                        }
                    }
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
                             headers=headers, data=json.dumps(body))
    result = response.json()
    card_number = result['choices'][0]['message']['content'].replace(" ", "")
    with open(filename, 'w') as file:
        file.write(card_number)


def get_embeddings(texts):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": texts
    }
    response = requests.post("https://aiproxy.sanand.workers.dev/openai/v1/embeddings",
                             headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print(f"🔴 Error fetching embeddings: {response.text}")
        return None
    return [item["embedding"] for item in response.json().get("data", [])]


async def A9(filename='/data/comments.txt', output_filename='/data/comments-similar.txt'):
    filename = os.path.abspath(filename)
    output_filename = os.path.abspath(output_filename)
    print(f"📂 Reading from: {filename}")
    print(f"📂 Writing to: {output_filename}")
    try:
        with open(filename, 'r') as f:
            comments = [line.strip() for line in f.readlines()]
        print(f"✅ Loaded {len(comments)} comments")
    except FileNotFoundError:
        print(f"❌ Error: File {filename} not found!")
        return
    if not comments:
        print("⚠️ No comments found in the file!")
        return
    batch_size = 2
    embeddings = []
    for i in range(0, len(comments), batch_size):
        batch = comments[i:i + batch_size]
        batch_embeddings = get_embeddings(batch)
        if batch_embeddings is None:
            print("❌ Error fetching embeddings! Aborting.")
            return
        embeddings.extend(batch_embeddings)
    min_distance = float('inf')
    most_similar = (None, None)
    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            distance = cosine(embeddings[i], embeddings[j])
            if distance < min_distance:
                min_distance = distance
                most_similar = (comments[i], comments[j])
    if most_similar == (None, None):
        print("⚠️ No similar comments found!")
        return
    print(f"✅ Most similar comments found: {most_similar}")
    try:
        with open(output_filename, 'w') as f:
            f.write(most_similar[0] + '\n')
            f.write(most_similar[1] + '\n')
        print(f"✅ Successfully written to: {output_filename}")
        if os.path.exists(output_filename):
            print(f"🎉 File successfully created: {output_filename}")
        else:
            print("🚨 File was not created for some reason!")
    except Exception as e:
        print(f"❌ Error writing file: {e}")


def A10(filename='data/ticket-sales.db', output_filename='data/ticket-sales-gold.txt', query="SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"):
    filename = '.' + os.path.abspath(filename)
    output_filename = '.' + os.path.abspath(output_filename)
    conn = sqlite3.connect(filename)
    print("Connected to SQLite")
    cursor = conn.cursor()
    cursor.execute(query)
    total_sales = cursor.fetchone()[0]
    total_sales = total_sales if total_sales else 0
    with open(output_filename, 'w') as file:
        file.write(str(total_sales))
    conn.close()

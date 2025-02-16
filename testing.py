import os
import shutil
import requests
import sqlite3
import duckdb
import markdown
from PIL import Image
import csv
import json
from bs4 import BeautifulSoup
import subprocess
from pydub import AudioSegment
import speech_recognition as sr

BASE_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(BASE_DIR, exist_ok=True)


# Security Functions
def ensure_within_data_dir(path: str):
    """
    Ensures that all file operations are restricted to the `data` directory.
    """
    abs_path = os.path.abspath(path)
    if not abs_path.startswith(os.path.abspath(BASE_DIR)):
        raise PermissionError(f"Access denied to path: {path}")

def ensure_no_deletion():
    """
    Override any deletion attempt (placeholder function).
    """
    raise PermissionError("Deletion operations are not allowed.")

def transcribe_audio():
    """ B8: Transcribe audio using SpeechRecognition and ffmpeg. """
    audio_path = os.path.join(BASE_DIR, input("Enter the audio file name: "))
    output_path = os.path.join(BASE_DIR, input("Enter the output file name for transcription: "))
    ensure_within_data_dir(audio_path)
    ensure_within_data_dir(output_path)

    # Convert audio to WAV format using pydub
    audio = AudioSegment.from_file(audio_path)
    wav_path = os.path.splitext(audio_path)[0] + ".wav"
    audio.export(wav_path, format="wav")

    # Transcribe audio using SpeechRecognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            text = f"Could not request results from Google Speech Recognition service; {e}"

    # Save transcription to output file
    with open(output_path, 'w') as f:
        f.write(text)
    print(f"Audio transcription saved to {output_path}")




def convert_markdown_to_html():
    """ B9: Convert Markdown to HTML. """
    md_path = os.path.join(BASE_DIR, input("Enter the Markdown file name: "))
    output_path = os.path.join(BASE_DIR, input("Enter the output file name for HTML: "))
    ensure_within_data_dir(md_path)
    ensure_within_data_dir(output_path)
    try:
        with open(md_path, 'r') as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=[
            'fenced_code', 'tables', 'footnotes', 'abbr', 'attr_list',
            'def_list', 'md_in_html', 'admonition', 'codehilite',
            'legacy_attrs', 'legacy_em', 'meta', 'nl2br', 'sane_lists',
            'smarty', 'toc', 'wikilinks'
        ])
        with open(output_path, 'w') as f:
            f.write(html_content)
        print(f"Markdown converted to HTML and saved to {output_path}")
    except FileNotFoundError:
        print(f"File not found: {md_path}")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# convert_markdown_to_html()
    
import os
import csv
import json
import random
import re
from datetime import datetime

BASE_DIR = "./data"  # Adjust as needed

def ensure_within_data_dir(path):
    if not path.startswith(BASE_DIR):
        raise ValueError("File access outside the data directory is not allowed.")


def filter_csv_and_return_json():
    """Enhanced CSV filter function supporting multiple filtering methods."""
    csv_path = os.path.join(BASE_DIR, input("Enter the CSV file name: "))
    ensure_within_data_dir(csv_path)
    output_path = os.path.join(BASE_DIR, input("Enter the output file name for filtered JSON: "))
    ensure_within_data_dir(output_path)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # 1. Column-Based Filtering
    selected_columns = input("Enter column names to keep (comma-separated, leave blank for all): ").split(',')
    if selected_columns and selected_columns[0]:
        data = [{k: v for k, v in row.items() if k in selected_columns} for row in data]
    
    # 2. Row-Based Filtering
    filter_column = input("Enter the column name to filter by (leave blank for none): ")
    if filter_column:
        filter_value = input("Enter the value to filter for: ")
        data = [row for row in data if row.get(filter_column) == filter_value]
    
    # 3. Text-Based Filtering
    text_column = input("Enter the column to apply text-based filtering (leave blank for none): ")
    if text_column:
        pattern = input("Enter regex pattern to match: ")
        data = [row for row in data if re.search(pattern, row.get(text_column, ''), re.IGNORECASE)]
    
    # 4. Numeric & Date-Based Filtering
    numeric_column = input("Enter a column to filter by numeric range (leave blank for none): ")
    if numeric_column:
        min_val, max_val = map(float, input("Enter min and max values separated by a comma: ").split(','))
        data = [row for row in data if min_val <= float(row.get(numeric_column, 0)) <= max_val]
    
    date_column = input("Enter a column to filter by date range (leave blank for none): ")
    if date_column:
        date_format = input("Enter date format (e.g., %Y-%m-%d): ")
        start_date, end_date = input("Enter start and end dates separated by a comma: ").split(',')
        start_date, end_date = datetime.strptime(start_date.strip(), date_format), datetime.strptime(end_date.strip(), date_format)
        data = [row for row in data if start_date <= datetime.strptime(row.get(date_column, ''), date_format) <= end_date]
    
    # 5. Advanced Filters
    deduplicate = input("Remove duplicate rows? (yes/no): ").strip().lower()
    if deduplicate == "yes":
        seen = set()
        filtered_data = []
        for row in data:
            row_tuple = tuple(row.items())
            if row_tuple not in seen:
                seen.add(row_tuple)
                filtered_data.append(row)
        data = filtered_data
    
    # 6. Format-Based Filters
    trim_whitespace = input("Trim whitespace in all columns? (yes/no): ").strip().lower()
    if trim_whitespace == "yes":
        data = [{k: v.strip() for k, v in row.items()} for row in data]
    
    # 7. Row Sampling & Limits
    row_limit = input("Enter max number of rows to return (leave blank for all): ")
    if row_limit:
        data = data[:int(row_limit)]
    random_sample = input("Return a random sample of rows? (yes/no): ").strip().lower()
    if random_sample == "yes":
        sample_size = int(input("Enter sample size: "))
        data = random.sample(data, min(sample_size, len(data)))
    
    # 8. File Metadata Filters (not applicable to row-level filtering but could be used to exclude large files, etc.)
    
    # Save filtered data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Filtered data saved to {output_path}")

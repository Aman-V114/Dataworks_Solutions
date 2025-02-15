
# DataWorks Solutions

DataWorks Solutions is a comprehensive automation agent designed to perform various tasks using LLM-based automation. This project includes functionalities such as data fetching, file processing, image processing, web scraping, and more.

## Features

- **Security Checks**: Ensure file access is restricted to specific directories.
- **Data Fetching**: Fetch data from APIs and save it locally.
- **Git Operations**: Clone repositories and make commits.
- **SQL Query Execution**: Run SQL queries on SQLite and DuckDB databases.
- **Web Scraping**: Scrape web content and save it locally.
- **Image Processing**: Resize and save images.
- **Audio Transcription**: Transcribe audio files using OpenAI's Whisper model.
- **Markdown to HTML Conversion**: Convert Markdown files to HTML.
- **CSV Filtering**: Filter CSV files based on specific criteria.

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

### Running the FastAPI Server

To start the FastAPI server, run:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Run Task

```http
POST /run
```

Execute a specified task.

**Parameters:**

- `task` (str): Description of the task to be executed.

**Example:**

```bash
curl -X POST "http://localhost:8000/run?task=Run%20a%20Python%20script"
```

#### Read File

```http
GET /read
```

Read the content of a specified file.

**Parameters:**

- `path` (str): Path to the file to be read.

**Example:**

```bash
curl -X GET "http://localhost:8000/read?path=/data/example.txt"
```

## Functions

### Task Functions (tasksA.py)

- **A1**: Run a Python script from a given URL, passing an email as the argument.
- **A2**: Format a markdown file using a specified version of Prettier.
- **A3**: Count the number of occurrences of a specific weekday in a date file.
- **A4**: Sort a JSON contacts file and save the sorted version to a target file.
- **A5**: Retrieve the most recent log files from a directory and save their content to an output file.
- **A6**: Generate an index of documents from a directory and save it as a JSON file.
- **A7**: Extract the sender's email address from a text file and save it to an output file.
- **A8**: Generate an image representation of credit card details from a text file.
- **A9**: Find similar comments from a text file and save them to an output file.
- **A10**: Identify high-value (gold) ticket sales from a database and save them to a text file.

### Task Functions (tasksB.py)

- **B12**: Check if filepath starts with /data.
- **B3**: Download content from a URL and save it to the specified path.
- **B5**: Execute a SQL query on a specified database file and save the result to an output file.
- **B6**: Fetch content from a URL and save it to the specified output file.
- **B7**: Process an image by optionally resizing it and saving the result to an output path.
- **B9**: Convert a Markdown file to another format and save the result to the specified output path.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or inquiries, please contact Aman Dhol at [your-email@example.com].


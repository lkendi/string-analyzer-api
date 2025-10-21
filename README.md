# String Analyzer API

A simple FastAPI service that analyzes strings and returns their properties, such as length, palindrome status, unique characters, word count, SHA256 hash, and character frequency map. It also provides filtering capabilities for retrieving analyzed strings (including natural language filtering)

## Prerequisites

- Python 3.8+
- pip

## Setup Instructions

1.  **Clone the Repository**
    If you haven't already, clone the repository to your local machine.

    ```bash
    git clone string-analyzer-api
    cd string-analyzer-api
    ```

2.  **Create and Activate Virtual Environment (Optional)**
    A virtual environment makes it easier to manage project-specific dependencies.

    ```bash
    python3 -m venv venv
    ```

    To activate the environment on Linux/MacOS use:

    ```bash
    source venv/bin/activate
    ```

    On Windows, use:

    ```bash
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**
    Install all required packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

With the dependencies installed, you can run the application using:

```bash
fastapi dev main.py
```

The API will be running and accessible at `http://127.0.0.1:8000`.


## API Documentation

You can access the documentation on http://127.0.0.1:8000/docs.

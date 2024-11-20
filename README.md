# Formula 1 Türkiye

## Description

## Requirements

- Python 3.10 or higher

## Setup Instructions

Follow these steps to set up the project on your local machine.

### 1. Create a Virtual Environment

Create a virtual environment in the root of your project folder:

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
**On Windows**:

```bash
venv\Scripts\activate
```

**On Linux**:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages using pip. Run the following command:

```bash
pip install -r requirements/development.txt
```

### 4. Set Up the Database

Run the following commands to set up the database:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Follow the prompts to create a superuser account.

### 5. Run the Development Server

Now you can run the development server:

```bash
python manage.py runserver
```

The server will start, and you can access it by navigating to `http://127.0.0.1:8888/` in your web browser.


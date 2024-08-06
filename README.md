# Good Reads Scraper with Django

A web application that scrapes data from Goodreads based on keywords. The project is built using Django, Celery for asynchronous task processing, and PostgreSQL for the database.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Project on Windows 10](#running-the-project-on-windows-10)
- [Usage](#usage)
- [License](#license)

## Features

- Scrape books and groups from Goodreads using specified keywords.
- Asynchronous task handling with Celery.
- Persistent task status tracking in the database.
- Admin interface for managing keywords and scraping results.
- Task scheduling with periodic scraping using Celery Beat.

## Tech Stack

- **Backend Framework:** Django 4.2
- **Task Queue:** Celery 5.4.0
- **Database:** PostgreSQL
- **Scraping:** BeautifulSoup4
- **Message Broker:** RabbitMQ (default)
- **Other:** Django Celery Beat, Django Celery Results

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- RabbitMQ
- Virtualenv (recommended)

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/CodeSymphonyy/goodreads-scraper.git
    cd good_reads_scraper_with_django
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On MacOS/Linux
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Settings:**

    - Copy `sample_settings.py` to `local_settings.py`:

        ```bash
        cp good_reads_scraper_with_django/sample_settings.py good_reads_scraper_with_django/local_settings.py
        ```

    - Open `local_settings.py` and update the following:

        - Set your `SECRET_KEY`.
        - Configure `ALLOWED_HOSTS` as needed.
        - Set `DEBUG = False` for production environments.

5. **Set up the PostgreSQL database:**

    - Create a new PostgreSQL database and user with the necessary permissions.
    - Update the `DATABASES` settings in `good_reads_scraper_with_django/settings.py` or `local_settings.py` with your database credentials.

6. **Apply the migrations:**

    ```bash
    python manage.py migrate
    ```

7. **Create a superuser (admin account):**

    ```bash
    python manage.py createsuperuser
    ```

8. **Start the RabbitMQ server:**

    Ensure RabbitMQ is running on your machine. If not installed, you can find installation instructions [here](https://www.rabbitmq.com/download.html).

9. **Run the Celery worker and Celery Beat:**

    In separate command prompt windows, start the Celery worker and Celery Beat:

    ```bash
    celery -A good_reads_scraper_with_django worker --loglevel=info
    celery -A good_reads_scraper_with_django beat --loglevel=info
    ```

10. **Start the Django development server:**

    ```bash
    python manage.py runserver
    ```

11. **Access the application:**

    Visit `http://127.0.0.1:8000/` in your browser.

## Running the Project on Windows 10

### Prerequisites

- **Ensure Python is installed and added to your PATH.**
- **PostgreSQL should be installed and running on your system.**
- **RabbitMQ should be installed and running.**
  - If RabbitMQ is not installed, you can download and install it from [here](https://www.rabbitmq.com/install-windows.html).

### Steps

1. **Open Command Prompt or PowerShell.**

2. **Navigate to your project directory:**

    ```bash
    cd path\to\your\project\good_reads_scraper_with_django
    ```

3. **Activate the virtual environment:**

    ```bash
    venv\Scripts\activate
    ```

4. **Run the Celery worker:**

    ```bash
    celery -A good_reads_scraper_with_django worker --loglevel=info
    ```

5. **Run the Celery Beat scheduler:**

    Open another Command Prompt or PowerShell window and navigate to your project directory again, then run:

    ```bash
    celery -A good_reads_scraper_with_django beat --loglevel=info
    ```

6. **Run the Django development server:**

    In a new Command Prompt or PowerShell window, run:

    ```bash
    python manage.py runserver
    ```

7. **Access the application:**

    Open your browser and go to `http://127.0.0.1:8000/`.

## Usage

- **Admin Interface:** Access the admin interface at `/admin/` to manage keywords, authors, books, groups, and scraping tasks.
- **Scraping:** Use the `/search_by_keyword` endpoint to start a new scrape by entering keywords and selecting the type (books or groups).
- **Monitoring Tasks:** Monitor Celery tasks using Flower (optional) by running `celery -A good_reads_scraper_with_django flower`.

## License

This software is proprietary and protected under copyright laws. CodeSymphonyy retains all rights to the software, and it is available for use under the following conditions:

- The software may be used on up to three devices owned by the user.
- The user is not permitted to modify, distribute, or sublicense the software.
- This license does not grant any rights to the source code or to make derivative works.

For the full license terms, please refer to the License Agreement included with the software or contact CodeSymphonyy for more details.
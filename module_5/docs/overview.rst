Overview & Setup
================

This project demonstrates a three-tiered architecture for scraping, cleaning, 
loading, and querying graduate admissions data, with a Flask web UI.

Setup
-----

1. **Install dependencies**::

      pip install -r requirements.txt

2. **Set required environment variable**::

      export DATABASE_URL="postgresql://postgres@localhost:5432/postgres"

   Replace values with your credentials if different.

3. **From the root directory, run the app with**::

      python -m module_4.src.app.app

4. **Change directory to module_4/src. Run tests with**::

      pytest


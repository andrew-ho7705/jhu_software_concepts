Architecture
============

This project is structured into three primary layers:

Web Layer
---------

- Implemented in ``module_4/src/app/`` (Flask app).
- Provides routes for displaying and updating analysis results.

ETL Layer
---------

- ``scrape.py``: Downloads raw data from external sources.
- ``clean.py``: Cleans and normalizes scraped records.
- ``load_data.py``: Loads cleaned data into the PostgreSQL database.

Database Layer
--------------

- ``query_data.py``: Encapsulates SQL queries and database connections.
- Relies on ``DATABASE_URL`` environment variable for connection details.


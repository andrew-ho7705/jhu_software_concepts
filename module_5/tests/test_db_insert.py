"""
Test module for database insertion functionality.
"""

import datetime
import pytest
from module_4.src.app.pages import pull_data
from module_4.src import load_data
import module_2.clean as clean_module


@pytest.mark.db
def test_insert_on_pull(
    client, mock_llm, connect_to_db, example_applicant_data, monkeypatch
):
    """
    Test database insertion during data pull operation
    """
    # Test insert on pull
    _, cur = connect_to_db

    # Before: target table empty
    cur.execute("SELECT COUNT(*) FROM test")
    count_before_insert = cur.fetchone()[0]
    assert count_before_insert == 0

    monkeypatch.setattr(clean_module, "clean_data", lambda data: example_applicant_data)
    monkeypatch.setattr(pull_data, "__defaults__", ("test",))

    # After POST/pull-data new rows exist with non-null fields
    response = client.post("/pull_data")
    assert response.status_code == 200

    cur.execute("SELECT COUNT(*) FROM test")
    count_after_insert = cur.fetchone()[0]
    assert count_after_insert == len(example_applicant_data)

    cur.execute("SELECT llm_generated_program, llm_generated_university FROM test")
    entries = cur.fetchall()
    for llm_program, llm_uni in entries:
        assert llm_program
        assert llm_uni


@pytest.mark.db
def test_idempotency(
    client, mock_llm, connect_to_db, example_duplicate_applicant_data, monkeypatch
):
    """
    Test idempotency and constraint handling for duplicate data
    """
    # Test idempotency / constraints
    _, cur = connect_to_db

    monkeypatch.setattr(
        clean_module, "clean_data", lambda data: example_duplicate_applicant_data
    )
    monkeypatch.setattr(pull_data, "__defaults__", ("test",))

    # Duplicate rows do not create duplicates in database (accidentally pulling the
    # same data should not result in the database acquiring duplicated rows)
    response = client.post("/pull_data")
    assert response.status_code == 200

    cur.execute("SELECT COUNT(*) FROM test")
    count_after_insert = cur.fetchone()[0]
    assert count_after_insert == 1


@pytest.mark.db
def test_simple_query(
    client, mock_llm, connect_to_db, example_applicant_data, monkeypatch
):
    """
    Test simple query functionality with database
    """
    # Test simple query function
    _, cur = connect_to_db

    monkeypatch.setattr(clean_module, "clean_data", lambda data: example_applicant_data)
    monkeypatch.setattr(pull_data, "__defaults__", ("test",))

    response = client.post("/pull_data")
    assert response.status_code == 200

    # You should be able to query your data to return a dict with our expected
    # keys (the required data fields within M3)
    cur.execute(
        """
                SELECT program, comments, date_added, url, status, term, 
                       llm_generated_program, llm_generated_university 
                FROM test
                """
    )
    entries = cur.fetchall()
    for entry in entries:
        assert entry[0]  # program
        assert entry[1]  # comments
        assert entry[2]  # date_added
        assert entry[3]  # url
        assert entry[4]  # status
        assert entry[5]  # term
        assert entry[6]  # llm_generated_program
        assert entry[7]  # llm_generated_university


@pytest.mark.db
def test_load_to_database(connect_to_db, mock_llm, example_applicant_data, monkeypatch):
    """
    Test loading data to database functionality
    """
    _, cur = connect_to_db

    monkeypatch.setattr(load_data, "load_data", lambda _: example_applicant_data)

    load_data.load_to_database("test")

    # Verify that all rows are inserted
    cur.execute("SELECT COUNT(*) FROM test")
    count = cur.fetchone()[0]
    assert count == len(example_applicant_data)

    # Verify that LLM-generated fields exist (they'll be None since we didn't run LLM here)
    cur.execute("SELECT llm_generated_program, llm_generated_university FROM test")
    entries = cur.fetchall()
    for llm_program, llm_uni in entries:
        assert llm_program is None
        assert llm_uni is None


@pytest.mark.db
def test_parse_date():
    """
    Test date parsing functionality
    """
    assert (
        load_data.parse_date("Added on September 17, 2025")
        == datetime.datetime(int(2025), 9, int(17)).date()
    )
    assert load_data.parse_date("") is None
    assert load_data.parse_date("Added on Sept 17, 2025") is None


@pytest.mark.db
def test_handle_score():
    """
    Test score handling functionality
    """
    assert load_data.handle_score("20.25") == 20.25
    assert load_data.handle_score(" ") is None

import pytest
from module_4.src.app.pages import pull_data
import module_2.clean as clean_module

@pytest.mark.db
def test_insert_on_pull(client, connect_to_db, example_applicant_data, monkeypatch):
    _, cur = connect_to_db

    cur.execute("SELECT COUNT(*) FROM test")
    count_before_insert = cur.fetchone()[0]
    assert count_before_insert == 0

    monkeypatch.setattr(clean_module, "clean_data", lambda data: example_applicant_data)
    monkeypatch.setattr(pull_data, "__defaults__", ("test",))

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
def test_idempotency(client, connect_to_db, example_duplicate_applicant_data, monkeypatch):
    _, cur = connect_to_db

    monkeypatch.setattr(clean_module, "clean_data", lambda data: example_duplicate_applicant_data)
    monkeypatch.setattr(pull_data, "__defaults__", ("test",))

    response = client.post("/pull_data")
    assert response.status_code == 200

    cur.execute("SELECT COUNT(*) FROM test")
    count_after_insert = cur.fetchone()[0]
    assert count_after_insert == 1

@pytest.mark.db
def test_simple_query(client, connect_to_db, example_applicant_data, monkeypatch):
    _, cur = connect_to_db

    monkeypatch.setattr(clean_module, "clean_data", lambda data: example_applicant_data)
    monkeypatch.setattr(pull_data, "__defaults__", ("test",))

    response = client.post("/pull_data")
    assert response.status_code == 200

    cur.execute("SELECT program, comments, date_added, url, status, term, llm_generated_program, llm_generated_university FROM test")
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
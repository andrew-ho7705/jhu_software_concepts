import pytest
import module_2.clean as clean_module
from module_4.src.app.pages import pull_data
from module_4.src.query_data import query_data


@pytest.mark.integration
def test_end_to_end_flow(client, mock_llm, connect_to_db, example_applicant_data, monkeypatch):
    _, cur = connect_to_db

    monkeypatch.setattr(
        "module_4.src.app.pages.query_data", 
        lambda execute_query, table="test": query_data(execute_query, "test")
        )
    monkeypatch.setattr(clean_module, "clean_data", lambda data: example_applicant_data)
    monkeypatch.setattr(pull_data, "__defaults__", ("test",))

    # POST /pull-data succeeds and rows are in DB
    resp_pull = client.post("/pull_data")
    assert resp_pull.status_code == 200

    cur.execute("SELECT COUNT(*) FROM test")
    count_after_pull = cur.fetchone()[0]
    assert count_after_pull == len(example_applicant_data)

    # POST /update-analysis succeeds (when not busy)
    resp_update = client.post("/update_analysis")
    assert resp_update.status_code == 200

    cur.execute("SELECT llm_generated_program, llm_generated_university FROM test")
    rows = cur.fetchall()
    assert all(p and u for p, u in rows)

    # GET /analysis shows updated analysis with correctly formatted values
    resp_render = client.get("/")
    assert resp_render.status_code == 200

@pytest.mark.integration
def test_multiple_pulls_consistent(client, mock_llm, connect_to_db,
                                   example_duplicate_applicant_data, monkeypatch):
    _, cur = connect_to_db

    monkeypatch.setattr(clean_module, "clean_data", lambda data: example_duplicate_applicant_data)
    monkeypatch.setattr(pull_data, "__defaults__", ("test",))

    # Running POST /pull-data twice with overlapping data remains consistent with uniqueness policy
    resp1 = client.post("/pull_data")
    assert resp1.status_code == 200

    resp2 = client.post("/pull_data")
    assert resp2.status_code == 200

    cur.execute("SELECT COUNT(*) FROM test")
    count_final = cur.fetchone()[0]
    assert count_final == 1

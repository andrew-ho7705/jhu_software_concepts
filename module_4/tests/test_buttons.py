import pytest

@pytest.mark.buttons
def test_pull_data_success(client, mock_llm, monkeypatch, example_applicant_data):
    # Test POST /pull-data (or whatever you named the path posting the pull data request)
    def fake_loader():
        return example_applicant_data

    monkeypatch.setattr("module_4.src.app.pages.scrape.scrape_survey_page", lambda pages=1: fake_loader)
    monkeypatch.setattr("module_4.src.app.pages.scrape.scrape_raw_data", lambda data: fake_loader)
    monkeypatch.setattr("module_4.src.app.pages.clean.clean_data", lambda data: fake_loader)

    # Returns 200
    resp = client.post("/pull_data")
    assert resp.status_code == 200
    # Triggers the loader with the rows from the scraper (should be faked / mocked)
    assert b"Success" in resp.data

@pytest.mark.buttons
def test_update_analysis_success(client, mock_llm):
    # Test POST /update-analysis (or whatever you named the path posting the update analysis request)
    # Returns 200 when not busy
    resp = client.post("/update_analysis")
    assert resp.status_code == 200
    assert b"Success" in resp.data

@pytest.mark.buttons
def test_busy_gating(client, mock_llm, monkeypatch):
    # Test busy gating
    monkeypatch.setattr("module_4.src.app.pages.scrape_running", True)

    # When busy, POST /pull-data returns 409
    resp1 = client.post("/pull_data")
    assert resp1.status_code == 409

    # When a pull is “in progress”, POST /update-analysis returns 409 (and performs no update).
    resp2 = client.post("/update_analysis")
    assert resp2.status_code == 409
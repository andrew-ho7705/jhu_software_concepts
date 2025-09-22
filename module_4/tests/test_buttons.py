import pytest

@pytest.mark.buttons
def test_pull_data_success(client, monkeypatch, example_applicant_data):
    def fake_loader():
        return example_applicant_data

    monkeypatch.setattr("module_4.src.app.pages.scrape.scrape_survey_page", lambda pages=1: fake_loader)
    monkeypatch.setattr("module_4.src.app.pages.scrape.scrape_raw_data", lambda data: fake_loader)
    monkeypatch.setattr("module_4.src.app.pages.clean.clean_data", lambda data: fake_loader)

    resp = client.post("/pull_data")
    assert resp.status_code == 200
    assert b"Success" in resp.data

@pytest.mark.buttons
def test_update_analysis_success(client):
    resp = client.post("/update_analysis")
    assert resp.status_code == 200
    assert b"Success" in resp.data

@pytest.mark.buttons
def test_busy_gating(client, monkeypatch):
    monkeypatch.setattr("module_4.src.app.pages.scrape_running", True)

    resp1 = client.post("/pull_data")
    assert resp1.status_code == 409

    resp2 = client.post("/update_analysis")
    assert resp2.status_code == 409
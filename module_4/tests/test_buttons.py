import pytest

@pytest.fixture
def example_applicant_data():
    return [
        {
            "program": "Computer Science, Johns Hopkins University",
            "comments": "Masters in Comupter Science at JHU",
            "date_added": "Added on January 1, 2021",
            "url": "https://www.thegradcafe.com/survey/result/123456",
            "status": "Accepted on 20 Dec",
            "term": "Fall 2021",
            "US/International": "American",
            "GPA": "3.13",
            "Degree": "Masters"
        },
        {
            "program": "Accounting, University Of Maryland",
            "comments": "Money money money",
            "date_added": "Added on February 2, 2022",
            "url": "https://www.thegradcafe.com/survey/result/234567",
            "status": "Accepted on 18 Jan",
            "term": "Fall 2022",
            "US/International": "International",
            "GPA": "3.85",
            "Degree": "PhD"
        },
        {
            "program": "Nursing, Towson University",
            "comments": "I am nurse",
            "date_added": "Added on March 3, 2023",
            "url": "https://www.thegradcafe.com/survey/result/345678",
            "status": "Rejected on 31 Jan",
            "term": "Fall 2023",
            "US/International": "American",
            "GPA": "3.17",
            "Degree": "Other"
        }
    ]

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
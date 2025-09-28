"""
Test module for Flask page functionality.
"""

import pytest


@pytest.mark.parametrize(
    "page_name, method, expected_result",
    [
        ("/", "GET", 200),
        ("/pull_data", "POST", 200),
        ("/update_analysis", "POST", 200),
    ],
)
@pytest.mark.web
def test_page_load(page_name, expected_result, method, client, monkeypatch):
    """
    Test for basic functionality and HTML elements on analysis page
    """

    # Mock data for q9, q10
    def fake_execute(query, multi_row=False):
        if "GROUP BY degree" in query:
            return [("Masters", 45.67), ("PhD", 30.12)]
        if "GROUP BY llm_generated_university" in query:
            return [("JHU", 25.0), ("Georgetown", 33.33)]
        return 1.23

    monkeypatch.setattr("module_4.src.app.pages.execute_query", fake_execute)

    if method == "GET":
        response = client.get(page_name)
    else:
        response = client.post(page_name)

    assert response.status_code == expected_result

    html = response.data.decode()
    # Test GET /analysis (page load)
    if method == "GET":
        response = client.get(page_name)
    if method == "POST":
        response = client.post(page_name)

    assert response.status_code == expected_result

    html = response.data.decode()

    # Page Contains both “Pull Data” and “Update Analysis” buttons
    # Page text includes “Analysis” and at least one “Answer:”
    if page_name == "/":
        assert "Pull Data" in html
        assert "Update Analysis" in html
        assert "Analysis" in html
        assert "Answer:" in html

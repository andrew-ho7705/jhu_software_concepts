import pytest
# from module_4.src.app.app import create_app
from flask import Flask

@pytest.mark.parametrize("page_name, method, expected_result",
[
    ("/", "GET", 200),
    ("/pull_data", "POST", 200),
    ("/update_analysis", "POST", 200),
])

@pytest.mark.web
def test_page_load(page_name, expected_result, method, client):
    # Test app factory / Config: Assert a testable Flask app is created with required routes (e.g. should test each of your “/routes” that you establish in flask)
    # assert app is not None
    # assert type(app) == type(Flask(__name__))
    # Test GET /analysis (page load)
    if method == "GET":
        response = client.get(page_name)
    if method == "POST":
        response = client.post(page_name)

    
    assert response.status_code == expected_result

    html = response.data.decode()

    # Page Contains both “Pull Data” and “Update Analysis” buttons, Page text includes “Analysis” and at least one “Answer:”
    if page_name == "/":  
        assert "Pull Data" in html
        assert "Update Analysis" in html
        assert "Analysis" in html
        assert "Answer:" in html

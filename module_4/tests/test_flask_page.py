import pytest
from module_4.src.app.app import app as flask_app


@pytest.fixture
def app():
    """Use the global Flask app instance."""
    flask_app.config.update({"TESTING": True})
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.mark.parametrize("page_name, method, expected_result",
[
    ("/", "GET", 200),
    ("/pull_data", "POST", 302),
    ("/update_analysis", "POST", 302),
])
def test__page_load(page_name, expected_result, method, client):
    if method == "GET":
        response = client.get(page_name)
    else:
        response = client.post(page_name)

    assert response.status_code == expected_result

    html = response.data.decode()

    if page_name == "/":  
        assert "Pull Data" in html
        assert "Update Analysis" in html
        assert "Analysis" in html
        assert "Answer:" in html

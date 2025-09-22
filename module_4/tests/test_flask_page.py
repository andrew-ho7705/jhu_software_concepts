import pytest

@pytest.mark.parametrize("page_name, method, expected_result",
[
    ("/", "GET", 200),
    ("/pull_data", "POST", 200),
    ("/update_analysis", "POST", 200),
])

@pytest.mark.web
def test_page_load(page_name, expected_result, method, client):
    if method == "GET":
        response = client.get(page_name)
    if method == "POST":
        response = client.post(page_name)

    assert response.status_code == expected_result

    html = response.data.decode()

    if page_name == "/":  
        assert "Pull Data" in html
        assert "Update Analysis" in html
        assert "Analysis" in html
        assert "Answer:" in html

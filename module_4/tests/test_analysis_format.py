import pytest
import re

@pytest.mark.parametrize("page_name", [("/")])

@pytest.mark.analysis
def test_analysis_format(page_name, client):

    response = client.get(page_name)
    html = response.data.decode()

    answer_count = html.count("Answer:")

    percentages = re.findall(r"\d+\.?\d*%", html)
    correct_format_percent = [p for p in percentages if re.match(r"^\d+\.\d{2}%", p)]

    assert len(correct_format_percent) == 21
    assert answer_count == 11

import pytest
import re

@pytest.mark.parametrize("page_name", [("/")])

@pytest.mark.analysis
def test_analysis_format(page_name, client):
    # Test labels & Rounding
    response = client.get(page_name)
    html = response.data.decode()

    # Test that your page include “Answer” labels for rendered analysis
    answer_count = html.count("Answer:")
    assert answer_count == 11

    # Test that any percentage is formatted with two decimals
    percentages = re.findall(r"\d+\.?\d*%", html)
    correct_format_percent = [p for p in percentages if re.match(r"^\d+\.\d{2}%", p)]
    assert len(correct_format_percent) == 21

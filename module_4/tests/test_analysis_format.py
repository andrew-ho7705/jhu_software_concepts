import pytest
import re

@pytest.mark.parametrize("page_name", [("/")])

@pytest.mark.analysis
def test_analysis_format(page_name, client, monkeypatch):
    # Test labels & Rounding
    fake_results = {
        "q1": 6640, "q2": 60.60, "q3a": 3.79, "q3b": 177.39, "q3c": 159.67, "q3d": 6.35,
        "q4": 3.77, "q5": 35.94, "q6": 3.76, "q7": 13, "q8": 0, "q9": [], "q10": []
    }
    monkeypatch.setattr("module_4.src.app.pages.query_data", lambda execute_query: fake_results)

    response = client.get(page_name)
    html = response.data.decode()

    # Test that your page include “Answer” labels for rendered analysis
    answer_count = html.count("Answer:")
    assert answer_count == 11

    # Test that any percentage is formatted with two decimals
    percentages = re.findall(r"\d+\.\d{2}%", html)
    correct_format_percent = [p for p in percentages if re.match(r"^\d+\.\d{2}%", p)]
    assert len(correct_format_percent) == 2

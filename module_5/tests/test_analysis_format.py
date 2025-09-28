"""
Test formatting functions and for consistency across the app
"""

import re
import pytest


@pytest.mark.parametrize("page_name", ["/"])
@pytest.mark.analysis
def test_analysis_format(page_name, client, fake_results, monkeypatch):
    """
    Test percentage formatting on analysis page
    """
    # Test labels & Rounding
    monkeypatch.setattr(
        "module_4.src.app.pages.query_data", lambda execute_query: fake_results
    )

    response = client.get(page_name)
    html = response.data.decode()

    # Test that your page include “Answer” labels for rendered analysis
    answer_count = html.count("Answer:")
    assert answer_count == 11

    # Test that any percentage is formatted with two decimals
    percentages = re.findall(r"\d+\.\d{2}%", html)
    correct_format_percent = [p for p in percentages if re.match(r"^\d+\.\d{2}%", p)]
    assert len(correct_format_percent) == 2

import psycopg2
import sys
import os
import re
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from module_2.clean import load_data


def handle_score(score):
    """
    Convert a numeric string to float or return None if invalid/falsy.

    Args:
        score: Score value.

    Returns:
        float | None: Parsed numeric value or None.
    """
    
    if (
        score is None
        or score in ("N/A", "")
        or score == ""
        or score == "0"
        or score == "0.00"
    ):
        return None
    try:
        return float(score)
    except (ValueError, TypeError):
        return None


def parse_date(date_string):
    """
    Parse date string in format 'Added on Month DD, YYYY'.

    Args:
        date_string: Date string.

    Returns:
        datetime.date | None: Parsed date or None if invalid.
    """

    # Only for the date_added field
    if not date_string or date_string == "":
        return None

    date_string = re.sub(r"Added on\s+", "", date_string, flags=re.IGNORECASE)

    pattern = r"(\w+)\s+(\d{1,2}),\s+(\d{4})"
    match = re.search(pattern, date_string, re.IGNORECASE)

    if match:
        month_name, day, year = match.groups()

        month_names = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        month = month_names.get(month_name.lower())
        if month:
            return datetime.datetime(int(year), month, int(day)).date()
    return None


def load_to_database(table):
    """
    Load applicant data from JSON into PostgreSQL.

    Args:
        table: Target database table name.
    
    Returns:
        Nothing
    """

    conn = psycopg2.connect(dbname="postgres", user="postgres")
    data = load_data("../module_2/llm_extend_applicant_data.json")

    with conn.cursor() as cur:
        for record in data:
            cur.execute(
                f"""
                INSERT INTO {table} (
                    program, comments, date_added, url, status, term, 
                    us_or_international, gpa, gre, gre_v, gre_aw, degree, 
                    llm_generated_program, llm_generated_university) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    record.get("program"),
                    record.get("comments"),
                    parse_date(record.get("date_added")),
                    record.get("url"),
                    record.get("status"),
                    record.get("term"),
                    record.get("US/International"),
                    handle_score(record.get("GPA")),
                    handle_score(record.get("GRE")),
                    handle_score(record.get("GRE_V")),
                    handle_score(record.get("GRE_AW")),
                    record.get("Degree"),
                    record.get("llm-generated-program"),
                    record.get("llm-generated-university"),
                ),
            )
    conn.commit()
    conn.close()

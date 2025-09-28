"""
Data loading and processing utilities for TheGradCafe analysis.
"""

import datetime
import os
import re

from module_2.clean import load_data
import psycopg
from psycopg import sql


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

    with psycopg.connect(os.environ.get("DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            data = load_data("../module_2/llm_extend_applicant_data.json")
            for record in data:
                insert_stmt = sql.SQL("""
                INSERT INTO {table} (
                    program, comments, date_added, url, status, term,
                    us_or_international, gpa, gre, gre_v, gre_aw, degree,
                    llm_generated_program, llm_generated_university
                )
                VALUES (
                    {program}, {comments}, {date_added}, {url}, {status}, {term},
                    {us_or_international}, {gpa}, {gre}, {gre_v}, {gre_aw}, {degree},
                    {llm_generated_program}, {llm_generated_university}
                )
                LIMIT 1
                """).format(
                table=sql.Identifier(table),
                program=sql.Placeholder("program"),
                comments=sql.Placeholder("comments"),
                date_added=sql.Placeholder("date_added"),
                url=sql.Placeholder("url"),
                status=sql.Placeholder("status"),
                term=sql.Placeholder("term"),
                us_or_international=sql.Placeholder("us_or_international"),
                gpa=sql.Placeholder("gpa"),
                gre=sql.Placeholder("gre"),
                gre_v=sql.Placeholder("gre_v"),
                gre_aw=sql.Placeholder("gre_aw"),
                degree=sql.Placeholder("degree"),
                llm_generated_program=sql.Placeholder("llm_generated_program"),
                llm_generated_university=sql.Placeholder("llm_generated_university")
            )

                cur.execute(
                    insert_stmt,
                    {
                        "program": record.get("program"),
                        "comments": record.get("comments"),
                        "date_added": parse_date(record.get("date_added")),
                        "url": record.get("url"),
                        "status": record.get("status"),
                        "term": record.get("term"),
                        "us_or_international": record.get("US/International"),
                        "gpa": handle_score(record.get("GPA")),
                        "gre": handle_score(record.get("GRE")),
                        "gre_v": handle_score(record.get("GRE_V")),
                        "gre_aw": handle_score(record.get("GRE_AW")),
                        "degree": record.get("Degree"),
                        "llm_generated_program": record.get("llm-generated-program"),
                        "llm_generated_university": record.get("llm-generated-university"),
                    }
                )
                conn.commit()

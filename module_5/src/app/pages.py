"""
Flask routes module for TheGradCafe data analysis web interface.
"""

import threading
import requests
import psycopg
from psycopg import sql
from flask import Blueprint, render_template, jsonify, redirect, url_for
from module_2 import scrape, clean
from module_5.src.load_data import parse_date, handle_score
from module_5.src.query_data import execute_query, connect_to_db, query_data

bp = Blueprint("pages", __name__)
scrape_lock = threading.Lock()


def _process_llm_data(new_entries):
    """
    Process entries through LLM service
    """
    llm_data = []
    entry_mapping = {}

    for i, entry in enumerate(new_entries):
        program_text = entry.get("program").strip() or entry.get("comments", "").strip()
        if program_text:
            llm_data.append({"program": program_text})
            entry_mapping[len(llm_data) - 1] = i

    return llm_data, entry_mapping


def _call_llm_service(llm_data, entry_mapping, new_entries):
    """
    Call LLM service and update entries with results
    """
    batch_size = 10
    for batch_start in range(0, len(llm_data), batch_size):
        batch_end = min(batch_start + batch_size, len(llm_data))
        batch_data = llm_data[batch_start:batch_end]

        llm_url = "http://localhost:8000/standardize"
        response = requests.post(llm_url, json=batch_data, timeout=60)
        response.raise_for_status()

        llm_results = response.json()
        processed_entries = llm_results.get("rows", [])

        for j, processed_entry in enumerate(processed_entries):
            original_index = entry_mapping[batch_start + j]
            new_entries[original_index]["llm_generated_program"] = processed_entry.get(
                "llm-generated-program", ""
            )
            new_entries[original_index]["llm_generated_university"] = (
                processed_entry.get("llm-generated-university", "")
            )


def _prepare_insert_data(new_entries):
    """
    Prepare data for database insertion
    """
    insert_data = []
    for entry in new_entries:
        insert_data.append(
            (
                entry["program"],
                entry["comments"],
                parse_date(entry["date_added"]),
                entry["url"],
                entry["status"],
                entry["term"],
                entry["US/International"],
                handle_score(entry.get("GPA", "")),
                handle_score(entry.get("GRE", "")),
                handle_score(entry.get("GRE_V", "")),
                handle_score(entry.get("GRE_AW", "")),
                entry["Degree"],
                entry.get("llm_generated_program", ""),
                entry.get("llm_generated_university", ""),
            )
        )
    return insert_data


@bp.route("/")
def home():
    """
    Homepage route: display analysis results.

    Returns:
        str: Rendered HTML template with query results.
    """

    results = query_data(execute_query)
    return render_template("pages/home.html", **results)


@bp.route("/pull_data", methods=["POST"])
def pull_data(table_name="applicants"):
    """
    Scrape and update applicants table with new entries.

    Args:
        table_name: Database table to insert new entries.

    Returns:
        Response: JSON message.
    """

    with scrape_lock:
        try:
            print("Scraping data...")
            survey_data = scrape.scrape_survey_page(pages=1)
            raw_data = scrape.scrape_raw_data(survey_data)
            cleaned = clean.clean_data(raw_data)
            print(f"Scraped {len(cleaned)} entries")

            # Check which entries already exist in database
            with connect_to_db() as conn:
                with conn.cursor() as cur:
                    urls = [entry["url"] for entry in cleaned]
                    if urls:
                        query = sql.SQL("""
                                SELECT url FROM {table} WHERE url IN ({placeholders})
                                """).format(
                            table=sql.Identifier(table_name),
                            placeholders=sql.SQL(",").join(sql.Placeholder() * len(urls))
                        )
                        cur.execute(query, urls)
                        existing_urls = {row[0] for row in cur.fetchall()}

                    # Filter out existing entries
                    new_entries = [
                        entry for entry in cleaned if entry["url"] not in existing_urls
                    ]
                    print(f"Found {len(new_entries)} new entries to process")

            # Run new entries through LLM
            if new_entries:
                print(f"Processing {len(new_entries)} new entries through LLM...")
                llm_data, entry_mapping = _process_llm_data(new_entries)
                _call_llm_service(llm_data, entry_mapping, new_entries)

            if new_entries:
                insert_data = _prepare_insert_data(new_entries)
                with connect_to_db() as conn:
                    with conn.cursor() as cur:
                        columns = [
                            "program", "comments", "date_added", "url", "status", "term",
                            "us_or_international", "gpa", "gre", "gre_v", "gre_aw", "degree",
                            "llm_generated_program", "llm_generated_university"
                        ]
                        cur.executemany(
                            sql.SQL("""
                                INSERT INTO {table} ({fields})
                                VALUES ({placeholders})
                                ON CONFLICT (url) DO NOTHING
                            """).format(
                                table=sql.Identifier(table_name),
                                fields=sql.SQL(",").join(map(sql.Identifier, columns)),
                                placeholders=sql.SQL(",").join(sql.Placeholder() * len(columns))
                            ), insert_data
                        )
                        conn.commit()

            print(f"Scrape complete: {len(new_entries)} new entries added")

        except (requests.RequestException, psycopg.Error, ValueError) as e:
            print(f"Error in pull_data: {e}")
            return jsonify({"error": "Busy"}), 409

    # return jsonify({"message": "Success"}), 200
    return redirect(url_for("pages.home"))


@bp.route("/update_analysis", methods=["POST"])
def update_analysis():
    """
    Scrape and update applicants table with new entries.

    Returns:
        Response: JSON message.
    """

    with scrape_lock:
        try:
            query_data(execute_query)
            print("Analysis updated successfully")
            # return jsonify({"message": "Success"}), 200
            return redirect(url_for("pages.home"))
        except (requests.RequestException, psycopg.Error, ValueError) as e:
            print(f"Error in pull_data: {e}")
            return jsonify({"error": "Busy"}), 409

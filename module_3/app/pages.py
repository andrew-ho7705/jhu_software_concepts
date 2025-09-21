from flask import Blueprint, render_template, redirect, url_for, flash
from ..query_data import execute_query, connect_to_db, query_data
from module_2 import scrape, clean

bp = Blueprint("pages", __name__)
scrape_running = False

@bp.route("/")
def home():
    results = query_data(execute_query)
    return render_template("pages/home.html", **results)

@bp.route('/pull_data', methods=['POST'])
def pull_data():
    global scrape_running
    if scrape_running:
        return redirect(url_for('pages.home'))

    scrape_running = True
    try:
        survey_data = scrape.scrape_survey_page(pages=3)
        raw_data = scrape.scrape_raw_data(survey_data)
        cleaned = clean.clean_data(raw_data)

        conn = connect_to_db()
        cur = conn.cursor()

        for entry in cleaned:
            print(entry)
            cur.execute("SELECT 1 FROM applicants WHERE url = %s", (entry["url"],))
            if not cur.fetchone():
                cur.execute("""
                            INSERT INTO applicants (
                                program, comments, date_added, url, status, term, 
                                us_or_international, gpa, gre, gre_v, gre_aw, degree, 
                                llm_generated_program, llm_generated_university
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, 
                            (
                                entry["program"],
                                entry["comments"],
                                entry["date_added"],
                                entry["url"],
                                entry["status"],
                                entry["term"],
                                entry["US/International"],
                                entry.get("GPA", ""),
                                entry.get("GRE", ""),
                                entry.get("GRE_V", ""),
                                entry.get("GRE_AW", ""),
                                entry["Degree"],
                                entry["llm_generated_program"],
                                entry["llm_generated_university"],
                            ))


        conn.commit()
        cur.close()
        conn.close()

        print("Scrape complete:", len(cleaned))

    finally:
        scrape_running = False

    return redirect(url_for('pages.home'))

@bp.route('/update_analysis', methods=['POST'])
def update_analysis():
    global scrape_running
    if scrape_running:
        print("Currently reanalyzing")
        # flash("Cannot update analysis while data pull is running.", "warning")
    else:
        _ = query_data(execute_query)
        # flash("Analysis updated with the latest data!", "success")
    return redirect(url_for('pages.home'))
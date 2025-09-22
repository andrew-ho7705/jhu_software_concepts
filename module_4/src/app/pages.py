from flask import Blueprint, render_template, redirect, url_for, jsonify
from ..query_data import execute_query, connect_to_db, query_data
from module_2 import scrape, clean
from ..load_data import parse_date, handle_score
import requests

bp = Blueprint("pages", __name__)
scrape_running = False

@bp.route("/")
def home():
    results = query_data(execute_query)
    return render_template("pages/home.html", **results)

@bp.route('/pull_data', methods=['POST'])
def pull_data(table_name="applicants"):
    global scrape_running
    if scrape_running:
        return jsonify({"error": "Busy"}), 409

    scrape_running = True
    try:
        print("Scraping data...")
        survey_data = scrape.scrape_survey_page(pages=1)
        raw_data = scrape.scrape_raw_data(survey_data)
        cleaned = clean.clean_data(raw_data)
        print(f"Scraped {len(cleaned)} entries")

        # Check which entries already exist in database
        conn = connect_to_db()
        cur = conn.cursor()
        
        urls = [entry["url"] for entry in cleaned]
        if urls:
            placeholders = ','.join(['%s'] * len(urls))
            cur.execute(f"SELECT url FROM {table_name} WHERE url IN ({placeholders})", urls)
            existing_urls = {row[0] for row in cur.fetchall()}
            
            # Filter out existing entries
            new_entries = [entry for entry in cleaned if entry["url"] not in existing_urls]
            print(f"Found {len(new_entries)} new entries to process")
        else:
            new_entries = cleaned

        # Run new entries through LLM
        if new_entries:
            print(f"Processing {len(new_entries)} new entries through LLM...")
            
            llm_data = []
            entry_mapping = {}
            
            for i, entry in enumerate(new_entries):
                program_text = entry.get("program").strip() or entry.get("comments", "").strip()
                if program_text:
                    llm_data.append({"program": program_text})
                    entry_mapping[len(llm_data) - 1] = i

            batch_size = 10
            for batch_start in range(0, len(llm_data), batch_size):
                batch_end = min(batch_start + batch_size, len(llm_data))
                batch_data = llm_data[batch_start:batch_end]
                
                try:
                    llm_url = "http://localhost:8000/standardize"
                    response = requests.post(llm_url, json=batch_data, timeout=60)
                    response.raise_for_status()
                    
                    llm_results = response.json()
                    processed_entries = llm_results.get("rows", [])
                    
                    for j, processed_entry in enumerate(processed_entries):
                        original_index = entry_mapping[batch_start + j]
                        new_entries[original_index]["llm_generated_program"] = processed_entry.get("llm-generated-program", "")
                        new_entries[original_index]["llm_generated_university"] = processed_entry.get("llm-generated-university", "")
                    
                except Exception as e:
                    print(f"Error processing LLM batch: {e}")

        if new_entries:
            insert_data = []
            for entry in new_entries:
                insert_data.append((
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
                ))
            
            cur.executemany(f"""
                INSERT INTO {table_name} (
                    program, comments, date_added, url, status, term, 
                    us_or_international, gpa, gre, gre_v, gre_aw, degree, 
                    llm_generated_program, llm_generated_university
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
            """, insert_data)

        conn.commit()
        cur.close()
        conn.close()

        print(f"Scrape complete: {len(new_entries)} new entries added")

    except Exception as e:
        print(f"Error in pull_data: {e}")
    finally:
        scrape_running = False

    return jsonify({"message": "Success"}), 200

@bp.route('/update_analysis', methods=['POST'])
def update_analysis():
    global scrape_running
    if scrape_running:
        return jsonify({"error": "Busy"}), 409
    else:
        try:
            query_data(execute_query)
            print("Analysis updated successfully")
        except Exception as e:
            print(f"Error updating analysis: {e}")
    return jsonify({"message": "Success"}), 200
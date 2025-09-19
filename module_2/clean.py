import json
from scrape import scrape_survey_page, scrape_raw_data

# Remove fields from the dataset according to the example in the pdf
def _remove_falsy_keys(entry):
  return {k: v for k, v in entry.items() if k in 'comments' or v not in ('0', '0.00', '')}

def clean_data(raw_data):
  cleaned_list = []
  for entry in raw_data:
    # Append university to program
    if "program" in entry and "university" in entry and entry["university"]:
        entry["program"] += f', {entry["university"]}'
        entry["university"] = ""

    cleaned = {k: v for k, v in entry.items() if v or k == "comments"}
    if "comments" not in cleaned:
        cleaned["comments"] = ""
    cleaned_list.append(cleaned)
  return [_remove_falsy_keys(entry) for entry in raw_data]

def load_data(path):
  with open(path, "r", encoding="utf-8") as f:
      return json.load(f)

def save_data(data, path):
  with open(path, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=4)

survey_data = scrape_survey_page(pages=1600)
raw_data = scrape_raw_data(survey_data)
cleaned = clean_data(raw_data)

save_data(cleaned, "applicant_data.json")

loaded = load_data("applicant_data.json")

print(len(loaded))
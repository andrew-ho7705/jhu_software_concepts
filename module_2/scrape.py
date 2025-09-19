import urllib3
from bs4 import BeautifulSoup
import re


def scrape_survey_page(pages):
  http = urllib3.PoolManager()
  base_survey_url = "https://www.thegradcafe.com/survey"
  survey_page_data = {}
  
   # Grab more than enough ids in case some don't exist
  for page_num in range(1, pages + 1):
    url = f"{base_survey_url}?page={page_num}"
    response = http.request('GET', url)
    html = response.data.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for dt in soup.find_all("dt", class_="tw-relative tw-flex-none"):
      a_tag = dt.find("a", href=re.compile(r"/result/\d{6}"))
      if not a_tag:
        continue
      result_url = a_tag['href']
      match_obj = re.search(r"/result/(\d{6})", result_url)
      if not match_obj:
        continue
      result_id = int(match_obj.group(1))

      parent = dt.find_parent("tr")
      tds = parent.find_all("td")
      added_on = tds[2].get_text(strip=True)
      decision = tds[3].get_text(strip=True)
      
      next_tr = parent.find_next_sibling("tr")
      term = None
      if next_tr:
        for div in next_tr.find_all("div"):
          text = div.get_text(strip=True)
          if text.lower().startswith("fall") or text.lower().startswith("spring"):
              term = text
              break
      survey_page_data[result_id] = [added_on, decision, term]
  
  return survey_page_data

def scrape_raw_data(survey_page_data):
    http = urllib3.PoolManager()
    base_url = "https://www.thegradcafe.com/survey/result/"
    raw_data = []

    # Extract data from respective survey page entry
    for key, value in survey_page_data.items():
      url = base_url + str(key)
      added_on, decision, term = value

      try:
        response = http.request("GET", url, retries=False, timeout=5.0)
        if response.status != 200:
          continue
      except Exception as e:
        print(f"[{key}] Request failed at {url}: {e}", flush=True)
        continue

      try:
          html = response.data.decode("utf-8")
          soup = BeautifulSoup(html, "html.parser")
          dl = soup.find("dl")
      except Exception as e:
          print(f"[{key}] Parse error at {url}: {e}", flush=True)
          dl = None

      page_data = {
          "program": '',
          "university": '',
          "comments": '',
          "date_added": f'Added on {added_on}' if added_on else '',
          "url": url,
          "status": decision,
          "term": term,
          "US/International": '',
          "GRE": '',
          "GRE_V": '',
          "GPA": '',
          "Degree": '',
          "GRE_AW": ''
      }

      if dl:
          for div in dl.find_all('div', recursive=False):
              dt = div.find('dt')
              dd = div.find('dd')

              # Grabbing GRE Scores
              if not dt or not dd:
                  for li in soup.find_all('li'):
                      spans = li.find_all('span')
                      if len(spans) >= 2:
                          label = spans[0].get_text(strip=True).rstrip(':').lower()
                          value = spans[1].get_text(strip=True)
                          if label == "gre general":
                              page_data["GRE"] = value
                          elif label == "gre verbal":
                              page_data["GRE_V"] = value
                          elif label == "analytical writing":
                              page_data["GRE_AW"] = value
                  continue

              dt_text = dt.get_text(strip=True)
              dd_text = dd.get_text(strip=True)

              # Grabbing everything else
              match dt_text.lower():
                  case "program":
                      page_data["program"] = dd_text
                  case "institution":
                      page_data["university"] = dd_text
                  case "notes":
                      page_data["comments"] = dd_text if dd_text else ''
                  case "degree's country of origin":
                      page_data["US/International"] = dd_text if dd_text else ''
                  case "degree type":
                      page_data["Degree"] = dd_text if dd_text else ''
                  case "undergrad gpa":
                      page_data["GPA"] = dd_text if dd_text not in ('0', '0.00') else ''

      raw_data.append(page_data)

    return raw_data
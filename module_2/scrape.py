import urllib3
from bs4 import BeautifulSoup
import re
import json

def scrape_data():
  http = urllib3.PoolManager()
  
  base_url = "https://www.thegradcafe.com/survey/result/"
  data = []
  
  for i in range(986446, 956000, -1):
    url = base_url + str(i)
    response = http.request('GET', url)
    html = response.data.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    dl = soup.find("dl")
  
    page_data = {
      "url": url
    }
    date_added = None
    status = None
  
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
              if value != "0" and value != "0.00":
                page_data["gre"] = value
            elif label == "gre verbal":
              if value != "0" and value != "0.00":
                page_data["gre_v"] = value
            elif label == "analytical writing":
              if value != "0" and value != "0.00":
                page_data["gre_aw"] = value
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
          if dd_text:
            page_data["comments"] = dd_text
        case "notification":
          match_obj = re.search(r'(\d{2}/\d{2}/\d{4})', dd_text)
          if match_obj:
            date_parts = match_obj.group(1).split("/")
            day, month, year = date_parts
            date_added = f'{month}/{day}/{year}'
            page_data["date_added"] = f' Added on {date_added}'
        case "decision":
          status = dd_text
          page_data["status"] = status
        case "degree's country of origin":
          if dd_text:
            page_data["us/international"] = dd_text
        case "gre general":
          if dd != "0":
            page_data["gre_score"] = dd_text
        case "gre verbal":
          if dd_text != "0":
            page_data["gre_v"] = dd_text
        case "degree type":
          if dd_text:
            page_data["degree"] = dd_text
        case "undergrad gpa":
          if dd_text != "0.00" and dd_text != "0":
            page_data["gpa"] = dd_text
            
    page_data["status"] += f' on {date_added[:5]}'
    if (status != "Rejected" and status != "Interview" and status != "Wait listed"):
      page_data["term"] = f'Fall {date_added[6:11]}' if (status == "Accepted" and int(date_added[:2]) >= 1 and int(date_added[:2]) < 8) else f'Spring {date_added[6:11]}'
    data.append(page_data)  

  filename = "applicant_data.json"
  with open(filename, 'w') as f:
    json.dump(data, f, indent=4)

scrape_data()
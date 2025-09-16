from urllib.request import urlopen
from bs4 import BeautifulSoup

base_url = "https://www.thegradcafe.com/survey/?page="

for i in range(1, 9060):
  url = base_url + str(i)
  page = urlopen(url)
  html = page.read().decode("utf-8")
  soup = BeautifulSoup(html, "html.parser")
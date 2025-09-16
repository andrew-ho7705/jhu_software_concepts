from urllib.request import urlopen

base_url = "https://www.thegradcafe.com/survey/?page="

for i in range(1, 9060):
  url = base_url + str(i) 
import requests
import scraper
import json
from selenium import webdriver
import rich
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from selenium.webdriver.chrome.options import Options
# counties = ['US','GB','PK','FR','AU']
counties = ['US']
# sendstr = "{"
# for country in counties:
#     sendstr = sendstr+country+","
# sendstr.rsplit(',')
# sendstr = "}"
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.headless = True
app_id=843730063297483
app_secret='56d967108c854f3a50a57142214d05c7'
x = scraper.scrape(country_code='US',search_term='test',limit=5)
# x = scraper.scrape(url="https://graph.facebook.com/v15.0/me/adaccounts?fields=name,id&")

# rich.print_json(json.dumps(x.json()))
j_r = x.json()

driver = webdriver.Chrome(options=chrome_options)

l = []
for i in j_r['data']:
    # rich.print(i['ad_snapshot_url'])
    l.append(i['ad_snapshot_url'])

for i in l:
    driver.get(i)
    soup = bs(driver.page_source,'html.parser')
    # print(soup.div['_8n9h'])
    ii = soup.find('div',{"class":"_8n9h"})
    # print(i)
    o = urlparse(i).query
    q = o.split('&')[0].lstrip('id=')
    i_h = str(ii)
    f = open(f'thing-{q}.html',"w")
    f.write(i_h)
    f.close


# xr = requests.get('//graph.facebook.com/v2.11/act_827649548583623/adimages')
# rich.print(xr.text)
'''from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome = webdriver.Chrome('/home/rohit/Downloads/chromedriver', chrome_options=chrome_options)
#chrome = webdriver.Chrome(executable_path='/home/rohit/Downloads/chromedriver')
chrome.get('https://allevents.in/bengaluru/concerts')
info = chrome.find_element_by_xpath("//script[@type='application/ld+json']")
info.get_attribute('innerHTML')
print(info)'''


import requests
from lxml import html
import re

# https://allevents.in/api/index.php/geo/web/city_suggestions_full/<name>
url = 'https://allevents.in/bengaluru/concerts'
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"})
tree = html.fromstring(r.content)
script = tree.xpath('//script[contains(., "@context")]/text()')[0]
#data = re.search(r"@context = (.*?);$", script).group(1)
print(script)

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

a = striphtml(script)
import json
data = json.loads(a)
print(data)

lists = []
import csv
import requests 
from bs4 import BeautifulSoup
for i in lists:      # Number of pages plus one 
    url = "https://allevents.in/api/index.php/geo/web/city_suggestions_full/{}".format(i)
    r = requests.get(url)
    soup = BeautifulSoup(r.content)


'''
with open("blob.json") as f:
    obj = json.loads(f.read())

for element in obj:
    del element['image'] 

json_data.write(obj)'''
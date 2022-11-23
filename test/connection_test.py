import requests
params = {'apikey': 'l8xx24faa60a17b14ef2947fb2e8222f8f24'}
url = r'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9919172176102836/representations'
r = requests.get(url,verify = False)
print(r.text)
r= requests.get(url, params)
print(r.text)
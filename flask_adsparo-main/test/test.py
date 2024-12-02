import json
import requests

cookies_j = '''
[
{
    "domain": ".facebook.com",
    "expirationDate": 1698420139.45224,
    "hostOnly": false,
    "httpOnly": false,
    "name": "c_user",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "100006640530896",
    "id": 1
},
{
    "domain": ".facebook.com",
    "expirationDate": 1696798653.580878,
    "hostOnly": false,
    "httpOnly": true,
    "name": "datr",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "q78TY_6oTAaR3lIqyIPaiVaR",
    "id": 2
},
{
    "domain": ".facebook.com",
    "expirationDate": 1674660137.452285,
    "hostOnly": false,
    "httpOnly": true,
    "name": "fr",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "09moONyEhoSrSKShz.AWXCLkwFa0KIldEcfetETSUw-p8.BjWqIs.LN.AAA.0.0.BjWqIs.AWXzKPCcbxU",
    "id": 3
},
{
    "domain": ".facebook.com",
    "hostOnly": false,
    "httpOnly": false,
    "name": "presence",
    "path": "/",
    "sameSite": "unspecified",
    "secure": true,
    "session": true,
    "storeId": "0",
    "value": "C%7B%22t3%22%3A%5B%7B%22i%22%3A%22u.110370018458536%22%7D%5D%2C%22utc3%22%3A1662357653613%2C%22v%22%3A1%7D",
    "id": 4
},
{
    "domain": ".facebook.com",
    "expirationDate": 1696798692.855242,
    "hostOnly": false,
    "httpOnly": true,
    "name": "sb",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "q78TY7_mHOu1U6857rA2d1gp",
    "id": 5
},
{
    "domain": ".facebook.com",
    "expirationDate": 1667489522,
    "hostOnly": false,
    "httpOnly": false,
    "name": "wd",
    "path": "/",
    "sameSite": "lax",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "1885x875",
    "id": 6
},
{
    "domain": ".facebook.com",
    "expirationDate": 1698420139.452273,
    "hostOnly": false,
    "httpOnly": true,
    "name": "xs",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "11%3Ad5rpNs6M5xkakw%3A2%3A1662238690%3A-1%3A5827%3A%3AAcU8RbO9XaO4f2Uvhwek3X48Tnsyl2UpIG9Awfla-g",
    "id": 7
}
]'''

cookies_l = json.loads(cookies_j)

useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'

header = {'User-Agent':useragent}
cookies = ""


s = requests.Session()

for i in cookies_l:
    s.cookies[i['name']] = i['value']

header['cookie']=cookies
# print(cookies)

url = 'https://developers.facebook.com/tools/accesstoken/'


while True:
    r = s.get(url)
    if(r.status_code==200):
        break

f = open('help.html','w')
f.write(r.content.__str__())
f.close()
# print(r.content.__str__())

import requests
import re
login_url = "https://pushover.net/login"
destry_url = "https://pushover.net/devices/destroy/{device}"
matchme = 'meta content=”(.*)” name=”csrf-token” /'

s = requests.session()
r = s.get(login_url,verify = False)

csrf = re.search(matchme,str(r.text))
payload = {
'user[email]' : 'mertz.james@live.com',
'user[password]' : 'captmoroni829',
'authenticity_token' : csrf.group(1),
}
r = s.post(login_url,data=payload,verify=False)

print('tests')
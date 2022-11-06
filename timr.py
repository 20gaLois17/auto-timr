import sys
import requests
import re
import os
from datetime import datetime as dt
from dotenv import load_dotenv
load_dotenv()

posts = []
tzOffset = "+01:00" # +02:00 for summertime

url=os.environ.get("timr-url")

cookies= {
	"Request Cookies": {
		"remember-me": os.environ.get("remember-me-cookie"),
	}
}

headers = {
    "Accept": "*/*" ,
    "Connection": "keep-alive" ,
    "Cookie": os.environ.get("cookie-header"),
    "DNT": "1" ,
    "Host": os.environ.get("host-header"),
    "Origin": os.environ.get("origin-header"),
    "Sec-Fetch-Site": "same-origin" ,
    "TE": "trailers" ,
    "X-Requested-With": "XMLHttpRequest" ,
    "X-XSRF-TOKEN": os.environ.get("xsrf-token-header"),
}

tasks = {
    "IN":   "2134217",        # Intern
    "MUKU": "2159740",        # ->IT->Entwicklung
    "MURD": "2159826",        # ->IT->Entwicklung
    "MAS":  "2159804",        # ->IT->Entwicklung
}

billable = {                  # defaults to "true" if not set
    "IN":   "false",
    "MUKU": "true",
    "MURD": "true",
    "MAS":  "true",
}

wtfile = open("logs.txt", "r")
days = re.split(r"---", wtfile.read())
# build all the day request objects
failCount = 0
for day in days:
    lines = day.strip().split('\n')
    # date needs to be in first line
    currDate = lines[0].strip()
    d = dt.strptime(currDate, "%d.%m.%y")

    for i in range(1, len(lines)):
        entry = {
            "changed": "true", # necessary?
            "status": "100",   # necessary?
            "breakTime": "0",  # no breaks allowed
        }
        # parse description
        chunks = lines[i].strip().split(' ')
        period = chunks[0].split('-')
        # process start and end time
        entry["start"] = dt.combine(d, dt.strptime(period[0], "%H:%M").time()).strftime("%Y-%m-%dT%H:%M:%S")+tzOffset
        entry["end"]   = dt.combine(d, dt.strptime(period[1], "%H:%M").time()).strftime("%Y-%m-%dT%H:%M:%S")+tzOffset
        if not tasks.get(chunks[1]):
            failCount += 1
            print("ERR: could not match task for: ", chunks[1])
        # task id from dict
        entry["task.id"]  = tasks[chunks[1]]
        # billable from dict
        entry["billable"] = billable[chunks[1]] or "true"

        try:
            desc = re.search(r'"(.*?)"', lines[i])
            entry["description"] = desc[0].strip('"')
        except TypeError:
            failCount += 1
            print("ERR: cannot parse description from", lines[i])

        posts.append(entry)

if failCount > 0:
    print("\n->please fix {:d} issue(s) and run script again", failCount)
    sys.exit()

for post in posts:
    res = requests.post(url, data = post, headers = headers)
    print(post['description'], "[ok]" if res.status_code == 204 else "[fail]")
    print(res.text)

wtfile.close()

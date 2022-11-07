import sys
import requests
import re
import os
from datetime import datetime as dt
from dotenv import load_dotenv
load_dotenv()

TZOFFSET = "+01:00" # +02:00 for summertime
FILENAME = "logs.txt"

def build_config(keys):
    tmp = {}
    for key in keys:
        val = os.environ.get(key)
        if val == "":
            print("please set (.env) value for", key)
            sys.exit()
        else:
            tmp[key] = val
    return tmp

def build_entry(line):
    entry = {
        "changed": "true", # necessary?
        "status": "100",   # necessary?
        "breakTime": "0",  # no breaks allowed
    }
    # parse description
    chunks = line.strip().split(' ')
    period = chunks[0].split('-')
    # process start and end time
    entry["start"] = dt.combine(d, dt.strptime(period[0], "%H:%M").time()).strftime("%Y-%m-%dT%H:%M:%S")+TZOFFSET
    entry["end"]   = dt.combine(d, dt.strptime(period[1], "%H:%M").time()).strftime("%Y-%m-%dT%H:%M:%S")+TZOFFSET

    if not tasks.get(chunks[1]):
        print("ERR: could not match task for: ", chunks[1])
    # task id from dict
    entry["task.id"]  = tasks[chunks[1]]
    # billable from dict
    entry["billable"] = billable[chunks[1]] or "true"

    try:
        desc = re.search(r'"(.*?)"', line)
        entry["description"] = desc[0].strip('"')
    except TypeError:
        print("ERR: cannot parse description from", line)
        sys.exit()

    return entry

config = build_config(
    [
        "remember-me-cookie",
        "timr-url",
        "cookie-header",
        "host-header",
        "xsrf-token-header",
        "origin-header"
    ] 
)

cookies= {
	"Request Cookies": {
		"remember-me": config["remember-me-cookie"],
	}
}

headers = {
    "Accept": "*/*" ,
    "Connection": "keep-alive" ,
    "Cookie": config["cookie-header"],
    "DNT": "1" ,
    "Host": config["host-header"],
    "Origin": config["origin-header"],
    "Sec-Fetch-Site": "same-origin" ,
    "TE": "trailers" ,
    "X-Requested-With": "XMLHttpRequest" ,
    "X-XSRF-TOKEN": config["xsrf-token-header"],
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



if __name__ == "__main__":
    posts = []

    wtfile = open(FILENAME, "r")
    days = re.split(r"---", wtfile.read())
    wtfile.close()

    for day in days:
        lines = day.strip().split('\n')
        # date needs to be in first line
        currDate = lines[0].strip()
        d = dt.strptime(currDate, "%d.%m.%y")

        for i in range(1, len(lines)):
            posts.append(build_entry(lines[i]))

    for post in posts:
        res = requests.post(config["timr-url"], data = post, headers = headers)
        print(post['description'], "[ok]" if res.status_code == 204 else "[fail]")
        print(res.text)


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

def worktime_from_posts(posts):
    # for a mock call
    entry = {
        "workingTimeType.id": "459229",
        "description": "",
        "startDate": "17.11.2022",
        "startTime": "18:30",
        "startTimeZone": TZOFFSET,
        "start": "2022-11-17T18:30:00.000+01:00",
        "startHalfDay": "false",
        "endDate": "17.11.2022",
        "endTime": "19:00",
        "endTimeZone": TZOFFSET,
        "end": "2022-11-17T19:00:00.000+01:00",
        "endHalfDay": "false",
        "breakTime": "0"
    }
    # use the first posts start time as start time for workday
    # use the last posts end time as end time for workday
    # calculate the total from start and end time
    # calculate the net project time for the day
    # breakTime is the delta between total and net project time
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
    "MAAG": "2865876",
}

billable = {                  # defaults to "true" if not set
    "IN":   "false",
    "MUKU": "true",
    "MURD": "true",
    "MAS":  "true",
    "MAAG": "true",
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


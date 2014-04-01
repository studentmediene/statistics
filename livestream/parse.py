# Functions for parsing Icecast2 access.log files

import re

from datetime import datetime, timedelta

from statistics.settings import DEBUG

class LogParseError(Exception):
    pass

def parse_access_log(lines):
    """Takes list of lines and
    parses each line as an access log line."""
    if DEBUG: print("Parsing...")
    # Compile regexp
    regexp = compile_access_log_parser_regexp()

    # Open access log and parse
    parsed_lines = []
    for line in lines:
        try:
            parsed_lines.append(parse_access_log_line(line, regexp))
        except LogParseError:
            if DEBUG: print("Could not parse line!")
    if DEBUG: print("Finished parsing!")
    return parsed_lines

def parse_access_log_file(path):
    """Reads specified access path and
    parses as access log.

    DEPRECATED"""
    # Compile regexp
    regexp = compile_access_log_parser_regexp()

    # Open access log and parse
    parsed_lines = []
    with open(path) as log:
        for line in log:
            try:
                parsed_lines.append(parse_access_log_line(line, regexp))
            except LogParseError:
                if DEBUG: print("Could not parse line!")
    return parsed_lines

def compile_access_log_parser_regexp():
    # Regular expression definitions
    re1='((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))(?![\\d])' ## IP address
    re2='.*?'   	    # Space
    re3='(\\[.*?\\])'   ## Date/time with square braces
    re4='.*?'   	    # Space
    re5='(".*?")'       ## HTTP request
    re6='.*?'   	    # Space
    re7='(\\d+)'        ## HTTP status
    re8='.*?'   	    # Space
    re9='(\\d+)'        ## Bytes
    re10='.*?'  	    # Space
    re11='(".*?")'      ## HTTP referer
    re12='.*?'  	    # Space
    re13='(".*?")'      ## HTTP agent
    re14='.*?'  	    # Space
    re15='(\\d+)'       ## Seconds connected

    reg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12+re13+re14+re15,re.IGNORECASE|re.DOTALL)
    return reg

def parse_access_log_line(line, regexp):
    # Regular expression matching
    match = regexp.search(line)

    if match:
        ### POTENSIELT PROBLEM: locales og %M?
        datetime_end = datetime.strptime(match.group(2)[1:-7], "%d/%b/%Y:%H:%M:%S") # e.g. 19/Feb/2014:22:22:46
        datetime_start = datetime_end + timedelta(seconds=int(match.group(8)))
        parsed_line = {"ip": match.group(1), "datetime_end": datetime_end, "datetime_start": datetime_start, "http_request": match.group(3), "http_status": match.group(4),
                "http_bytes": match.group(5), "http_referer": match.group(6), "http_agent": match.group(7), "duration": int(match.group(8))}
        return parsed_line
    else:
        raise LogParseError({"message": "Could not match with regular expression", "line": line})

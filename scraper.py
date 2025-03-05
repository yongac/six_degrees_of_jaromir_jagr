# Functions that automatically retrieve roster information from Hockey-Reference
# so it can be directly inserted to the database.

import requests 
from bs4 import BeautifulSoup 

def scrape_roster(team_id, year, timeout=10):
    """
    Fetches html table for roster data given a team_id (e.g. "CGY") and a year (e.g. 1989 means "1988-1989 season")
    and returns a python dict mapping player_id (key) to lastname_comma_firstname (assoc. value) for each player 
    on the roster.

    Uses requests to retrieve the html and bs4 to parse it.
    Default setting of 10 seconds before timeout.
    """
    url = f"https://www.hockey-reference.com/teams/{team_id}/{year}.html" 
    try:
        response = requests.get(url, timeout = timeout)
        # TODO: optionally add error handling based on status code here.

    except requests.exceptions.Timeout as err:
        print(err)
        return dict() 

    soup = BeautifulSoup(response.content, "html.parser") 
    roster_table = soup.find("table", id="roster") 
    roster_tbody = roster_table.find("tbody")

    contents = roster_tbody.contents  # list of <tr> elements, some of which are empty (usually every other one)

    if len(contents) == 0:
        print("Error in reading table body for {team_id} in {year}.")
        return dict() 

    # Go row-by-row in the table, extracting and adding data to a dict:
    roster_dict = {} 
    for entry in contents:

        # it's a meaningful row if it has around 10 tags inside of it, but certainly > 1...
        if len(entry) > 2:
            # get the first td tag
            tdata = entry.find("td")

            # extract the values within it, at the following attributes
            player_id = tdata["data-append-csv"]
            last_comma_first = tdata["csk"]       # Note: this name may contain accents/diacritics.
            roster_dict[player_id] = last_comma_first
    
    return roster_dict 



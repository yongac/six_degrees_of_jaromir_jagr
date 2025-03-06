# Functions that automatically retrieve roster information from Hockey-Reference
# so it can be directly inserted to the database.

import time, requests 
from bs4 import BeautifulSoup 

def scrape_roster(team_id, year, timeout=10):
    """
    Returns python dict mapping player_id (key) to lastname_comma_firstname (assoc. value) for each player 
    on specified roster. 

    Fetches html table for roster data given a team_id (e.g. "CGY") and a year (e.g. 1989 means "1988-1989 season").

    Uses requests to retrieve the html and bs4 to parse it.
    Default setting of 10 seconds before timeout.
    """
    # Handle NHL lock-out season (2004-2005) without making a request
    if int(year) == 2005:
        return dict() 

    url = f"https://www.hockey-reference.com/teams/{team_id}/{year}.html" 
    try:
        response = requests.get(url, timeout = timeout)

        # To handle errors based on status code:
        if response.status_code != 200:
            time.sleep(2)
            print(f"Failed to retrieve {url}. Status code: {response.status_code}")
            return dict()

    except requests.exceptions.Timeout as err:
        print(err)
        return dict() 

    soup = BeautifulSoup(response.content, "html.parser") 
    roster_table = soup.find("table", id="roster") 

    # If no such roster_table is found, note it and return:
    if roster_table is None:
        print(f"Table not found for {team_id} in {year}.")
        time.sleep(2)
        return dict() 

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



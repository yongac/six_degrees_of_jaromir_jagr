# Some helper functions to manipulate the CSV files involved in building the database.
# to be imported and used in database.py

########################################################################
# Function signatures for functions herein:
#
# get_team_ids_and_names(team_names_csv)     
# get_team_ids_and_seasons(team_seasons_csv) 
#
########################################################################

def get_team_ids_and_names(team_names_csv):
    """
    Reads a CSV file with header "team_id,team_name" and converts non-header 
    columns into python dict mapping team_id (key) to team name (assoc. value)

    Returns python dict.
    """
    id_to_name = {} 
    with open(team_names_csv,"r") as file:
        rows = file.readlines()
    
    # First line is just a header, so omit it and proceed. 
    for i in range(1, len(rows)):
        row = rows[i]
        id, name = row.split(',')
        id = id.strip()
        name = name.strip()
        id_to_name[id] = name
    
    return id_to_name

def get_team_ids_and_seasons(team_seasons_csv):
    """
    Returns a dict mapping team_id to tuple (inaugural_season, most_recent_season)

    Uses CSV with header "team_id,inaugural_season,most_recent_season"
    """
    D = {}
    with open(team_seasons_csv,"r") as file:
        file.readline() # discard header
        rows = file.readlines()

    for row in rows:
        id, start, end = row.split(',')
        id = id.strip()
        start = start.strip()
        end = end.strip()
        
        D[id] = (start, end)
    
    return D

        
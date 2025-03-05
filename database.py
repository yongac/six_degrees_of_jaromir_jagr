# Python code for building and updating the database.
import sqlite3, os, time
import unicodedata # for removing diacritics from player names.
import scraper # my custom scraper, in scraper.py
import csv_helpers # in csv_helpers.py

########################################################################
# Function signatures for functions herein:
#
# add_teams_to_table(db_filename, team_id_to_name_dict) 
# add_to_database(db_filename, team_names_csv, team_seasons_csv)
# add_to_database_from_roster_dict(db_filename, roster_dict, team_id, year) 
# check_bfs_parent_ready(db_filename):
# common_team(player1_id, player2_id, db_filename)
# get_all_players(db_filename)
# get_bfs_parent(player_id, db_filename)
# get_player_name_from_id(player_id, db_filename)
# make_BFS_parent_table(bfs_parent_dict, db_filename)
# make_teammates_table(db_filename)
# remove_diacritics(name)                                  
# set_up_db(db_filename)
#
########################################################################

def add_to_database(db_filename, team_names_csv, team_seasons_csv):
    """
    Fills "players", "teams", "team_membership" tables of database at db_filename, 
    using 2 CSV files: 
      one for mapping team_ids to team names, 
      other maps team_id to both inaugural and most recent seasons. 
    """
    set_up_db(db_filename)

    # Extract team ids, names from CSV:
    team_id_to_name = csv_helpers.get_team_ids_and_names(team_names_csv) 
    # For each item in this dict, make/replace an entry in the "teams" table.
    add_teams_to_table( db_filename, team_id_to_name )  

    # Extract team_id and season range for each team, store in a dict
    team_id_to_seasons = csv_helpers.get_team_ids_and_seasons(team_seasons_csv) 
    
    # Fetch and add team_membership data for each team_id and the specified years.
    for team_id in team_id_to_seasons.keys():

        inaugural, most_recent = team_id_to_seasons[team_id]
        inaugural = int(inaugural)
        most_recent = int(most_recent)

        for year in range(inaugural, most_recent + 1):
            time.sleep(3) # Wait 5 seconds, to respect scraping rule on HockeyReference (<= 20 requests/mins)
            roster_dict = scraper.scrape_roster(team_id,year)

            add_to_database_from_roster_dict(db_filename, roster_dict, team_id, year)  

    return

def add_teams_to_table(db_filename, team_id_to_name_dict):
    """
    Uses a dictionary mapping team_id to team name and adds corr. entries to the database at db_filename. 

    Supposes that the database at db_filename has been correctly set up.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor() 
    cursor.executemany("INSERT OR REPLACE INTO teams (id, name) VALUES (?,?)", team_id_to_name_dict.items() )
    conn.commit()
    conn.close() 
    return 


def add_to_database_from_roster_dict(db_filename, roster_dict, team_id, year):
    """
    Fills player and team_membership tables in db_filename using :
        - roster information in roster_dict 
        - team_id (supplied as argument)
        - year (supplied as argument)

    Assumes it is being called within a call to [database.] add_to_database() 
    """

    # Connect to the database and make a cursor:
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Prepare template for insertion queries:
    player_query = "INSERT OR REPLACE INTO players (id, first_name, last_name) VALUES (?,?,?)"
    team_membership_query = "INSERT OR REPLACE INTO team_membership (player_id, team_id, season) VALUES (?,?,?)"

    # Prepare list for batch execution of SQL commands (for efficiency)
    player_fill_data = []   # for filling player_query
    team_membership_fill_data = [] # for team_membership_query
    
    # Loop over all players:
    for player_id in roster_dict.keys():
        last, first = roster_dict[player_id].split(',')
        
        first = first.strip()
        first = remove_diacritics(first) 

        last = last.strip()
        last = remove_diacritics(last) 

        player_fill_data.append( (player_id, first, last) )
        team_membership_fill_data.append( (player_id, team_id, year))
        
    # Once batch instructions for SQL inserting is done, execute:
    cursor.executemany(player_query, player_fill_data)
    cursor.executemany(team_membership_query, team_membership_fill_data)

    conn.commit()
    conn.close()
    return 


def check_bfs_parent_ready(db_filename):
    """
    Checks whether the table "bfs_parent" has been made yet.
        - if not, returns 0
        - if so, returns the number of rows.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    table_name = "bfs_parent"
    cursor.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,) )
    as_list = cursor.fetchall()
    if len(as_list) == 0:
        # The table was not initialized yet.
        return 0

    # otherwise, the table exists. count the number of rows.
    cursor.execute("SELECT COUNT(*) FROM bfs_parent")
    res = cursor.fetchone() # should give a tuple, which must be unpacked
    return res[0]


def common_team(player1_id, player2_id, db_filename):
    """
    Returns team name + season when players appeared on same roster.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    common_team_query = """
    WITH p1_tm AS (SELECT team_id, season FROM team_membership WHERE player_id = ?),
    p2_tm AS (SELECT team_id, season FROM team_membership WHERE player_id = ?),
    team_and_season AS (
        SELECT p1_tm.team_id AS team_id, p1_tm.season AS season
        FROM p1_tm JOIN p2_tm
        ON p1_tm.team_id = p2_tm.team_id
        AND p1_tm.season = p2_tm.season
        )
    --
    SELECT name AS team_name, season
    FROM team_and_season JOIN teams
    ON team_and_season.team_id = teams.id
    ;
    """

    cursor.execute(common_team_query, (player1_id, player2_id))
    row = cursor.fetchone()
    if row:
        team, season = row
        return f"{team} ({season-1}-{season})"
    return "Did not play together."


def get_all_players(db_filename):
    """
    Returns set of player_ids found in "players" table of db_filename.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM players;")

    as_list = cursor.fetchall() # returns rows as list of tuples
    player_set = set()
    for row in as_list:
        player_set.add(row[0])

    return player_set

def get_bfs_parent(player_id, db_filename):
    """
    Returns id for BFS parent of player_id,
    by looking it up in "bfs_parent" table of "db_filename"

    Assumes that "bfs_parent" was correctly constructed already.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("SELECT parent_id FROM bfs_parent WHERE player_id = ?;", (player_id,))

    row = cursor.fetchone()
    return row[0]

def get_player_name_from_id(player_id, db_filename):
    "Returns player name given id"
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name FROM players WHERE id = ?;", (player_id,))

    row = cursor.fetchone()
    if row:
        f,n = row
        return f"{f} {n}"
    else:
        print("No such player found in the database.")

def make_BFS_parent_table(bfs_parent_dict, db_filename):
    """
    Takes a python dictionary of BFS parent relationships between players and
    constructs a table in the database to capture these relationships.

    both columns of the resulting table will be player_ids, matching "players".id
    EXCEPT two special values:
        - The root of BFS (Jagr) has "HIMSELF" as parent
        - Players for which no connection found have "DISCONNECTED" as their parent
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    create_query = """
    CREATE TABLE IF NOT EXISTS bfs_parent (
        player_id TEXT,
        parent_id TEXT,
        FOREIGN KEY (player_id) REFERENCES players(id),
        FOREIGN KEY (parent_id) REFERENCES players(id),
        PRIMARY KEY (player_id, parent_id)
    );"""
    cursor.execute(create_query)

    cursor.executemany("INSERT OR REPLACE INTO bfs_parent (player_id, parent_id) VALUES (?,?)", bfs_parent_dict.items() )

    conn.commit() # save the changes
    conn.close()  # close the database connection
    return



def make_teammates_table(db_filename):
    """
    Builds a table consisting of pairs of teammates, rows of form (teammate1_id, teammate2_id),
    where teammate1_id < teammate2_id (lexicographically) and there are no duplicates.

    Assumes that a correctly built database with players, teams, and team_memberships.
    Assumes "teammates" table has not yet been built.
    """

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    make_teammates_query = """
    CREATE TABLE IF NOT EXISTS teammates AS
        SELECT
            tm1.player_id as teammate1_id,
            tm2.player_id as teammate2_id
        FROM team_membership tm1
        JOIN team_membership tm2
        ON tm1.team_id = tm2.team_id
        AND tm1.season = tm2.season
        WHERE teammate1_id < teammate2_id
    ;
    """

    cursor.execute(make_teammates_query)
    conn.commit()
    conn.close()


def remove_diacritics(name):
    """
    Removes accents and the like from a given name.

    Implementation obtained with ChatGPT's help.
    """
    # NFKD option changes internal representation of accented char to a sum of unaccented + accent symbol.
    normalized_version = unicodedata.normalize("NFKD", name)
    simplified = ''.join(c for c in normalized_version if not unicodedata.combining(c))
    return simplified


def set_up_db(db_filename):
    """
    A function to initialize the tables in a file called db_filename
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()


    players_query = """
    CREATE TABLE IF NOT EXISTS players (
        id TEXT PRIMARY KEY UNIQUE, -- built to match the ids used on hockey-reference
        first_name TEXT,
        last_name TEXT,
        birth_year NUMERIC
    );"""
    cursor.execute(players_query)

    teams_query = """
    CREATE TABLE IF NOT EXISTS teams (
        id TEXT PRIMARY KEY UNIQUE, -- built to match the ids used on hockey-reference
        name TEXT
    );"""
    cursor.execute(teams_query)

    membership_query = """
    CREATE TABLE IF NOT EXISTS team_membership (
        player_id TEXT,
        team_id TEXT,
        season INTEGER, -- to match hockey-reference, use the end of the season: 1999-2000 -> 2000
        FOREIGN KEY (player_id) REFERENCES players(id),
        FOREIGN KEY (team_id) REFERENCES teams(id),
        PRIMARY KEY (player_id, team_id, season)
    );"""
    cursor.execute(membership_query)

    conn.commit()
    conn.close()

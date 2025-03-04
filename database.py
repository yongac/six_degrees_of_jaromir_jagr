# Python code for building and updating the database.
import sqlite3

########################################################################
# Function signatures for functions herein:
#
# add_to_database(data_file, db_filename)
# check_bfs_parent_ready(db_filename):
# common_team(player1_id, player2_id, db_filename)
# get_all_players(db_filename)
# get_bfs_parent(player_id, db_filename)
# get_player_name_from_id(player_id, db_filename)
# make_BFS_parent_table(bfs_parent_dict, db_filename)
# make_teammates_table(db_filename)
# set_up_db(db_filename)
#
########################################################################



def add_to_database(db_filename, data_source_file, csv=False, txt=True):
    """
    Takes data from "data_source_file" and fills the "players", "teams", and "team_membership" tables
    of the database within db_filename.

    TEMPORARILY: just reads from a .txt file with all INSERT queries spelled out.
    TODO: make this compatible with a script that generates CSVs from hockey-reference...

    Assumes that set_up_db(db_filename) has previously been called.
    """
    set_up_db(db_filename)

    with open(data_source_file) as file_pointer:
        fill_instructions = file_pointer.read()
        file_pointer.close()

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.executescript(fill_instructions)
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

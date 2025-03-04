# A file for all graph theoretic operations involved in main.py

from collections import deque
import sqlite3
import database # my database.py file

########################################################################
# Function signatures for functions herein:
#
# BFS(db_filename, root='jagrja01')
# make_graph(db_filename)
# traverse_bfs_path(starting_player_id, db_filename, root='jagrja01')
#
########################################################################

def make_graph(db_filename):
    """
    Construct a graph of teammates using the SQL db file of db_filename.

    Vertex set of graph = players in the data base, nodes labelled by player_id

    Implementation: undirected edge between players A and B if and only if (id_A, id_B) or (id_B, id_A)
    appears in table "teammates", with rows of the form (teammate1_id, teammate2_id),
        --> Requires that "teammates" is properly built, correctly populated.
        --> Depends on database.py implementation.

    Returns: a dict teammates_graph, where teammates[player_id] is a set of all teammates.
    (like an adjacency list representation of the graph, but with a set instead of a list)
    """
    # Open the database file with a sqlite3 connection and cursor
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    # Set the cursor with a SQL query for teammates:
    teammates_query = "SELECT * FROM teammates;"
    cursor.execute(teammates_query)

    teammates_graph = dict() # map players to set of their teammates

    # Go row-by-row in the resulting table and add information to the graph and other dictionary.
    for row in cursor.fetchall():
        p1_id, p2_id = row
        # Add one another to each other's adjacency list
        if p1_id not in teammates_graph.keys():
            teammates_graph[p1_id] = set()
        if p2_id not in teammates_graph.keys():
            teammates_graph[p2_id] = set()

        teammates_graph[p1_id].add(p2_id)
        teammates_graph[p2_id].add(p1_id)

    # Close the data base file.
    connection.commit()
    connection.close()
    return teammates_graph



def BFS(db_filename, root='jagrja01'):
    """
    Runs one round of BFS on the teammates graph output by make_graph.

    Returns dict parent[player_id] where parent[player_id] identifies the player id
    of the BFS parent who discovered player_id.

    Only finds connection to connected players. Players for which no connection found
    will be handled separately

    If no connection found for player_id, parent[player_id] = "None found"
    """
    # Initialize the teammates graph.
    teammates_graph = make_graph(db_filename)

    # Initialize the BFS objects:
    parent = dict()
    BFS_q = deque()
    discovered = set()

    BFS_q.append(root) # Initially, only root/Jagr discovered and in queue
    discovered.add(root)
    parent[root] = "HIMSELF"

    while BFS_q:
        curr_id = BFS_q.popleft()

        # Check neighbours
        for teammate_id in teammates_graph[curr_id]:
            if teammate_id not in discovered:
                discovered.add(teammate_id)
                BFS_q.append(teammate_id)
                parent[teammate_id] = curr_id


    player_set = database.get_all_players(db_filename)
    for player_id in player_set.difference(discovered):
        parent[player_id] = "DISCONNECTED"

    return parent


def traverse_bfs_path(starting_player_id, db_filename, root='jagrja01'):
    """
    Attempts to traverse BFS path (in "bfs_parent" table of db_filename) until it finds Jagr.
        * Except: if starting_player_id is Jagr's -> returns "This is Jagr"
        * Except: if starting_player_id has no parent in BFS -> returns "Found no connection to Jagr"

    If neither exception holds, computes list of player names, computes list of shared teams,
    and returns the joined, interleaved result.
    """
    curr_id = starting_player_id
    player_id_sequence = [curr_id]
    team_sequence = []

    # Handle special cases:
    if curr_id == root:
        return 0, "This is Jagr"
    elif database.get_bfs_parent(curr_id, db_filename) == "DISCONNECTED":
        return "Infinity", "Found no connection to Jagr"

    while curr_id != root:
        parent_id = database.get_bfs_parent(curr_id, db_filename)  # returns a player id
        shared_team = database.common_team(curr_id, parent_id, db_filename) # returns a team name + season

        player_id_sequence.append(parent_id)
        team_sequence.append(shared_team)

        # move to next person in sequence
        curr_id = parent_id

    # Turn player ids into recognizable names:
    player_name_sequence = [ database.get_player_name_from_id(pid, db_filename) for pid in player_id_sequence  ]

    # Combine the player sequence and team sequence for human-readable output.
    result = ""
    for idx in range(len(team_sequence)):
        p1 = player_name_sequence[idx]
        p2 = player_name_sequence[idx+1]
        team = team_sequence[idx]
        result += f"{p1} played on {team} with {p2}.\n"

    distance = len(team_sequence)
    return distance, result


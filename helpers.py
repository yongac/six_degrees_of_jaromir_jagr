# File to store various small helper functions for the main.py file.
import sqlite3

########################################################################
# Function signatures for functions herein:
#
# count_relevant_players(first, last, db_file)
# get_and_validate_user_input(db_file)
# get_id_from_player_name(first, last, db_filename)
# get_relevant_players(first, last, db_file)
# print_relevant_players(first, last, db_file):
# set_of_relevant_players(first, last, db_file)
#
########################################################################

def count_relevant_players(first, last, db_file):
    list_of_rows = get_relevant_players(first, last, db_file)
    return len(list_of_rows)


def get_and_validate_user_input(db_file):
    """
    Returns first name, last name, and player id for player selected by user.
    """
    player_name = input("Type a player's name: ").strip().split()
    if len(player_name) != 2:
        print("\nPlease supply input as <first_name> <last_name>.")
        return False, False, False

    first = player_name[0].title()
    last = player_name[1].title()

    name_count = count_relevant_players(first, last, db_file)
    if name_count == 0:
        print("\nNo such player exists in our database.")
        return False, False, False
    elif name_count > 1:
        s = set_of_relevant_players(first, last, db_file)
        print("\nWe found multiple players with that name in our database:")
        print_relevant_players(first, last, db_file) # prints birth year and id, to distinguish players with same name.
        player_id = input("\nPlease type the ID of the player: ")
        while player_id not in s:
            player_id = input("\nPlease type the ID of the player: ")

    elif name_count == 1:
        player_id = get_id_from_player_name(first, last, db_file)

    return first, last, player_id


def get_id_from_player_name(first, last, db_filename):
    """
    Retrieves a player's id given the name... provided it's unique.
    """
    list_of_players = get_relevant_players(first, last, db_filename)

    if len(list_of_players) == 1:
        id_index = 0 # based on query in get_relevant_players
        return list_of_players[0][id_index]
    else:
        raise ValueError("This name does not appear uniquely in our database.")


def get_relevant_players(first, last, db_file):
    """
    Returns list of rows from "players" table with matching name.
    """
    db_connection = sqlite3.connect(db_file)
    db_cursor = db_connection.cursor()

    player_query = "SELECT id, first_name, last_name, birth_year FROM players WHERE first_name = ? AND last_name = ?;"
    db_cursor.execute(player_query, (first, last))
    return db_cursor.fetchall()


def print_relevant_players(first, last, db_file):
    list_of_players = get_relevant_players(first, last, db_file)
    for row in list_of_players:
        id, F, L, birth = row
        print(f"{F} {L} born {birth}. id: {id}")

    return

def set_of_relevant_players(first, last, db_file):
    list_of_players = get_relevant_players(first, last, db_file)
    s = set()
    for row in list_of_players:
        s.add( row[0] )
    return s


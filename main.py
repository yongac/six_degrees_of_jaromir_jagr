# Main .py file for this project.

import database
import helpers
import graph_operations

def main():
    """
    Executes all steps of the project:
    0. Set up: ensure database ready, user input is valid.
    1. Checks if "bfs_parent" table in the data base (and constructs if isn't)
    2. Call "traverse_bfs_path()" to get distance to Jagr and sequence of teammates + common teams
    3. Print the resulting path data in human-readable form.
    """

    ### Step 0: Set-up

    # Declare which database file to construct
    db_file = "1980_to_2025.db"  # got an error 2025/03/06 when scraping for 45 years of data.
    #db_file = "auto.db"

    # Specify CSV file for meta data used to make database (teams, years)
    team_names_csv = "team_info/small_names.csv"  
    team_seasons_csv = "team_info/small_seasons.csv" 
    # team_names_csv = "team_info/tiny_names.csv"
    # team_seasons_csv = "team_info/tiny_seasons.csv"

    # Ensure the tables have been initialized: 
    database.set_up_db(db_file)  
    EXPECTED_NUM_PLAYERS = 200
    num_players = len(database.get_all_players(db_file))
    if num_players < EXPECTED_NUM_PLAYERS:
        # Only bother constructing the database if it appears incomplete.
        # We use "completeness" proxy of checking it has "enough" players.
        database.add_to_database(db_file, team_names_csv, team_seasons_csv)
    
    num_players = len(database.get_all_players(db_file)) # reset the number of players after adding

    # Get and Validate User Input
    player_id = False
    while not player_id:
        first, last, player_id = helpers.get_and_validate_user_input(db_file)

    # Prepare the "teammates" table:
    database.make_teammates_table(db_file)

    ## Step 1: Check that the table for BFS parents is ready, or make it.
    num_rows = database.check_bfs_parent_ready(db_file)
    if num_rows < num_players:
        # Do BFS and make the bfs_parent table.
        bfs_parent_dict = graph_operations.BFS(db_file, root='jagrja01')
        database.make_BFS_parent_table(bfs_parent_dict, db_file)

    ## Step 2:  Call "traverse_bfs_path()" to get distance to Jagr and sequence of teammates + common teams
    distance, result = graph_operations.traverse_bfs_path( player_id, db_file, root='jagrja01')

    ## Step 3: Print the result:
    print(f"\n{first} {last}'s distance to Jagr = {distance}:")
    print(result, '\n')
    return distance


if __name__ == "__main__":
    main()

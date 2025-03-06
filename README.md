# Six Degrees of Jaromir Jagr

This repository contains a CLI program that finds the shortest sequence of teammates from NHL legend [Jaromir Jagr](https://en.wikipedia.org/wiki/Jarom%C3%ADr_J%C3%A1gr) to a user-selected NHL player. 

**Purpose:** This project is meant to be a learning exercise, with the aim of practicing some project-specific skills (scraping data from the internet, using SQL databases) as well as more general software development skills (organizing a public-facing project and version controlling it with Git). 

<br>

**Note:** This iteration shows that the main logic of the program works, from scraping data to building a database file and then to processing that data and computing shortest paths. 

Other issues and future improvements are discussed at the bottom of this file, just before the Acknowledgments section. 

## Usage:

1. Fork and clone this repository.
2. Set up your Python 3 environment to meet the specifications in either `environment.yml` or `requirements.txt` 
3. (Optionally, scrape the data) In this iteration, I'm providing a (*limited*) database file that can be used right away, without the need for the scraping step (which is slow, due to rate limiting described below).
4. Run `python3 main.py`, and follow the prompts for further input.

<br> 

*Note:* The database included currently only has player/team data from the 1980-1981 NHL season onward to 2025/03/06. If you want more/less data to this database, change the parameters/meta data in `team_names.csv` and/or `team_seasons.csv`. However, the scraping process will take minutes or hours, since Hockey-Reference rate limits bot traffic to 20 requests per minute. So, expect a single roster (team in a given year) to take approximately 3 seconds. 


## Organization

In this iteration, the project is organized as follows:

```
|-- README.md
|-- environment.yml
|-- requirements.txt
|-- main.py               # the file to actually run.
|-- database.py           # code to interact with the database
|-- scraper.py            # scraping roster data from Hockey Reference
|-- graph_operations.py   # BFS functionality
|-- helpers.py            
|-- team_info/            # CSVs containing meta data for scraping
|   |-- team_names.csv    # for converting team_ids to full team names
|   |-- team_seasons.csv  # tells which season-range to scrape data for
|   |-- ...               # smaller (test) versions of the 2 CSVs above. 
|-- 1980_to_2025.db       # sqlite3 database built using database.py + CSVs above
```

## Design

1. We set up a SQLite3 database and populate it with player, team, and other data. In this iteration, this is done by scraping many pages of roster data from Hockey-Reference.

2. After building a table of teammates, we check if tables for breadth-first search (BFS) logic have been constructed. They are constructed only once (or periodically) to amortize the cost of BFS across many calls to the function.

3. If the BFS-relevant tables haven't been built, we construct them:
    - We build a teammates graph in memory, represented as an adjacency list (dict of lists of teammates), with nodes indexed by player ids and edges inserted acc. to a teammates table.
    - We do BFS rooted at Jagr's node, recording BFS parent-children relationships in a dict
    - The dict mapping a player to their BFS parent is used to build a corresponding table in the DB

4. User input is received, validated, and the player's id is extracted and passed to the next part.

5. We trace a path from the input player's id to Jagr's id by traversing child-to-parent in the BFS parent table, storing all results.

6. We use queries to record the player names and common teams along this path, and print the result.


## Issues and Future Improvements

#### Populating the database

In this iteration of the project, the database is populated by scraping Hockey-Reference for rosters of given teams and years (as specified in the CSV files within `team_info/`).

#### Validating player data

At present, roster data is collected from Hockey Reference and is not manually verified. Some errors can be found in that data (e.g. the id, birth year, etc., of one player may be used for another player with the same name).

#### Validating whether supposed teammates actually played together

One oversight in this code is that is uses roster membership to decide whether players should be considered teammates: if two players appear on the same roster in any given year, they are assumed to have played together and thus be teammates. This is not a valid assumption (for instance, they may have been traded for one another during the season, and thus appear on *two* rosters together, despite never having played together).

Thus, a player may actually be farther from Jagr than this program suggests. A future improvement would be to collect data about line-ups from individual games, which would then be used to build a teammates table free of this issue.

#### Efficiency

At present, we use the teammates database to construct a graph of teammates, with player ids labelling nodes and edges between teammates, and this graph is stored in memory. This seems to not be an issue with NHL player data, since there have only ever been about 8,000 NHL players across history and the average number of (NHL) teammates is one or two orders of magnitude smaller, meaning the graph isn't too big. But, a more efficient implementation may be possible. 

Other efficiency issues: very likely, the SQL queries could be re-written and optimized. 


#### Updating the interface

A nicer interface (e.g. web-app) is another obvious improvement.


#### Re-constructing the database

If the app is going to be used several times in a short time interval, the database only needs to be prepared once. However, for more up-to-date information (e.g. after trades or the start of a new season), you may want to re-build your database.

The code currently only builds the database by checking whether the number of rows in the teammates data set exceeds some threshold quantity. This is an inelegant stopgap solution that should probably be automated, which I hope to do later.


#### Shortest paths between any pair of players

Once the teammates graph is in memory, we can easily find the shortest path from any given player to any other using breadth-first search rooted at one of those two players. In the case with a fixed root (namely, Jagr), I cached BFS information in a table, where each player is mapped to the player who discovered them in BFS, allowing us to trace a path back to the fixed root. With a single fixed root, we only need one such table, and the cost of BFS can be amortized across many calls to the main function. On the other hand, I have not thought about the specific implementation of rapidly serving requests in the setting without a fixed root. 


## Acknowledgments

This project has relied on the data provided by [Hockey Reference](https://www.hockey-reference.com), and this project was conducting in accordance with [their terms of use.](https://www.sports-reference.com/data_use.html)
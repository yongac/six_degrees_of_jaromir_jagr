# Six Degrees of Jaromir Jagr

This repository contains a CLI program that finds the shortest sequence of teammates from Jaromir Jagr to a user-selected NHL player. 

**Purpose:** This project is meant to be a learning exercise, with the aim of practicing some project-specific skills (scraping data from the internet, using SQL databases) as well as more general software development skills (organizing a public-facing project and version controlling it with Git). 

**Note: this project is <font color='red'>under construction</font>!** 

(2025/03/04) In this (second) iteration, the data used is very limited -- consisting of just a few rosters and totalling around 200 players (and considering only a small part of their careers). In addition to showing that the main functionality works as intended, the aim of this version is to show that we can build our database from CSV files.

Other issues and future improvements are discussed at the bottom of this file, just before the Acknowledgments section. 

## Usage:

1. Ensure you have Python 3 installed (tested with both 3.8.20 and 3.12.8). The only packages used so far are in the standard library.
2. Clone this repository.
3. Run `python3 main.py`, and follow the prompts for further input.

## Organization

In this initial iteration, the project is organized as follows:

```
|-- README.md
|-- main.py             # the file to actually run.
|-- database.py         # code to interact with the database
|-- graph_operations.py # helpers for BFS functionality
|-- helpers.py          # misc helper functions to de-clutter main.py
|-- data.db             # sqlite DB of player, team, and other required data
|-- manual_csv_data/    # folder containing copy-pasted CSV data for a handful of rosters.
|   |-- mtl2006.csv
|   |-- mtl2016.csv
|   |-- ott2015.csv
|   |-- pit1991.csv
|   |-- pit1999.csv
|   |-- veg2020.csv
|-- semiauto.db         # a sqlite3 database constructed by database.py using the CSVs above
```

*Note:* the database file `semiauto.db` is only constructed using the CSV files of `manual_csv_data/` in this early iteration of the project. It will be replaced in future iterations, described further below.

## Design

1. We set up a SQLite3 database and populate it with player, team, and other data.
    * The amount of data entered will greatly increase with each iteration of the project.
    * (Previouly) In Stage 0, it is populated manually (from a text file) with limited data points.
    * (Currently) In Stage 1, several CSV files are manually prepared and then automatically fed to the database.
    * (Forthcoming) In Stage 2, the CSV generation is done by a script.

2. After building a table of teammates, we check if tables for BFS logic have been constructed. They are constructed only once (or periodically) to amortize the cost of BFS across many calls to the function.

3. If the BFS-relevant tables haven't been built, we construct them:
    - We build a teammates graph in memory, represented as an adjacency list (dict of lists of teammates), with nodes indexed by player ids and edges inserted acc. to a teammates table.
    - We do BFS rooted at Jagr's node, recording BFS parent-children relationships in a dict
    - The dict mapping a player to their BFS parent is used to build a corresponding table in the DB

4. User input is received, validated, and the player's id is extracted and passed to the next part.

5. We trace a path from the input player's id to Jagr's id by traversing child-to-parent in the BFS parent table, storing all results.

6. We use queries to record the player names and common teams along this path, and print the result.


## Issues and Future Improvements

#### Populating the database

In this iteration of the project, the database is populated manually by producing CSV files of rosters for a given team and year (copied and pasted from Hockey Reference), storing many of these in a separate `manual_csv_data/` folder, and writing python script to ingest these to populate the database.
   * Unless you want to manually produce 1000s of CSVs, this will still yield an incomplete database.

In the next iteration of the project, we will write a .py file that scrapes the relevant table data and directly adds each table to the database.

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
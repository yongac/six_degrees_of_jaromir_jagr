# Six Degrees of Jaromir Jagr

This repository contains a CLI program that finds the shortest sequence of teammates from Jaromir Jagr to a user-selected NHL player. 

**Purpose:** This project is meant to be a learning exercise, with the aim of practicing some project-specific skills (scraping data from the internet, using SQL databases) as well as more general software development skills (organizing a public-facing project and version controlling it with Git). 

<style>
    .red{
        color:#ff0000;
        background-color:transparent;
    }
</style>

## <div class="red">Under Construction!</div>

This project is currently under construction. In this initial iteration, the data used is extremely (cartoonishly) limited -- consisting of just a few players and a tiny subset of their career information. The logic of the program is internally consistent, and this initial phase of the project showcases that the various parts of the code work together as intended. 

Other issues and future improvements are discussed at the bottom of this file, just before the Acknowledgments section. 

## Requirements:

Python 3 (tested with 3.12.8)
- packages used (sqlite3, os, collections, unicodedata) are all included in python's standard library.

## Organization

Coming soon. 

## Issues and Future Improvements

### Validating player data

At present, roster data is collected from Hockey Reference and is not manually verified. Some errors can be found in that data (e.g. the id, birth year, etc., of one player may be used for another player with the same name).

### Validating teammates played together

One oversight in this code is that is uses roster membership to decide whether players should be considered teammates: if two players appear on the same roster in any given year, they are assumed to have played together and thus be teammates. This is not a valid assumption (for instance, they may have been traded for one another during the season, and thus appear on *two* rosters together, despite never having played together).

Thus, a player may actually be farther from Jagr than this program suggests. A future improvement would be to collect data about line-ups from individual games, which would then be used to build a teammates table free of this issue.

### Efficiency

At present, we use the teammates database to construct a graph of teammates, with player ids labelling nodes and edges between teammates, and this graph is stored in memory. This seems to not be an issue with NHL player data, since there have only ever been about 8,000 NHL players across history and the average number of (NHL) teammates is one or two orders of magnitude smaller, meaning the graph isn't too big. But, a more efficient implementation may be possible. 

Other efficiency issues: very likely, the SQL queries could be re-written and optimized. 


### Updating the interface

A nicer interface (e.g. web-app) is another obvious improvement.


### Re-constructing the database

If the app is going to be used several times in a short time interval, the database only needs to be prepared once. However, for more up-to-date information (e.g. after trades or the start of a new season), you may want to re-build your database.

The code currently only builds the database by checking whether the number of rows in the teammates data set exceeds some threshold quantity. This is an inelegant stopgap solution that should probably be automated, which I hope to do later.


### Shortest paths between any pair of players

Once the teammates graph is in memory, we can easily find the shortest path from any given player to any other using breadth-first search rooted at one of those two players. In the case with a fixed root (namely, Jagr), I cached BFS information in a table, where each player is mapped to the player who discovered them in BFS, allowing us to trace a path back to the fixed root. With a single fixed root, we only need one such table, and the cost of BFS can be amortized across many calls to the main function. On the other hand, I have not thought about the specific implementation of rapidly serving requests in the setting without a fixed root. 


## Acknowledgments

This project has relied on the data provided by [Hockey Reference](https://www.hockey-reference.com), and this project was conducting in accordance with [their terms of use.](https://www.sports-reference.com/data_use.html)
# Overview
Welcome to the Jedi Master, the automated assistant moderator for the Stanford A Capella Jedi Council Meeting!

The goal of this program is to improve the efficiency of the existing Jedi Council meeting structure by automating some of the bookkeeping and allowing every group to enter their preferences at once.

# Installation and Running
To install Jedi Master, clone the code into some local directory, then navigate to the static folder and run `npm install`.

Then, to run the code, run app.py with python 3.

## Dependencies
javascript dependencies: Bootstrap, JQuery, Dragula, and Select2

python dependencies: Flask, Sqlite

# Program Structure

The meeting proceeds in rounds until all candidates are resolved.

## Group Interface

In each round, each group is presented with five lists:
1. Committed: these are resolved candidates who will join your group.
2. Unavailable: these are resolved candidates who will NOT join your group.
3. Claims: these are unresolved candidates who you attempted to claim last round.
4. Holds: these are unresolved candidates on which you have placed a hold.
5. Available: these are unresolved candidates which you are not claiming or holding

In each round, each group may freely move candidates between the Claims, Holds, and Avaialble lists.
This allows for human operators to handle the existing selection logic, limiting the scope of the application and reducing the need for time consuming data entry.

When you are satisfied with your claims and holds, press the "Ready" button in the top right to save your claims and holds to the server.

When the moderator ends a round, readied clients will automatically refresh the candidate listing information.

There is also a "Refresh" button provided in the top left to refresh the candidate listing information at any time.

When all candidates are resolved, the "Ready" button will be replaced with a "Download Results" button, which will generate a spreadsheet with all the candidates who will join your group.

## Moderator Interface

The moderator will see a list of all the groups with an indicator of whether they are ready or not. It is recommended to wait to end a round until all groups are ready.

There is a "Do Round" button provided in the center of the screen to end the round, resolving candidates automatically according to their preferences and the claims and holds from each group.

When all candidates are resolved, the "Do Round" button will be replaced with a "Download Results" button, which will generate a spreadsheet with all the candidate assignments.

If a need arises for manual intervention from the moderator, there is a "Manually Assign Candidates" button provided, which allows the moderator to assign candidates to any group at any time. The Group Client will not automatically detect these manual changes, so it is advised to request that all group representatives refresh to fetch the new information.




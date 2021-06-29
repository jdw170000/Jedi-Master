Welcome to the Jedi Master, the automated assistant moderator for the Stanford A Capella Jedi Council Meeting!

The goal of this program is to improve the efficiency of the existing Jedi Council meeting structure by automating some of the bookkeeping and allowing every group to enter their preferences at once.

#Program Structure

The meeting proceeds in rounds until all candidates are resolved.
In each round, each group is presented with four lists:
1. Successful claims: these are resolved candidates who will join your group.
2. Failed claims: these are resolved candidates who will NOT join your group.
3. Pending claims: these are unresolved candidates who you attempted to claim last round.
4. Holds: these are unresolved candidates on which you have placed a hold.

Each group may update the "pending claims" and "holds" lists in reaction to the success and fail information.
This allows for human operators to handle the existing selection logic, limiting the scope of the application and reducing the need for time consuming data entry.

#Development checklist
1. Round logic: accept pending claims and holds from all groups and return the updated result lists.
2. Backend Network Interface: connect client devices to the moderator's machine to allow for distributed input.
3. User Interface: allow users to intuitively read and modify their round lists
4. Configuration: read the google forms file that contains the candidates and their preference lists

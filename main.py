# Minefield Problem main
# Written by: Joshua Cutting
# Dependent on Path.py (OOP usage to manage pathway data)
# Goal: Reach the end of the minefield... only one path needs to arrive!
#       Give output as a single string inputted into their site within 7 seconds
# Current Expected Output:
#       The minefield in 0s and Xs. 0s are blank and Xs are bombs
#       The successful path as a correctly formatted string
#       The html code of the response from our guess
from lxml import html
import requests
import time
from array import *


# Defines a Path object to be used later on
# Paths keep track of their position in the maze, their route, and previouos stops

class Path:

    def __init__(self, currentx, currenty, pathway, prevspaces):
        self.pathway = pathway
        self.currentx = currentx
        self.currenty = currenty
        self.prevspaces = prevspaces


# canMove determines if a path could be

def canMove(mazestartx, mazestarty, mazegoalx, mazegoaly, newx, newy, prevspaces):
    newspace = [newx, newy]
    return (mazestartx <= newx <= mazegoalx) and (mazestarty <= newy <= mazegoaly) and newspace not in prevspaces


def main():
    # testing performance
    t0 = time.time()

    mazesizex = 22
    mazesizey = 22
    mazestartx = 0
    mazestarty = 0
    mazegoalx = 21
    mazegoaly = 21
    # Creation of the Paths coordinate grid to keep track of all Path objects

    paths = []

    maze = []
    bombloc = []

    successfulpath = ""

    # The following creates a PERSISTANT session on the site, gets the html table data, and then converts it into a
    # 1D array
    s = requests.Session()
    # This line makes the intitial request so we can get the minefield
    page = s.post('https://pg-0451682683.fs-playground.com/#')

    # These lines convert the html into a tree and then finds the html table
    # The html table is sorted and every "full" or "empty" value is extracted from every "<td>" tag
    tree = html.fromstring(page.content)
    slots = tree.xpath('//td/@class')

    # Converting the 1D array into the 2D array
    for x in range(mazestartx, mazesizex):
        newrow = []
        for y in range(mazestarty, mazesizey):
            newrow.append(slots[y + (mazesizex * x)])
        maze.append(newrow)

    # prints out the maze... lookin decent =D

    for x in range(0, len(maze)):
        for y in range(0, len(maze)):
            if (maze[x][y] == "empty"):
                print("0 ", end='')
            else:
                print("X ", end='')
        print(" ")

    # creates list of locations where bombs exist... intend to use this to simplify elimination by bomb later on
    for x in range(mazestartx, mazesizex):
        for y in range(mazestarty, mazesizey):
            if maze[x][y] == "full":
                loc = [x, y]
                bombloc.append(loc)

    # Creation of the original path starting at point 0,0
    firstpath = Path(mazestartx, mazestarty, "", [])

    paths.append(firstpath)

    successful = False

    # start to cycle through paths in order to move all paths one space
    # after finding all new paths, flush old paths and replace with new ones
    while not successful:
        newpaths = []
        for path in paths:

            # Tries to move up
            if canMove(mazestartx, mazestarty, mazegoalx, mazegoaly, path.currentx - 1, path.currenty, path.prevspaces):
                temppathway = path.pathway
                temppathway += "U"
                tempprevspaces = []
                for space in path.prevspaces:
                    tempprevspaces.append(space)
                newspace = [path.currentx - 1, path.currenty]
                tempprevspaces.append(newspace)

                temppath = Path(path.currentx - 1, path.currenty, temppathway, tempprevspaces)
                newpaths.append(temppath)
            # Tries to move down
            if canMove(mazestartx, mazestarty, mazegoalx, mazegoaly, path.currentx + 1, path.currenty, path.prevspaces):
                temppathway = path.pathway
                temppathway += "D"
                tempprevspaces = []
                for space in path.prevspaces:
                    tempprevspaces.append(space)
                newspace = [path.currentx + 1, path.currenty]
                tempprevspaces.append(newspace)

                temppath = Path(path.currentx + 1, path.currenty, temppathway, tempprevspaces)
                newpaths.append(temppath)
            # Tries to move left
            if canMove(mazestartx, mazestarty, mazegoalx, mazegoaly, path.currentx, path.currenty - 1, path.prevspaces):
                temppathway = path.pathway
                temppathway += "L"
                tempprevspaces = []
                for space in path.prevspaces:
                    tempprevspaces.append(space)
                newspace = [path.currentx, path.currenty - 1]
                tempprevspaces.append(newspace)

                temppath = Path(path.currentx, path.currenty - 1, temppathway, tempprevspaces)
                newpaths.append(temppath)
            # Tries to move right
            if canMove(mazestartx, mazestarty, mazegoalx, mazegoaly, path.currentx, path.currenty + 1, path.prevspaces):
                temppathway = path.pathway
                temppathway += "R"
                tempprevspaces = []
                for space in path.prevspaces:
                    tempprevspaces.append(space)
                newspace = [path.currentx, path.currenty + 1]
                tempprevspaces.append(newspace)

                temppath = Path(path.currentx, path.currenty + 1, temppathway, tempprevspaces)
                newpaths.append(temppath)

        # flushes old paths and then inserts new paths
        paths.clear()
        for path in newpaths:
            paths.append(path)
            # print(str(path.currentx)+" : "+str(path.currenty))
        newpaths.clear()
        # Elimination based on conflicting paths AND bombs
        for x in range(mazestartx, mazesizex):
            for y in range(mazestarty, mazesizey):
                for path in paths:
                    # first if checks for a bomb... if it is, we don't need to check any other paths in this loc,
                    #   because they must all be bad
                    # then if there is NOT a bomb, it checks if it belongs to this location, if it does
                    #   then it saves it and eliminates all other locations within this spot since we only need one
                    currentloc = [path.currentx, path.currenty]
                    if currentloc in bombloc:
                        continue
                    elif path.currentx == x and path.currenty == y:
                        newpaths.append(path)
                        break

        # cycles newpaths back into paths again
        paths.clear()
        for path in newpaths:
            paths.append(path)
            # (str(path.currentx)+" : "+str(path.currenty))
        newpaths.clear()

        # Check for success from paths
        # NOTE: only ONE path needs to be successful for a win!

        for path in paths:
            if path.currentx == mazegoalx and path.currenty == mazegoaly:
                successfulpath = path.pathway
                successful = True
                break

    # reporting results
    print("successful path: " + successfulpath)

    # submitting the pathway found:
    # notice request is made with the "s" Session object made earlier... we have to do that so the session is
    # persistent and the maze we initialized still is being used
    url = 'https://pg-0451682683.fs-playground.com/Solution/Submit?solution=' + successfulpath
    answerresponse = s.post(url)
    # prints out the html code of the response website... inspecting this shows if we win or not
    print(answerresponse.text)

    # end time
    t1 = time.time()
    print("Time taken: " + str(t1 - t0))


if __name__ == '__main__':
    main()

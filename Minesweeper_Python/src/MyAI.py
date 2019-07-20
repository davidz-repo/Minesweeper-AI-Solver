# ==============================CS-271P==================================
# FILE:			MyAI.py
#
# AUTHOR: 		David Zhang
#
# DESCRIPTION:  This file contain the core algorithm to solve the game
#               Refer below at getAction(self, number: int) for details
# ==============================CS-271P==================================

from AI import AI
from Action import Action
from collections import deque
from collections import Counter

import random

class MyAI( AI ):

    # Tile class
    class __Tile():
        """ create templates for each tile on the board for knowledge base """
        mine = False # if the tile is a mine
        covered = True # if the tile is covered
        flag = False # is the tile flagged
        number = -100 # what is the percept number

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        # get map dimensions, number of mines, and coveredTiles
        self.row = rowDimension
        self.col = colDimension
        self.totalMines = totalMines
        self.coveredTiles = rowDimension * colDimension
        # moves
        self.movesMade = 1
        self.movesLimit = 0
        # lastTile is self.board[c][r] instance
        self.cLast = startX
        self.rLast = startY
        self.lastTile = None
        # lastAction is an action number
        self.lastAction = None
        self.flagsLeft = totalMines
        # first move coordinates
        self.startX = startX
        self.startY = startY
        # create a queue for safe Tiles
        self.safeQ = deque([])
        self.unknown = [(j, i) for i in range(self.row) for j in range(self.col)]
        self.prob = dict()
        self.mines = []
        self.minesLeft = totalMines
        # the world
        self.board = None
        # create the board
        self.__createBoard()
        # since the first move is made, update on the agent's KB
        self.__updateFirstMove()


    def getAction(self, number: int) -> "Action Object":
        """ input: an integer number as a perceptnumber from World.py act as a
            hint output: action number, rowCoordinate x, columnCoordinate y

            Total of 5 parts:

                I: Patient 0
                 - Uncover all the surrounding tiles if the center tile is 0

                II: Basic 3x3 deductions
                 - If the number of covered surrending tiles is qual to the percept
                   number for the center tile, then the covered tiles are mines

                III: Multisquare algorithm
                 - Looking at each single tile in the frontier (tiles that are
                   unexplored by adjcent to a percept number), expand the deduction
                   method from part II to multiple surrounding neighbors that have
                   multural affecting tiles.

                IV: Linear algebra
                 - Looking at the entier frontier and simplify it into a matrix. Use
                   the uncovered neighbor tiles' percept number as constraints. Each
                   constraint tells the max possible number of mines among its
                   surrounding tiles. Also, use the entire board's unexplored Tiles
                   and mines left as the final equation in the matrix. Solve or
                   reduce the matrix into row echelon form. Since each tile can
                   either be a mine or not, further deduction can be made.

                V: Guesses
                 - Assign each unexplored tiles a probability based on the current
                   knowledge base (number of minesleft and surrouding constraints)
                   One exception - guess corners first since the probability that
                   a corner being a mines is low. """

        # in the beginning, update KB with the received percept number
        self.logLastMovePercept(number)

        """ Part I - Patient 0 """
        # if the number is 0, then the last tile's surrounding is safe
        if (number == 0):
            """ if in bounds, not the last move,
                not already in safeQ, and covered"""
            for col in range(self.cLast-1, self.cLast+2):
                for row in range(self.rLast-1, self.rLast+2):
                    if (self.__isInBounds(col, row) and \
                          not (col == self.cLast and row == self.rLast)) and \
                          ((col, row) not in self.safeQ) and \
                          self.board[col][row].covered == True:
                        # add to the safeQ
                        self.safeQ.append((col, row))
        # uncover all the safe ones
        while (self.safeQ != deque([])):
            # get the left most tile in the safe queue
            cr = self.safeQ.popleft()
            # update the knowledge base
            self.logMove(AI.Action(1), cr[0], cr[1])
            # return the action to the World
            return Action(AI.Action(1), cr[0], cr[1])

        """ Part II - Basic 3x3 deductions """
        # locate the mine
        for col in range(0, self.col):
            for row in range(0, self.row):
                """ If the total number of covered surrending the tile
                        is the percept number for the tile,
                    then the covered tile is the mine """
                if (self.board[col][row].covered == False and \
                     self.board[col][row].number != 0 and \
                     self.board[col][row].number == \
                       self.surCovered(col, row)[0]):
                    # flag those as mines
                    mines = self.surCovered(col, row)[1]
                    for _ in mines:
                        self.markMines(_)
        for col in range(0, self.col):
            for row in range(0, self.row):
                # percept == known mines
                # surrounding unexplored - known mines > 0
                if ((self.board[col][row].number == \
                      self.surMines(col, row)[0]) and \
                     (self.surCovered(col, row)[0] - \
                      self.surMines(col, row)[0] > 0)):
                    # get the unexplored tiles and known mines
                    covered = self.surCovered(col, row)[1]
                    mines = self.surMines(col, row)[1]
                    for _ in covered:
                        # if the mines are all discovered, the rest of the tiles
                        # must be safe
                        if (_ not in mines) and (_ not in self.safeQ):
                            self.safeQ.append(_)
        # uncover all the safe ones
        while (self.safeQ != deque([])):
            # get the left most tile in the safe queue
            cr = self.safeQ.popleft()
            # update the knowledge base
            self.logMove(AI.Action(1), cr[0], cr[1])
            # return the action to the World
            return Action(AI.Action(1), cr[0], cr[1])

        """ Part III: neighbor_test (multisquare algorithm) """
        for col in range(self.col):
            for row in range(self.row):
                if self.board[col][row].number > 0 and \
                    self.surUnknown(col, row)[0] > 0:
                    neigh = self.neighbor_test(col, row)
                    if neigh is not None and neigh != []:
                        for _ in neigh:
                            if _ in self.unknown and _ not in self.safeQ:
                                self.safeQ.append(_)

        # uncover all the safe ones
        while (self.safeQ != deque([])):
            # get the left most tile in the safe queue
            cr = self.safeQ.popleft()
            # update the knowledge base
            self.logMove(AI.Action(1), cr[0], cr[1])
            # return the action to the World
            return Action(AI.Action(1), cr[0], cr[1])
		
        """ Part IV: linear algebra """
        # initialize contraints, frontier, and frontier encoding for the matrix
        constraints = []
        frontier = []
        frontierMap = dict()
        unknown = self.unknown
        totalMinesLeft = self.minesLeft

        # get the current contraints
        constraints = self.constraints()
        constraintsCount = len(constraints)

        # get the current frontier
        frontier = self.frontier()
        frontierCount = len(frontier)

        # each row is a contraint
        # the additional constraint is the entire unexplored tiles
        rowCount = constraintsCount + 1
        # each column is an explored tile on the board
        columnCount = len(unknown) + 1

        # if there are constraints and the variables, construct the matrix
        if columnCount != 1 and rowCount != 1:
            # create a list of column code for each variable tile plus the
            # general rule (unexplored tiles and total mines left)
            columnHeader = [x for x in range(columnCount)]
            frontierHeader = columnHeader[:-1]
            # encode each tile into a dictionary
            col_to_tile = dict(zip(frontierHeader, unknown))
            tile_to_col = dict(zip(unknown, frontierHeader))

            # initialize the matrix
            matrix = [[0 for i in range(columnCount)] for j in range(rowCount)]

            # construct the matrix
            row = 0
            for constraint in constraints:
                # list out the tiles to be explored for each constraint
                sub_frontier = self.surUnknown(constraint[0], constraint[1])[1]
                # mark the coordinates
                for tile in sub_frontier:
                    # encode each column into tile coordinates
                    col = tile_to_col.get(tile)
                    # update the matrix coordinate value
                    matrix[row][col] = 1
                # update the last column with the actual number of mines
                # which is (percept - number of mines already discovered)
                minesCount = self.board[constraint[0]][constraint[1]].number - \
                             self.surMines(constraint[0], constraint[1])[0]
                # update the last number as the effective percept number
                matrix[row][-1] = minesCount
                # move on to the next row
                row += 1

            # update the last row as the general rule
            for i in range(columnCount):
                matrix[row][i] = 1
            matrix[-1][-1] = totalMinesLeft

            # reduce to row echelon form, where the magic happens
            self.reduceRowEchelon(matrix)

            """
            Since each tile is either a mine or not, its value is binary. this
            is useful to solve the matrix or at least some tile's value.
            """
            safe = []
            mines = []
            for row in matrix:
                last = row[-1]
                onesCount = self.countMix(row[:-1])[0]
                onesList = self.countMix(row[:-1])[1]
                neg_onesCount = self.countMix(row[:-1])[2]
                negList = self.countMix(row[:-1])[3]

                # case when the total number of mines is 0
                if last == 0:
                    # case when there are only possitive coefficients on the left
                    if onesCount > 0 and neg_onesCount == 0:
                        for col in onesList:
                            tile = col_to_tile.get(col)
                            # they are safe
                            if tile not in safe:
                                safe.append(tile)
                    # case when there are only negative coefficients on the left
                    if neg_onesCount > 0 and onesCount == 0:
                        for col in negList:
                            tile = col_to_tile.get(col)
                            # they are mines
                            if tile not in mines:
                                mines.append(tile)
                # case when the total number of mines is possitive
                if last > 0:
                    # ignore the negative coefficients
                    if onesCount == last:
                        for col in onesList:
                            tile = col_to_tile.get(col)
                            if tile not in safe:
                                mines.append(tile)
                        for col in negList:
                            tile = col_to_tile.get(col)
                            if tile not in mines:
                                safe.append(tile)
                # case when the total number of mines is negative
                if last < 0:
                    # ignore the possitive coefficients
                    if neg_onesCount == last:
                        for col in onesList:
                            tile = col_to_tile.get(col)
                            if tile not in safe:
                                safe.append(tile)
                        for col in negList:
                            tile = col_to_tile.get(col)
                            if tile not in mines:
                                mines.append(tile)
            # update the knowledge base
            if mines != []:
                for _ in mines:
                    self.markMines(_)

            # update the knowledge base and append to the safe queue
            if safe != []:
                for _ in safe:
                    if _ in self.unknown and _ not in self.safeQ:
                        self.safeQ.append(_)

        # uncover all the safe ones
        while (self.safeQ != deque([])):
            # get the left most tile in the safe queue
            cr = self.safeQ.popleft()
            # update the knowledge base
            self.logMove(AI.Action(1), cr[0], cr[1])
            # return the action to the World
            return Action(AI.Action(1), cr[0], cr[1])

        """ Part V: Guesses """
        # assign heuristics to each tile: number of mines / number of unexplored
        if self.unknown != []:
            keys = self.unknown
            values = [self.minesLeft/len(self.unknown)]*len(self.unknown)
            self.prob = dict(zip(keys, values))
        for col in range(0, self.col):
            for row in range(0, self.row):
                percept = self.board[col][row].number
                num_mines = self.surMines(col, row)[0]
                num_covered = self.surCovered(col, row)[0]
                if ((percept > 0) and \
                    (num_covered - num_mines > 0)):
                    mines = self.surMines(col, row)[1]
                    covered = self.surCovered(col, row)[1]
                    for _ in covered:
                        if (_ not in mines) and (_ not in self.safeQ):
                            # only get the maximum probability of being a mine
                            self.prob[_] = max( ( percept-num_mines ) / \
                                                num_covered,\
                                           self.prob[_])

        # get the corners first
        corners = [(self.col-1, self.row-1), \
                    (0, 0), \
                    (self.col-1, 0), \
                    (0, self.row-1)]
        for _ in corners:
            if _ in self.unknown:
                self.prob[_] = self.prob[_]-1

        if (self.unknown != []):
            # only uncover the least possible mines
            minList = self.minList(self.prob)
            self.safeQ.append(random.choice(minList))
        if (self.minesLeft == 0):
            return Action(AI.Action(0))

        # uncover all the safe ones
        while (self.safeQ != deque([])):
            # get the left most tile in the safe queue
            cr = self.safeQ.popleft()
            # update the knowledge base
            self.logMove(AI.Action(1), cr[0], cr[1])
            # return the action to the World
            return Action(AI.Action(1), cr[0], cr[1])

        if (self.minesLeft == 0):
            return Action(AI.Action(0))

    ###########################################################################
    #                             organize movesMade                          #
    ###########################################################################
    def markMines(self, coord):
        """ update the KB if a mine is found """
        col = coord[0]
        row = coord[1]
        if (col, row) not in self.mines:
            self.minesLeft -= 1
            self.mines.append((col, row))
            self.board[col][row].mine = True
            self.board[col][row].flag = True
            self.unknown.remove((col, row))

    def logLastMovePercept(self, number):
        """ log the feedback percept number from the world """
        if self.lastAction == AI.Action(1):
            self.lastTile.covered = False
            self.lastTile.number = number

    def logMove(self, action, c, r):
        """ log the last move """
        self.cLast = c
        self.rLast = r
        self.lastTile = self.board[c][r]
        self.lastAction = action
        self.movesMade+=1
        self.unknown.remove((c, r))
        if (c, r) in list(self.prob.keys()):
            self.prob.pop((c, r))

    def __updateFirstMove(self) -> None:
        """ update the first move in KB"""
        c = self.startX
        r = self.startY
        self.unknown.remove((c, r))
        # self.safeQ.append([c, r])
        self.cLast = c
        self.rLast = r
        # update the 4 instances for this coordinates if necessary
        self.board[c][r].covered = False
        self.board[c][r].nubmer = 0
        # update lastTile instance
        self.lastTile = self.board[c][r]
        self.lastAction = AI.Action(1)

    ###########################################################################
    #                              print current board                        #
    ###########################################################################
    def __createBoard(self) -> None:
        """ create a board with given dimension and set moves limit"""
        self.board = [[self.__Tile() for i in range(self.row)] for j in range(self.col)]
        self.movesLimit = self.col * self.row * 2 - 1

    def __printWorld(self) -> None:
        """ Prints to console information about Minesweeper World """
        self.KB()
        self.__printAgentInfo()

    def KB(self) -> None:
        """ Print board for debugging """
        print("================================================================")
        print("================================================================")
        print("================== Agent's current knowledge base ==============")
        print("Number of mines: " + str(self.minesLeft))
        print("Number of flags left: " + str(self.flagsLeft))

        board_as_string = ""
        print("", end=" ")
        for r in range(self.row - 1, -1, -1):
            print(str(r).ljust(2) + '|', end=" ")
            for c in range(self.col):
                self.__printTileInfo(c, r)
            if (r != 0):
                print('\n', end=" ")

        column_label = "     "
        column_border = "   "
        for c in range(0, self.col):
            column_border += "---"
            column_label += str(c).ljust(3)
        print(board_as_string)
        print(column_border)
        print(column_label)
        print("================================================================")
        print("================================================================")
        print("================================================================")

    def __printAgentInfo(self) -> None:
        """ Prints information about the board that are useful to the user """
        print("Tiles covered: " + \
              str(self.coveredTiles) + \
              " | Flags left: " + \
              str(self.flagsLeft) + \
              " | Last action: {} on {}"\
              .format(self.lastAction, self.lastTile))

    def __printTileInfo(self, c: int, r: int) -> None:
        """ Checks tile attributes and prints accordingly """
        if not self.board[c][r].covered and self.board[c][r].mine:
            print('B ', end=" ")
        elif not self.board[c][r].covered:
            print(str(self.board[c][r].number) + ' ', end=" ")
        elif self.board[c][r].flag:
            print('? ', end=" ")
        elif self.board[c][r].covered:
            print('. ', end=" ")

    ###########################################################################
    #                             Tile information                            #
    ###########################################################################
    def __isInBounds(self, c: int, r: int) -> bool:
        """ Returns true if given coordinates are within the boundaries """
        if c < self.col and c >= 0 and \
           r < self.row and r >= 0:
            return True
        return False

    def frontier(self):
        """ Return a list of tiles to be explored / for gaussian elimination """
        frontier = []
        for _ in self.unknown:
            col = _[0]
            row = _[1]
            coord = (col, row)
            if ( len(self.surTiles(coord)) - self.surCovered(col, row)[0] > 0 ):
                frontier.append(_)
        return frontier

    def constraints(self):
        """ Return a list of tiles next to the frontier as constraints """
        constraints = []
        for col in range(self.col):
            for row in range(self.row):
                if self.board[col][row].number > 0 and \
                    self.surUnknown(col, row)[0] > 0:
                    constraints.append((col, row))
        return constraints

    def surTiles(self, coord):
        """ return a list of surrounding tiles' coordinates"""
        tiles = set()
        for c in range(coord[0]-1, coord[0]+2):
            for r in range(coord[1]-1, coord[1]+2):
                if self.__isInBounds(c, r) and (c, r) != coord:
                    tiles.add((c, r))
        return tiles

    def surUnknown(self, col, row):
        """ return the total number of tiles that are unknown """
        count = 0
        noFlag = []
        for c in range(col-1, col+2):
            for r in range(row-1, row+2):
                if self.__isInBounds(c, r) and (c, r) != (col, row):
                    if self.known((c,r)) == False:
                        count+=1
                        noFlag.append((c, r))
        return count, noFlag

    def surCovered(self, col, row):
        """ return the total number of covered tiles, and a list of coordinates
            of those covered tiles surrounding the input coords """
        count = 0
        covered = []
        for c in range(col-1, col+2):
            for r in range(row-1, row+2):
                if self.__isInBounds(c, r) and (c, r) != (col, row):
                    if self.board[c][r].covered == True:
                        count+=1
                        covered.append((c, r))
        return count, covered

    def surMines(self, col, row):
        """ return the number of mines, and a list of coordinates of those
            mines surrounding the input coords """
        count = 0
        s_mines = []
        for c in range(col-1, col+2):
            for r in range(row-1, row+2):
                if self.__isInBounds(c, r):
                    if self.board[c][r].mine == True:
                        self.board[c][r].flag = True
                        count+=1
                        s_mines.append((c, r))
        return count, s_mines

    def set_known(self, set):
        """ test if any of the tiles are unknown """
        for i in set:
            if self.known(i) == False:
                return False
        return True

    def known(self, coord):
        """ test if the tile is unknown (covered and not flagged) """
        if self.board[coord[0]][coord[1]].covered == True and \
             self.board[coord[0]][coord[1]].flag == False:
            return False
        return True

    ###########################################################################
    #                           Multisquare method                            #
    ###########################################################################
    def neighbor_test(self, col, row):
        """ return the number of wild tiles, and a list of safe tiles if any """
        safe = []
        center = (col, row)
        percept_center = self.board[col][row].number
        # neighbors = self.surTiles((col, row))

        neighbors_list = []
        for co in range(col-2, col+3):
            for ro in range(row-2, row+3):
                if self.__isInBounds(co, ro) == True and \
                     (co, ro) != (col, row):
                    neighbors_list.append((co, ro))
        neighbors = set(neighbors_list)

        for neighbor in neighbors:
            percept_neighbor = self.board[neighbor[0]][neighbor[1]].number

            if percept_neighbor < 1:
                # if the percept number of the neighbor is less than 1
                continue

            N = self.surTiles(neighbor)
            if center in N:
                # remove the center coords from the surrounding set
                N.remove(center)

            if self.set_known(N) == True:
                # if the surrounding tiles are all known, skip
                continue

            A = self.surTiles(center)
            if neighbor in A:
                A.remove(neighbor)

            both = A & N
            N_not_A = N.difference(A)
            A_not_N = A.difference(N)

            mines_A = set(self.surMines(center[0], center[1])[1])
            mines_N = set(self.surMines(neighbor[0], neighbor[1])[1])

            mines_both = mines_A.intersection(N)
            mines_A_not_N = mines_A.intersection(A_not_N)
            mines_N_not_A = mines_N.intersection(N_not_A)

            percept_both = len(mines_both)
            percept_A_not_N = len(mines_A_not_N)
            percept_N_not_A = len(mines_N_not_A)

            if self.set_known(N_not_A) == False:
                continue

            if percept_N_not_A == 0 and percept_both == 0:
                continue

            if (percept_center - percept_A_not_N) == \
                 (percept_neighbor - percept_N_not_A):
                for coord in A_not_N:
                    if self.known(coord) == False:
                        safe.append(coord)

        return safe

    ###########################################################################
    #                           Gaussian eliminations                         #
    ###########################################################################
    def reduceRowEchelon(self, matrix):
        """ https://rosettacode.org/wiki/Reduced_row_echelon_form# """
        j = 0
        row_num = len(matrix)
        column_num = len(matrix[0])
        for ro in range(row_num):
            if j >= column_num:
                return
            i = ro
            while matrix[i][j] == 0:
                i += 1
                if i == row_num:
                    i = ro
                    j += 1
                    if column_num == j:
                        return
            matrix[i], matrix[ro] = matrix[ro], matrix[i]
            level = matrix[ro][j]
            matrix[ro] = [ int(_ / level) for _ in matrix[ro]]
            for i in range(row_num):
                if i != ro:
                    level = matrix[i][j]
                    matrix[i] = [iv-level*rv for rv,iv in zip(matrix[ro],matrix[i])]
            j += 1

    def countMix(self, row):
        """ count coefficients of 1's and -1's in a row of the matrix """
        ones = 0
        neg_ones = 0
        onesList = []
        negList = []
        for _ in range(len(row)):
            if row[_] == 1:
                ones += 1
                onesList.append(_)
            if row[_] == -1:
                neg_ones += 1
                negList.append(_)
        return ones, onesList, neg_ones, negList
    ###########################################################################
    #                                Guessing GAME                            #
    ###########################################################################
    def minList(self, dict):
        minList = []
        # finding the lowest values for the list
        min = float("inf")
        for k, v in dict.items():
            if v == min:
                minList.append(k)
            if v < min:
                min = v
                minList = []
                minList.append(k)
        return minList

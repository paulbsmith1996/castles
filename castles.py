# Author: Paul Baird-Smith, 2017
# A simultor for a castles game that is played as follows:
#
# We are given castles labelled 1-n, and we say that the castle's
# label is its value. Two players present attack strategies given
# a fixed number of soldiers, deciding how many soldiers they want
# to send to every castle. Once the bets are compared, the player with
# the most soldiers at a castle wins that castle's points. For 4
# castles and 10 soldiers, this might look like:
#
#
#  Player 1's bets:   4   2   3   1
#  ----------------------------------
#  Castles:           1   2   3   4
#  ----------------------------------
#  Player 2's bets:   0   0   5   5
#
#
# In this case, Player 1 is assigned a score of 3, because the player
# won the castles labelled 1 and 2. Player 2 scores 7 for winning the
# other two castles and thus wins the game
#
# We investgiate different algorithms for reacting to an opponent's
# betting in this game.
#
# Copyright Baird-Smith 2017
# 

import random

class Game:
    
    # Initial conditions to determine number of castles to bet on and
    # number of betting "chips" or soldiers
    def __init__(self):
        # Set the number of soldiers available and number of castles to be fought for
        # Available data set from 538 github has 100 soldiers for 10 castles
        self.numCastles = 10
        self.numSoldiers = 100

        # Read in data set
        self.fp = FileParser("castle-solutions.csv", self)
        self.fp.readFile()

        # Create a new data set that can be manipulated by adding in more data points
        self.dataSetPlus = [selection for selection in self.fp.playerSelections]


        # Create a larger data set to train the PlayerBeater
        #dataSetLen = len(self.dataSetPlus)
        #for i in range(dataSetLen):
            #sel = self.dataSetPlus[i]
            #newSel = self.updateHorizontal(sel)
            #newSel = self.updateVertical(sel)
            #self.dataSetPlus.append(newSel)            

    # Determines which of two selections won the most points
    def compare(self, player1Sel, player2Sel):

        # Check that the selections are valid. Check number of castles proposed and
        # total number of soldiers used
        if len(player1Sel) > self.numCastles or len(player2Sel) > self.numCastles:
            print "ERROR: Invalid size of betting selections"
            return -1
        if sum(player1Sel) > self.numSoldiers or sum(player2Sel) > self.numSoldiers:
            print "ERROR: Invalid number of soldiers in selections"
            return -1


        # Determine which player wins each castle. If each player has 
        # attacked with the same number of soldiers, castle is won by
        # neither
        player1Score = 0
        player2Score = 0

        # Assign each castle score to either player 1 or player 2 depending on
        # number of soldiers on castle. If tied, neither player gets points
        for i in range(0, self.numCastles):
            if player1Sel[i] > player2Sel[i]:
                player1Score = player1Score + i + 1
            elif player2Sel[i] > player1Sel[i]:
                player2Score = player2Score + i + 1

        # Return tuple of scores
        return (player1Score, player2Score)
        
    # Returns a tuple of the number of wins, ties, and losses that playerSelection
    # achieves when comapred against every selection in dataSet
    def testSelection(self, playerSelection, dataSet):
        
        # Keep track of number of wins, ties, and losses
        playerWins = 0
        playerTies = 0
        playerLosses = 0

        # Loop through all selections
        for selection in dataSet:

            (s1, s2) = self.compare(playerSelection, selection)

            # Determine if given selection wins, draws, or loses
            if s1 > s2:
                playerWins = playerWins + 1
            elif s1 < s2:
                playerLosses = playerLosses + 1
            else:
                playerTies = playerTies + 1

                
        return (playerWins, playerTies, playerLosses)

    # Score-calculating function that takes a tuple of wins, ties, and losses
    # and assigns appropriate score (3pts for a win, 1 for a tie, 0 for a loss)
    def calcScore(self, wtl):
        return 3 * wtl[0] + wtl[1] 

    # Assign a new selection to the player
    def copySelection(self, selection):
        newSelection = []

        for soldiersAtCastle in selection:
            newSelection.append(soldiersAtCastle)

        return newSelection

    # Throw mass at the higher value castles
    def updateVertical(self, oppSelection):
        
        selection = self.copySelection(oppSelection)
        selectionLen = len(selection)

        # Get the index of the first non-zero bet made by opponent
        index = 0
        while (index < selectionLen - 1) and (selection[index] == 0):
            index = index + 1
        
        # Decrement the lowest bid and increment the bid on the highest value
        # castle. Preserves sum
        selection[index] = selection[index] - 1
        selection[selectionLen - 1] = selection[selectionLen - 1] + 1

        return selection

    # Remove mass from the highest value castle and spread over all castles
    def updateDown(self, oppSelection):

        selection = self.copySelection(oppSelection)
        selectionLen = len(selection)

        # Get bid on highest value castle and set bid to 0
        highestBidOn = selection[selectionLen - 1]
        selection[selectionLen - 1] = 0
        
        # Redistribute bid over all castles
        for i in range(highestBidOn):
            randPos = random.randrange(selectionLen)
            selection[randPos] = selection[randPos] + 1
        
            
        return selection

    # Throw mass at castles that are not occupied
    def updateHorizontal(self, oppSelection):

        selection = self.copySelection(oppSelection)
        selectionLen = len(selection)

        # Get the index of the first (lowest) castle with a non-zero bet made 
        # by opponent
        index = 0
        while (index < selectionLen - 1) and (selection[index] == 0):
            index = index + 1

        # Find all castles where bets were not made
        zeroBets = []
        for i in range(selectionLen):
            if selection[i] == 0:
                zeroBets.append(i)

        # Edge case where every castle is bet on
        if len(zeroBets) == 0:
            return oppSelection

        soldiersToDistribute = selection[index]
        selection[index] = 0

        # Redistribute soldiers to castles with no soldiers
        zIndex = 0
        while soldiersToDistribute > 0:
            curCastle = zeroBets[zIndex]
            selection[curCastle] = selection[curCastle] + 1

            zIndex = zIndex + 1
            if zIndex >= len(zeroBets):
                zIndex = 0

            soldiersToDistribute = soldiersToDistribute - 1

        return selection

    # Disregards move made by opponent and randomly creates new bet selection
    def updateRandom(self, oppSelection=None):

        # Very clsoe to creating a list of random numbers that sum to numSoldiers
        newSelection = [random.randrange(self.numSoldiers) for i in range(self.numCastles)]
        s = sum(newSelection)

        selection = [self.numSoldiers * i/s for i in newSelection]
        selectionLen = len(selection)

        # Need to fix some gaps due to possible rounding error in previous
        # list comprehension
        while sum(selection) != self.numSoldiers:
            index = random.randrange(selectionLen)
            selection[index] = selection[index] + 1

        return selection

    # Apply updateVertical() twice
    def updateVerticalWinner(self, oppSelection):
        selection = self.copySelection(oppSelection)

        newSelection = self.updateVertical(selection)

        self.updateVertical(newSelection)

        return selection

    # Bets 0 on the bottom half of the castles and bets the rest on top half
    def updateRandomPlus(self, oppSelection=None):

        selection = self.copySelection(oppSelection)
        selectionLen = len(selection)

        zeros = [0] * (selectionLen / 2)
        
        # Very clsoe to creating a list of random numbers that sum to numSoldiers
        newSelection = [random.randrange(self.numSoldiers) for i in range(self.numCastles / 2)]
        s = sum(newSelection)
        newSelection = [self.numSoldiers * i/s for i in newSelection]

        # Fix gaps due to possible rounding error in previous list comprehension
        while sum(newSelection) != self.game.numSoldiers:
            index = random.randrange(selectionLen / 2)
            newSelection[index] = newSelection[index] + 1

        selection = zeros + newSelection

        # Edge case where selectionLen / 2 rounded down
        while len(selection) != self.numCastles:
            self.selection = [0] + self.selection

        return self.selection

    # Mutates given selection slightly, by decrementing one bet and incrementing
    # another up to 10 times
    def mutate(self, oppSelection):

        selection = self.copySelection(oppSelection)
        selectionLen = len(selection)
        
        # Pick a a number in [1,..,10] for number of mutations
        numMutations = random.randrange(10)

        # Perform numMutations mutations
        for i in range(numMutations + 1):
            # Decrement one bid and increment another (these can be the same bid)
            randIndex1 = random.randrange(selectionLen)
            randIndex2 = random.randrange(selectionLen)
            
            castle1Sel = selection[randIndex1]
            castle2Sel = selection[randIndex2]
            
            if castle1Sel > 0:
                selection[randIndex1] = selection[randIndex1] - 1
                selection[randIndex2] = selection[randIndex2] + 1

        return selection


# Maintains a list of selections, ranked by their scores. Every time this list
# is updated, the top third of the list is maintained, another third is composed
# of mutants of the top third, and the final third is composed of random selections
class PlayerBeater:

    # Create list of players, using an instance of Game
    def __init__(self, game):
        self.game = game

        # Number of selections per generation
        self.numPlayers = 60

        self.players = []
        for i in range(self.numPlayers):
            player = game.updateRandom()
            self.players.append(player)


    # Function that wraps calcScore and testSelection conveniently
    def scorePlayer(self, player):
        return self.game.calcScore(self.game.testSelection(player, game.dataSetPlus))

    # Creates the next generation from the current one
    def update(self):
        
        # Create a list of betting selections and their corresponding scores for ranking
        playersAndScores = [(player, self.scorePlayer(player)) for player in self.players]
        
        # Do a bubble sort, but this needs to be rewritten ASAP
        for i in range(self.numPlayers):
            for j in range(self.numPlayers - 1):
                if playersAndScores[j][1] < playersAndScores[j + 1][1]:
                    temp = playersAndScores[j]
                    playersAndScores[j] = playersAndScores[j + 1]
                    playersAndScores[j + 1] = temp

        # Populate a new generation
        newPlayers = []

        # Create 3 new selections for every iteration: one original, one mutant,
        # and one random
        for index in range(self.numPlayers / 3):
            
            # Keep the selection from the preceding generation
            newPlayers.append(playersAndScores[index][0])

            # Create a random selection, for variety in the next generation
            randomPlayer = game.updateRandom()
            newPlayers.append(randomPlayer)
            
            # Create a mutant of the betting selection in the previous generation.
            mutant = game.mutate(playersAndScores[index][0])

            # Assure this mutant does not already exist in generation
            contained = True            
            while contained:
                playerIndex = 0
                # Loop through all bets in the given selection
                while playerIndex < len(newPlayers):
                    player = newPlayers[playerIndex]
                    # Determine if current player has same selection as mutant
                    # If it does, mutant is already contained in new generation
                    sameSel = True
                    selectionLen = len(player)
                    
                    for castleIndex in range(selectionLen):
                        if player[castleIndex] != mutant[castleIndex]:
                            sameSel = False

                    # Found a creature with the same selection
                    if sameSel:
                        break
                            
                    playerIndex = playerIndex + 1
                
                # Contained is false if every selection in the new generation iss
                # a different selection from the mutant (aka we reach the end of
                # our lsit without finding a match)
                contained = not (playerIndex == len(newPlayers))
                mutant = game.mutate(mutant)
            
            newPlayers.append(mutant)                

        self.players = newPlayers

# Reads in the given file and creates a list of betting selections from the data
class FileParser:

    # Initialize file name and an empty list of selections. An instance of game is
    # needed to determine the number of castles used in the data set
    def __init__(self, fileName, game):
        self.fileName = fileName
        self.playerSelections = []
        self.game = game

    # Reads file with name fileName and populates the playerSelections list with
    # selections from the data set
    def readFile(self):
        # Open file
        toRead = open(self.fileName)

        # Increment when a line is read from file
        lineNum = 0
        for line in toRead:
            # First line (lineNum 0) is a header line with category information.
            # We omit this line
            if lineNum != 0:
                
                # Get only the first numCastles entries in each selection,
                # entries[len(entries) - 1] is an explanation made to explain betting
                # selection to the 538 competition
                entries = line.split(",")
                entries = [entries[index] for index in range(0, self.game.numCastles)]
                
                # Convert Strings to ints
                curSelection = [int(s) for s in entries]
                
                self.playerSelections.append(curSelection)
                
            lineNum = lineNum + 1

        # Close file
        toRead.close()

    

# Script to find seleciton that wins the 538 competition

# Instantiate Game and PlayerBeater
game = Game()
pb = PlayerBeater(game)

# Run 1000 generations of pb
for i in range(1000):
    
    # Print generation number
    print str("Gen: " + str(i))
    # Create new generation of betting selections
    pb.update()


    # Commented code to add the best selection to a growing data set
    # in an attempt to expand data set during training
    '''
    newSel = pb.players[0].selection

    if i < 500:
        while newSel in game.dataSetPlus:
            newSel = game.updateHorizontal(newSel)
            newSel = game.updateVertical(newSel)
        
        game.dataSetPlus.append(pb.players[0].selection)
    '''

    
    # Print relevant information for each generation, with selections tested
    # on dataSetPlus, rather than just the original data
    bestSelection = pb.players[0]
    print "Best Selection: " + str(bestSelection)    
    bestPerformance = game.testSelection(bestSelection, game.dataSetPlus)
    print "Best Performance: " + str(bestPerformance)
    print "Best Score: " + str(game.calcScore(bestPerformance))

# The final best selection's performance, as evaluated on the original data set
bestSelection = pb.players[0].selection
print "Best Selection: " + str(bestSelection)
bestPerformance = game.testSelection(bestSelection, game.fp.playerSelections)
print "Best Performance: " + str(bestPerformance)
print "Best Score: " + str(game.calcScore(bestPerformance))

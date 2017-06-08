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
        self.numCastles = 10
        self.numSoldiers = 100

        self.fp = FileParser("castle-solutions.csv", self)
        self.fp.readFile()
        #self.dataSetPlus = [selection for selection in self.fp.playerSelections]
        #self.dataSetPlus = [self.updateRandom() for i in range(len(self.fp.playerSelections))]
        self.dataSetPlus = []

        #dataSetLen = len(self.dataSetPlus)
        #for i in range(dataSetLen):
            #sel = self.dataSetPlus[i]
            #self.dataSetPlus.append(sel)            
            #self.dataSetPlus.append(sel)
            #newSel = self.updateHorizontal(sel)
            #self.dataSetPlus.append(newSel)
            #newSel = self.updateHorizontal(newSel)
            #newSel = self.updateHorizontal(sel)
            #newSel = self.updateVertical(sel)
            #self.dataSetPlus.append(newSel)            

        for i in range(3000):
            sel = self.updateRandom()
            sel = self.updateDown(sel)
            self.dataSetPlus.append(sel)


        print "game init"

    # Determines which of two players won the most points
    def compare(self, player1Sel, player2Sel):

        if len(player1Sel) > self.numCastles or len(player2Sel) > self.numCastles:
            print "ERROR: Invalid size of betting selections"
            return -1
        
        if sum(player1Sel) > self.numSoldiers or sum(player2Sel) > self.numSoldiers:
            print "ERROR: Invalid number of soldiers in selections"
            return -1

        player1Score = 0
        player2Score = 0

        # Determine which player wins each castle. If each player has 
        # attacked with the same number of soldiers, castle is won by
        # neither
        for i in range(0, self.numCastles):
            if player1Sel[i] > player2Sel[i]:
                player1Score = player1Score + i + 1
            elif player2Sel[i] > player1Sel[i]:
                player2Score = player2Score + i + 1

        return (player1Score, player2Score)
        
    def testSelection(self, playerSelection, dataSet):
        
        playerWins = 0
        playerTies = 0
        playerLosses = 0
        
        #for selection in self.fp.playerSelections:
        for selection in dataSet:

            (s1, s2) = self.compare(playerSelection, selection)

            if s1 > s2:
                playerWins = playerWins + 1
            elif s1 < s2:
                playerLosses = playerLosses + 1
            else:
                playerTies = playerTies + 1

                
        return (playerWins, playerTies, playerLosses)

    def calcScore(self, wtl):
        return 3 * wtl[0] + wtl[1] 

    # Assign a new selection to the player
    def copySelection(self, selection):
        newSelection = []

        for soldiersAtCastle in selection:
            newSelection.append(soldiersAtCastle)

        return newSelection

    # Throw mass at the higher scoring castles
    def updateVertical(self, oppSelection):
        
        selection = self.copySelection(oppSelection)
        selectionLen = len(selection)

        # Get the index of the first non-zero bet made by opponent
        index = 0
        while (index < selectionLen - 1) and (selection[index] == 0):
            index = index + 1
        
        selection[index] = selection[index] - 1
        selection[selectionLen - 1] = selection[selectionLen - 1] + 1

        return selection

    def updateDown(self, oppSelection):

        selection = self.copySelection(oppSelection)
        selectionLen = len(selection)

        highestBidOn = selection[selectionLen - 1]
        selection[selectionLen - 1] = 0

        for i in range(highestBidOn):
            randPos = random.randrange(selectionLen)
            selection[randPos] = selection[randPos] + 1
        
            
        return selection

    # Throw mass at castles that are not occupied
    def updateHorizontal(self, oppSelection):

        selection = self.copySelection(oppSelection)
        selectionLen = len(selection)

        # Get the index of the first non-zero bet made by opponent
        index = 0
        while (index < selectionLen - 1) and (selection[index] == 0):
            index = index + 1

        # Find all castles where bets were not made
        zeroBets = []
        for i in range(selectionLen):
            if selection[i] == 0:
                zeroBets.append(i)

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



class Player:
    
    # Initializes a player with a very bad bet selection
    def __init__(self, game):
        self.selection = []
        remaining = game.numSoldiers + 1
        
        # Very biased method of filling in bets
        # Puts a heavy weight for high bets on lower scoring castles
        for i in range(game.numCastles):
            nextNum = random.randrange(remaining)
            self.selection.append(nextNum)
            remaining = remaining - nextNum

        self.selectionLen = len(self.selection)
        self.game = game

    # Assign a new selection to the player
    def copySelection(self, selection):
        self.selection = []

        for soldiersAtCastle in selection:
            self.selection.append(soldiersAtCastle)

    def mutate(self):

        p = Player(self.game)
        p.copySelection(self.selection)
        
        numMutations = random.randrange(10)

        for i in range(numMutations + 1):
            randIndex1 = random.randrange(p.selectionLen)
            randIndex2 = random.randrange(p.selectionLen)
            
            castle1Sel = p.selection[randIndex1]
            castle2Sel = p.selection[randIndex2]
            
            if castle1Sel > 0:
                p.selection[randIndex1] = p.selection[randIndex1] - 1
                p.selection[randIndex2] = p.selection[randIndex2] + 1

        return p

        

    # Throw mass at the higher scoring castles
    def updateVertical(self, oppSelection):
        
        self.copySelection(oppSelection)
        
        # Get the index of the first non-zero bet made by opponent
        index = 0
        while (index < self.selectionLen - 1) and (self.selection[index] == 0):
            index = index + 1
        
        self.selection[index] = self.selection[index] - 1
        self.selection[self.selectionLen - 1] = self.selection[self.selectionLen - 1] + 1

        return self.selection

    # Throw mass at castles that are not occupied
    def updateHorizontal(self, oppSelection):

        self.copySelection(oppSelection)
        
        # Get the index of the first non-zero bet made by opponent
        index = 0
        while (index < self.selectionLen - 1) and (self.selection[index] == 0):
            index = index + 1

        # Find all castles where bets were not made
        zeroBets = []
        for i in range(self.selectionLen):
            if self.selection[i] == 0:
                zeroBets.append(i)

        if len(zeroBets) == 0:
            return 0

        soldiersToDistribute = self.selection[index]
        self.selection[index] = 0

        # Redistribute soldiers to castles with no soldiers
        zIndex = 0
        while soldiersToDistribute > 0:
            curCastle = zeroBets[zIndex]
            self.selection[curCastle] = self.selection[curCastle] + 1

            zIndex = zIndex + 1
            if zIndex >= len(zeroBets):
                zIndex = 0

            soldiersToDistribute = soldiersToDistribute - 1

        return self.selection


    # Apply updateVertical() twice
    def updateVerticalWinner(self, oppSelection):
        newSelection = self.updateVertical(oppSelection)
        self.updateVertical(newSelection)
        return self.selection

    # Disregards move made by opponent and randomly creates new bet selection
    def updateRandom(self, oppSelection=None):

        # Very clsoe to creating a list of random numbers that sum to numSoldiers
        newSelection = [random.randrange(self.game.numSoldiers) for i in range(self.game.numCastles)]
        s = sum(newSelection)
        self.selection = [self.game.numSoldiers * i/s for i in newSelection]

        # Need to fix some gaps due to possible rounding error in previous
        # list comprehension
        while sum(self.selection) != self.game.numSoldiers:
            index = random.randrange(self.selectionLen)
            self.selection[index] = self.selection[index] + 1

        return self.selection

    # Bets 0 on the bottom half of the castles and bets the rest on top half
    def updateRandomPlus(self, oppSelection):
        zeros = [0] * (self.selectionLen / 2)
        
        # Very clsoe to creating a list of random numbers that sum to numSoldiers
        newSelection = [random.randrange(self.game.numSoldiers) for i in range(self.game.numCastles / 2)]
        s = sum(newSelection)
        newSelection = [self.game.numSoldiers * i/s for i in newSelection]

        # Need to fix some gaps due to possible rounding error in previous
        # list comprehension
        while sum(newSelection) != self.game.numSoldiers:
            index = random.randrange(self.selectionLen / 2)
            newSelection[index] = newSelection[index] + 1

        self.selection = zeros + newSelection

        while len(self.selection) != self.game.numCastles:
            self.selection = [0] + self.selection

        return self.selection

class PlayerBeater:

    def __init__(self, game):
        self.game = game
        self.numPlayers = 60

        self.players = []
        for i in range(self.numPlayers):
            player = Player(game)
            player.updateRandom()
            self.players.append(player)


    def scorePlayer(self, player):
        return self.game.calcScore(self.game.testSelection(player.selection, game.dataSetPlus))


    def update(self):
        playersAndScores = [(player, self.scorePlayer(player)) for player in self.players]
        
        # Do a bubble sort, but this needs to be rewritten ASAP
        for i in range(self.numPlayers):
            for j in range(self.numPlayers - 1):
                if playersAndScores[j][1] < playersAndScores[j + 1][1]:
                    temp = playersAndScores[j]
                    playersAndScores[j] = playersAndScores[j + 1]
                    playersAndScores[j + 1] = temp

        newPlayers = []
        
        #rankedscores = [score for (player, score) in playersAndScores]

        for index in range(self.numPlayers / 3):
            newPlayers.append(playersAndScores[index][0])

            randomPlayer = Player(self.game)
            randomPlayer.updateRandom()
            newPlayers.append(randomPlayer)
            
            mutant = playersAndScores[index][0].mutate()

            
            contained = True
            
            # Test to see if the mutant's selection already exists in the new generation
            while contained:
                playerIndex = 0
                while playerIndex < len(newPlayers):
                    
                    player = newPlayers[playerIndex]
                    # Determine if current player has same selection as mutant
                    # If it does, mutant is alerady contained in new generation
                    sameSel = True

                    for castleIndex in range(player.selectionLen):
                        if player.selection[castleIndex] != mutant.selection[castleIndex]:
                            sameSel = False

                    # Found a creature with the same selection
                    if sameSel:
                        break
                            
                    playerIndex = playerIndex + 1
                        
                contained = not (playerIndex == len(newPlayers))
                mutant = mutant.mutate()
            
            newPlayers.append(mutant)                

        self.players = newPlayers



class FileParser:

    def __init__(self, fileName, game):
        self.fileName = fileName
        self.playerSelections = []
        self.game = game

    def readFile(self):
        toRead = open(self.fileName)
        
        lineNum = 0
        for line in toRead:
            if lineNum != 0:
                player = Player(self.game)
                
                entries = line.split(",")
                entries = [entries[index] for index in range(0, self.game.numCastles)]
                
                curSelection = [int(s) for s in entries]
                
                self.playerSelections.append(curSelection)
                
            lineNum = lineNum + 1

            

        toRead.close()

    

'''
# Keep track of number of trials won by player1, player2, and the number that
# ended in a draw
p1TrialWins = 0
p2TrialWins = 0
draws = 0

for numExp in range(0, 100):
    # Perform the desired number of experiments(trials)

    g = Game()

    # Scores within each trial
    pScore1 = 0
    pScore2 = 0

    # Create new players for the trial
    player1 = Player(g)
    player2 = Player(g)

    for numTrial in range(0, 100):
        # Perform the desired number of games within a trial
        
        # Create copies of the bet selections for both players
        p1Sel = []
        p2Sel = []
        for index in range(len(player1.selection)):
            p1Sel.append(player1.selection[index])
            p2Sel.append(player2.selection[index])


            
        # Compare the bets of the two players to see who wins the game
        (s1, s2) = g.compare(p1Sel, p2Sel)
        if s1 > s2:
            # Player 1 wins the game
            pScore1 = pScore1 + 1 
        elif s2 > s1:
            # Player 2 wins the game
            pScore2 = pScore2 + 1 
            player1.updateHorizontal(p2Sel)
            


        #player1.updateRandomPlus(p2Sel)
        #player1.updateHorizontal(p2Sel)
        player2.updateRandomPlus(p1Sel)



    #print("Player 1 final selection: " + str(player1.selection))
    if pScore1 > pScore2:
        # Player 1 wins the most games in the trial
        p1TrialWins = p1TrialWins + 1
    elif pScore2 > pScore1:
        # Player 2 wins the most games in the trial
        p2TrialWins = p2TrialWins + 1        
    else:
        # Both players won the same number of games in the trial
        draws = draws + 1

    print( "Player 1 wins: " + str(pScore1) + " Player 2 wins: " + str(pScore2)) 


# Print relevant information for the results of the experiments
print "\n"
print "Player 1 won in " + str(p1TrialWins) + " trials."
print "Player 2 won in " + str(p2TrialWins) + " trials."
print "Draws in " + str(draws) + " trials."
print "\n"


'''
'''
g = Game()
player1 = Player(g)
player2 = Player(g)

print str(player1.selection)
player1.updateRandom(player2.selection)
print str(player1.selection)
'''

game = Game()
pb = PlayerBeater(game)
for i in range(1000):
    print str(i)
    pb.update()
    
    newSel = pb.players[0].selection

    if i < 500:
        while newSel in game.dataSetPlus:
            newSel = game.updateHorizontal(newSel)
            newSel = game.updateVertical(newSel)
        
        game.dataSetPlus.append(pb.players[0].selection)
        
    bestSelection = pb.players[0].selection
    print "Best Selection: " + str(bestSelection)
    
    '''
    pbPlayersLen = len(pb.players)

    for selIndex in range(pbPlayersLen / 12):
        curSel = pb.players[selIndex].selection
        if curSel not in game.dataSetPlus:
            game.dataSetPlus.append(curSel)
    '''

    bestPerformance = game.testSelection(bestSelection, game.dataSetPlus)
    print "Best Performance: " + str(bestPerformance)
    print "Best Score: " + str(game.calcScore(bestPerformance))

bestSelection = pb.players[0].selection
print "Best Selection: " + str(bestSelection)
bestPerformance = game.testSelection(bestSelection, game.fp.playerSelections)
print "Best Performance: " + str(bestPerformance)
print "Best Score: " + str(game.calcScore(bestPerformance))

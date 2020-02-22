from AIPlayerUtils import *
from GameState import *
from Move import Move
from Ant import UNIT_STATS
from Construction import CONSTR_STATS
from Constants import *
from Player import *
from AgentTest import *
import random
import sys
sys.path.append("..")  # so other modules can be found in parent dir


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "MiniMax")
        self.root = None
        self.prune = True
        self.test = False

    def init2(self):
      self.test = True
      self.winCount = -1
      self.moveCount = -1
      self.me = 0

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        if currentState.phase == SETUP_PHASE_1:
            return [(3, 1), (7, 1), (0, 3), (1, 3), (2, 3), (3, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3)]
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 7)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        self.me = currentState.whoseTurn
        if self.root is None:
          self.root = Node(None, currentState, 0, None, self.test)

          # For loops goes until set depth
          # in this case a depth of 3 
          self.total = 0
          self.expandNode(self.root)
          print(self.total)
        if not len(self.root.children) == 0:
          maxNode = self.root.children[0]
          maxScore = self.root.children[0].score
          for child in self.root.children:
            #print(child.move)
            #print(child.score)
            if child.score > maxScore:
              maxScore = child.score
              maxNode = child
          print(maxNode.score)
          print(maxNode.move)
          if maxNode.move.moveType == END or self.root.children == []:
            self.root = None
          else:
            self.root = maxNode
          return maxNode.move
        return Move(END)

    def legalMove(self, state, move):
      if move.coordList is not None and move.moveType == MOVE_ANT:
        if getAntAt(state, move.coordList[0]).hasMoved:
          return False
      return True
        
    ##
    # expandNode
    #
    # takes in a node and expands it by
    # taking all valid moves from that state
    # and creating new nodes for each new move
    #
    # returns a list of nodes
    ##
    def expandNode(self, node):
      win = None
      if not self.test:
        win = getWinner(node.state)
      else:
        win = getWinnerMock()
      if win is not None:
        node.score = 100 if (win == 1) else -100
        node.score = node.score if (node.turn == self.me) else -node.score
        if node.parent is not None:
          node.parent.updateBounds(node, self.me)
        return
      if node.depth == 3:
        if not self.test:
          node.score = self.utility(node.state)
        else:
          node.score = utilityMock()
        if node.parent is not None:
          node.parent.updateBounds(node, self.me)
        return
      if not self.test:
        moves = listAllLegalMoves(node.state)
      else:
        moves = listMovesMock()
      for move in moves:
        if not self.test:
          nextState = getNextStateAdversarial(node.state, move)
        else:
          nextState = None
        if node.depth > 0 and node.move.moveType == BUILD and not move.moveType == END:
          continue
        newDepth = node.depth + 1
        newNode = Node(move, nextState, newDepth, node, self.test)
        if self.test and newDepth % 2 == 0:
          newNode.setTurn(0)
        if self.test and not newDepth % 2 == 0:
          newNode.setTurn(1)
        node.addChild(newNode)
        self.expandNode(newNode)
        if self.prune and node.parent is not None:
          if node.turn == self.me:
            if node.alpha >= node.parent.beta or (node.score is not None and node.score >= node.parent.beta):
              if self.test:
                print("Alpha: {}, {}".format(node.alpha, node.parent.beta))
              node.parent.removeChild(node)
              return
          else:
            if node.beta <= node.parent.alpha or (node.score is not None and node.score <= node.parent.alpha):
              if self.test:
                print("Beta: {}, {}".format(node.beta, node.parent.alpha))
              node.parent.removeChild(node)
              return
      
      self.total += len(node.children)
      if node.turn == self.me:
        node.score = node.alpha
      else:
        node.score = node.beta
      if node.parent is not None:
        node.parent.updateBounds(node, self.me)
      if node.parent is None:
        print("Root:")
        print(node.score)
        print(len(node.children))

    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##

    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass

    ##
    #heuristicStepsToGoal
    #Description: Gets the number of moves to get to a winning state from the current state
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #                 This will assumed to be a fast clone of the state
    #                 i.e. the board will not be needed/used
    ##
    def utility(self, currentState):
      me = currentState.whoseTurn
      enemy = abs(me - 1)
      myInv = getCurrPlayerInventory(currentState)
      myFood = myInv.foodCount
      enemyInv = getEnemyInv(self, currentState)
      enemyFood = enemyInv.foodCount
      tunnels = getConstrList(currentState, types=(TUNNEL,))
      myTunnel = tunnels[1] if (tunnels[0].coords[1] > 5) else tunnels[0]
      enemyTunnel = tunnels[0] if (myTunnel is tunnels[1]) else tunnels[1]
      hills = getConstrList(currentState, types=(ANTHILL,))
      myHill = hills[1] if (hills[0].coords[1] > 5) else hills[0]
      enemyHill = hills[1] if (myHill is hills[0]) else hills[0]
      myQueen = myInv.getQueen()
      enemyQueen = enemyInv.getQueen()

      foods = getConstrList(currentState, None, (FOOD,))

      myWorkers = getAntList(currentState, me, (WORKER,))
      myOffense = getAntList(currentState, me, (SOLDIER,))
      enemyWorkers = getAntList(currentState, enemy, (WORKER,))
      enemyOffense = getAntList(currentState, enemy, (SOLDIER, R_SOLDIER))
      enemyDrones = getAntList(currentState, enemy, (DRONE,))

      # "steps" val that will be returned
      myScore = 0
      enemyScore = 0

      # value army size
      if me == self.me:
        myScore += min(len(myOffense), 3) * 15
        enemyScore += max((min(len(enemyDrones), 5) * 7), min(len(enemyOffense), 3) * 15)
      else:
        enemyScore += min(len(myOffense), 3) * 15
        myScore += max((min(len(enemyDrones), 5) * 7), min(len(enemyOffense), 3) * 15)

      # encourage more food gathering
      myScore -= 10 if (myFood < 1) else 0
      enemyScore -= 10 if (enemyFood < 1) else 0

      # never want 0 workers
      myScore -= 30 if (len(myWorkers) < 1) else 0
      enemyScore -= 30 if (len(enemyWorkers) < 1) else 0

      # calculation for soldier going
      # to kill enemyworker and after
      # going to sit on enemy anthill
      dist = 100
      for ant in myOffense:
        if len(enemyWorkers) == 0:
          dist = stepsToReach(currentState, ant.coords, enemyHill.coords)
        else:
          dist = stepsToReach(currentState, ant.coords, enemyWorkers[0].coords)
        myScore += 10 - min(dist, 10)
      myScore += 21 - 7*(enemyHill.captureHealth)
      dist = 100
      for ant in enemyOffense:
        dist = approxDist(ant.coords, myHill.coords)
        enemyScore += 10 - min(dist, 10)
      enemyScore += 21 - 7*(myHill.captureHealth)

      # Gather food
      if me == self.me:
        workers = myWorkers
        tunnel = myTunnel
        hill = myHill
      else:
        workers = enemyWorkers
        tunnel = enemyTunnel
        hill = enemyHill
      score = 0
      for w in workers:
        if w.carrying: # if carrying go to hill/tunnel
          score += 3
          distanceToTunnel = approxDist(w.coords, tunnel.coords)
          distanceToHill = approxDist(w.coords, hill.coords)
          dist = min(distanceToHill, distanceToTunnel)
          if dist > 2 and dist <= 4:
            score += 1
          if dist <= 2:
            score += 2
        else: # if not carrying go to food
          dist = 100
          for food in foods:
            temp = approxDist(w.coords, food.coords)
            if temp < dist:
              dist = temp
          if dist > 2 and dist <= 4:
            score += 1
          if dist <= 2:
            score += 2
      if self.me == me:
        myScore += score
      else:
        enemyScore += score
#     for w in myWorkers:
#       if w.carrying:
#         myScore += 4
#     myScore += myFood * 7

      if self.me == me:
        workers = enemyWorkers
      else:
        workers = myWorkers
      score = 0
      for w in workers:
        if w.carrying:
          enemyScore += 4
      if self.me == me:
        enemyScore += score
      else:
        myScore += score
      enemyScore += enemyFood * 7

      score = min(myScore - enemyScore, 95) if (myScore - enemyScore > 0) else max(myScore - enemyScore, -95)
      win = getWinner(currentState)
      if win is not None:
        score = 100 if (win == 1) else -100
      return score if (me == self.me) else -score

     

##
# Node Class
#
# Defines how our Node is set up to use for searching
#
##
class Node:
  def __init__(self, move, state, depth, parent, test):
    self.move = move
    self.state = state
    self.depth = depth
    self.score = None
    if not test:
      self.turn = state.whoseTurn
    else:
      self.turn = None
    self.alpha = -200
    self.beta = 200#alpha and beta values for minimax
    self.children = []
    self.parent = parent
  
  def init2():
    self.test = True

  def addChild(self, node):
    self.children.append(node)

  def removeChild(self, node):
    self.children.remove(node)
  
  def updateBounds(self, node, me):
    if self.turn == me:#max player
      self.alpha = max(self.alpha, node.score)
        
    else:
      self.beta = min(self.beta, node.score)
    return True

  def setTurn(self, turn):
    self.turn = turn

# Term Project BOO

# code file taken from https://www.diderot.one/course/34/
from cmu_112_graphics import *
import random
from random_maze_creator import *

################################################################################
# Functions used 
################################################################################

def distance(x0:int, y0:int, x1:int, y1:int) -> int: # finds disance between two objects
    return ((x1-x0)**2+(y1-y0)**2)**0.5

# cade taken from www.diderot.one/course/34/chapters/2604/
def readFile(path):     # reads text  from scoreboard.txt
    with open(path, "rt") as f:
        return f.read()

# cade taken from www.diderot.one/course/34/chapters/2604/
def writeFile(path, contents):      # writes scores into scoreboard.txt
    with open(path, "wt") as f:
        f.write(contents)

################################################################################
# Class for power-ups
################################################################################
# class for the power ups in the game.
class PowerUps(object):
    def __init__(self, app, cx, cy, image):
        self.app = app
        self.cx = cx
        self.cy = cy
        self.image = image
        self.r = 7    # radius of spawned power-up

    def checkCollision(self):
        # check collision with player and spawned power-up
        dist = distance(self.cx, self.cy, self.app.playerX, self.app.playerY)
        if dist <= self.app.playerR - self.r:
            return True
        return False

    def checkGhostCollision(self):
        # chesk collision with a ghost
        for ghost in self.app.ghosts:
            dist = distance(self.cx, self.cy, ghost.ghostCX, ghost.ghostCY)
            if dist <= self.r - ghost.ghostR:
                return True
            return False

    def render(self, canvas):
        # animates the power-up
        canvas.create_oval(self.cx-self.r, self.cy-self.r,
                           self.cx+self.r, self.cy+self.r, 
                           fill="pink", width=0)
        canvas.create_image(self.cx, self.cy, image=ImageTk.PhotoImage(self.image))

################################################################################
# Class for ghosts
################################################################################
# class for the general ghost in the game.
# appears in game mode level 1
class Ghosts(object):
    def __init__(self, app, ghostCX, ghostCY, image):
        self.app = app
        self.ghostCX = ghostCX
        self.ghostCY = ghostCY
        self.ghostR = 12    # radius of ghost
        self.image = image
        self.speed = 2
    
    def checkPlayerCollision(self):
        # checks collision between ghost and player
        dist = distance(self.ghostCX, self.ghostCY, self.app.playerX, self.app.playerY)
        if dist <= self.app.playerR + self.ghostR:
            return True
        return False 

    def checkLightCollision(self):
        # checks the collision of the flashlight with the a ghost
        dist = distance(self.ghostCX, self.ghostCY, self.app.playerX, self.app.playerY)
        if dist <= self.app.lightR + self.ghostR:
            return True
        return False

    def checkWallCollision(self, row, col):
        # checks if the ghost is colliding with the maze walls.
        # ghosts do not go through walls.
        x0, y0, x1, y1 = self.app.getCellBounds(row, col)
        # for ghost in self.ghosts:
        if y0 <= self.ghostCY <= y1:
            if self.ghostCX > x1:
                if self.ghostCX-self.ghostR <= x1:
                    return True
            if self.ghostCX < x0: 
                if self.ghostCX+self.ghostR >= x0:
                    return True
        if x0 <= self.ghostCX <= x1: 
            if self.ghostCY > y1: 
                if self.ghostCY-self.ghostR <= y1:
                    return True
            if self.ghostCY < y0: 
                if self.ghostCY+self.ghostR >= y0:
                    return True
        return False
    
    def followPlayer(self):
        # function for making the ghost follow the player around.
        if self.ghostCX > self.app.playerX:
            self.ghostCX -= self.speed
            for row in range(self.app.rows):
                for col in range(self.app.cols):
                    if (self.checkWallCollision(row, col) == True and
                        self.app.maze[row][col] == False):
                        self.ghostCX += self.speed
        elif self.ghostCX < self.app.playerX:
            self.ghostCX += self.speed
            for row in range(self.app.rows):
                for col in range(self.app.cols):
                    if (self.checkWallCollision(row, col) == True and
                        self.app.maze[row][col] == False):
                        self.ghostCX -= self.speed
        if self.ghostCY < self.app.playerY:
            self.ghostCY += self.speed
            for row in range(self.app.rows):
                for col in range(self.app.cols):
                    if (self.checkWallCollision(row, col) == True and
                        self.app.maze[row][col] == False):
                        self.ghostCY -= self.speed
        elif self.ghostCY > self.app.playerY:
            self.ghostCY -= self.speed
            for row in range(self.app.rows):
                for col in range(self.app.cols):
                    if (self.checkWallCollision(row, col) == True and
                        self.app.maze[row][col] == False):
                        self.ghostCY += self.speed

    def render(self, canvas):
        # animates the ghost
        canvas.create_oval(self.ghostCX-self.ghostR, self.ghostCY-self.ghostR,
                           self.ghostCX+self.ghostR, self.ghostCY+self.ghostR,
                           fill="white", width=0)
        canvas.create_image(self.ghostCX, self.ghostCY, image=ImageTk.PhotoImage(self.image))

# subclass for ghosts that collect items if it is closer to the power-ups and
# follow the player if it is closer to the player.
# Appears in level 2, they will prioritize following the player over 
# collecting items when the player is closer to the end than the ghost.
class SmartBoi(Ghosts):
    def __init__(self, app, ghostCX, ghostCY, image):
        super().__init__(app, ghostCX, ghostCY, image)
        self.app = app
        self.ghostR = 12    # radius of ghost
        self.image = image
        self.speed = 2

    def checkCloserToPlayer(self, powerUp):
        # checks if the ghost is closer to the goal than the player. If so, it 
        # will go get a power-up, if not will follow the player. 
        # Following the player is top priority.
        playerDistToGoalX = self.app.playerX 
        playerDistToGoalY = self.app.playerY
        ghostDistToGoalX = self.ghostCX
        ghostDistToGoalY = self.ghostCY
        # checks whether the player is closer to the goal than the ghost
        if (playerDistToGoalX <= ghostDistToGoalX or
            playerDistToGoalY <= ghostDistToGoalY):
            return True
        # checks whether the the ghost is closer to the player or the power up.
        distWithPlayer = distance(self.ghostCX, self.ghostCY, self.app.playerX, self.app.playerY)
        distWithPowUp = distance(self.ghostCX, self.ghostCY, powerUp.cx, powerUp.cy)
        if distWithPlayer <= distWithPowUp or len(self.app.powerUps) == 0:
            return True
        return False

    def getItem(self):
        # function for ghost to get closest power-up
        for powerUp in self.app.powerUps:
            if self.checkCloserToPlayer(powerUp) == False:
                if self.ghostCX > powerUp.cx:
                    self.ghostCX -= self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCX -= self.speed
                elif self.ghostCX < powerUp.cx:
                    self.ghostCX += self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCX -= self.speed
                if self.ghostCY < powerUp.cy:
                    self.ghostCY += self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCY -= self.speed
                elif self.ghostCY > powerUp.cy:
                    self.ghostCY -= self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCY += self.speed

# subclass for ghosts that collect items if it is closer to the power-ups and
# follow the player if it is closer to the player.
# Appears in level 3, they will prioritize following the player over 
# collecting items when the player is closer to the end than the ghost.
# If the ghost collects a power up, it speeds up. (there is a cap to its speed)
class SmartBoi2(Ghosts):
    def __init__(self, app, ghostCX, ghostCY, image):
        super().__init__(app, ghostCX, ghostCY, image)
        self.app = app
        self.ghostR = 12    # radius of ghost
        self.image = image
        self.speed = 2

    def checkCloserToPlayer(self, powerUp):
        # same as SmartBoi1
        playerDistToGoalX = self.app.rBounds - self.app.playerX
        playerDistToGoalY = self.app.dBounds - self.app.playerY
        ghostDistToGoalX = self.app.rBounds - self.ghostCX
        ghostDistToGoalY = self.app.dBounds - self.ghostCY
        # checks whether the player is closer to the goal than the ghost
        if (playerDistToGoalX <= ghostDistToGoalX or
            playerDistToGoalY <= ghostDistToGoalY):
            return True
        # checks whether the the ghost is closer to the player or the power up.
        distWithPlayer = distance(self.ghostCX, self.ghostCY, self.app.playerX, self.app.playerY)
        distWithPowUp = distance(self.ghostCX, self.ghostCY, powerUp.cx, powerUp.cy)
        if distWithPlayer <= distWithPowUp or len(self.app.powerUps) == 0:
            return True
        return False

    def getItem(self):
        # same as SmartBoi2
        for powerUp in self.app.powerUps:
            if self.checkCloserToPlayer(powerUp) == False:
                if self.ghostCX > powerUp.cx:
                    self.ghostCX -= self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCX -= self.speed
                elif self.ghostCX < powerUp.cx:
                    self.ghostCX += self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCX -= self.speed
                if self.ghostCY < powerUp.cy:
                    self.ghostCY += self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCY -= self.speed
                elif self.ghostCY > powerUp.cy:
                    self.ghostCY -= self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCY += self.speed

# class for ghosts that appear in the inifinite mazes mode.
class InfiGhosts(object):
    def __init__(self, app, ghostCX, ghostCY):
        self.app = app
        self.ghostCX = ghostCX
        self.ghostCY = ghostCY
        self.ghostR = 10    # radius of ghost
        self.speed = 2

    def checkPlayerCollision(self):
        # checks collision between ghost and player
        dist = distance(self.ghostCX, self.ghostCY, self.app.playerX, self.app.playerY)
        if dist <= self.app.playerR + self.ghostR:
            return True
        return False 

    def checkLightCollision(self):
        # check collision between the light from the flashlight and ghost.
        dist = distance(self.ghostCX, self.ghostCY, self.app.playerX, self.app.playerY)
        if dist <= self.app.lightR + self.ghostR:
            return True
        return False

    def checkWallCollision(self, row, col):
        # cheks if the ghost collided into the wall or not.
        x0, y0, x1, y1 = self.app.getCellBounds(row, col)
        # for ghost in self.ghosts:
        if y0 <= self.ghostCY <= y1:
            if self.ghostCX > x1:
                if self.ghostCX-self.ghostR <= x1:
                    return True
            if self.ghostCX < x0: 
                if self.ghostCX+self.ghostR >= x0:
                    return True
        if x0 <= self.ghostCX <= x1: 
            if self.ghostCY > y1: 
                if self.ghostCY-self.ghostR <= y1:
                    return True
            if self.ghostCY < y0: 
                if self.ghostCY+self.ghostR >= y0:
                    return True
        return False
    
    def followPlayer(self):
        # function for the ghost to follow the player.
        if self.ghostCX > self.app.playerX:
            self.ghostCX -= self.speed
            for row in range(self.app.rows):
                for col in range(self.app.cols):
                    if (self.checkWallCollision(row, col) == True and
                        self.app.maze[row][col] == False):
                        self.ghostCX += self.speed
        elif self.ghostCX < self.app.playerX:
            self.ghostCX += self.speed
            for row in range(self.app.rows):
                for col in range(self.app.cols):
                    if (self.checkWallCollision(row, col) == True and
                        self.app.maze[row][col] == False):
                        self.ghostCX -= self.speed
        if self.ghostCY < self.app.playerY:
            self.ghostCY += self.speed
            for row in range(self.app.rows):
                for col in range(self.app.cols):
                    if (self.checkWallCollision(row, col) == True and
                        self.app.maze[row][col] == False):
                        self.ghostCY -= self.speed
        elif self.ghostCY > self.app.playerY:
            self.ghostCY -= self.speed
            for row in range(self.app.rows):
                for col in range(self.app.cols):
                    if (self.checkWallCollision(row, col) == True and
                        self.app.maze[row][col] == False):
                        self.ghostCY += self.speed

    def checkFollowPlayer(self, powerUp):
        # same as SmartBoi1 and 2
        playerDistToGoalX = self.app.rBounds - self.app.playerX
        playerDistToGoalY = self.app.dBounds - self.app.playerY
        ghostDistToGoalX = self.app.rBounds - self.ghostCX
        ghostDistToGoalY = self.app.dBounds - self.ghostCY
        # checks whether the player is closer to the goal than the ghost
        if (playerDistToGoalX <= ghostDistToGoalX or
            playerDistToGoalY <= ghostDistToGoalY):
            return True
        # checks whether the the ghost is closer to the player or the power up.
        distWithPlayer = distance(self.ghostCX, self.ghostCY, self.app.playerX, self.app.playerY)
        distWithPowUp = distance(self.ghostCX, self.ghostCY, powerUp.cx, powerUp.cy)
        if distWithPlayer <= distWithPowUp or len(self.app.powerUps) == 0:
            return True
        return False

    def getItem(self):
        # function for the ghost to go get the power up.
        for powerUp in self.app.powerUps:
            if self.checkFollowPlayer(powerUp) == False:
                if self.ghostCX > powerUp.cx:
                    self.ghostCX -= self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCX -= self.speed
                elif self.ghostCX < powerUp.cx:
                    self.ghostCX += self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCX -= self.speed
                if self.ghostCY < powerUp.cy:
                    self.ghostCY += self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCY -= self.speed
                elif self.ghostCY > powerUp.cy:
                    self.ghostCY -= self.speed
                    for row in range(self.app.rows):
                        for col in range(self.app.cols):
                            if (self.checkWallCollision(row, col) == True and
                                self.app.maze[row][col] == False):
                                self.ghostCY += self.speed

    def render(self, canvas):
        # animate the ghost
        canvas.create_oval(self.ghostCX-self.ghostR, self.ghostCY-self.ghostR,
                           self.ghostCX+self.ghostR, self.ghostCY+self.ghostR,
                           fill="white", width=0)
        canvas.create_text(self.ghostCX, self.ghostCY, text='boo')

################################################################################
# Start/Home Screen
################################################################################
class StartMode(Mode):
    def appStarted(self):
        self.title = 'Boo!'
        self.play = self.getMode('play')
        self.scoreboard = self.getMode('scores')
        # load background image
        self.backgroundSize = 1100
        self.backgroundImage = self.loadImage('images/boos.png')
        w,h = self.backgroundImage.size
        self.backgroundImage = self.scaleImage(self.backgroundImage, self.backgroundSize/w)

    def onClickPlay(self):
        self.app.setActiveMode('play')

    # def onClickScoreBoard(self):
    #     self.scoreboard.createBoard()
    #     self.app.setActiveMode('scores')
    
    def onClickInstructions(self):
        self.app.setActiveMode('instr')

    def onClickInfinite(self):
        self.app.setActiveMode('inf')

    def redrawAll(self, canvas):
        # load the image of the background picture
        canvas.create_image(self.app.width/2, self.app.height/2, image=ImageTk.PhotoImage(self.backgroundImage))
        # create the buttons
        canvas.create_text(self.app.width/2, self.app.height/3, 
                           text=self.title, fill='orange', font="Chiller 200 bold")
        canvas.create_rectangle((4*self.app.width/5-40), (3*self.app.height/4-20),
                                (4*self.app.width/5+40), (3*self.app.height/4+20),
                                fill="pink", onClick=self.onClickPlay)
        canvas.create_text(4*self.app.width/5, 3*self.app.height/4, font="Times 11 bold", text="PLAY")
        # canvas.create_rectangle((self.app.width/5-40), (4*self.app.height/5-20),
        #                         (self.app.width/5+40), (4*self.app.height/5+20),
        #                         fill="light blue", onClick=self.onClickScoreBoard)
        # canvas.create_text(self.app.width/5, 4*self.app.height/5, font="Times 8 bold", text="SCOREBOARD")
        canvas.create_rectangle((4*self.app.width/5-40), (5*self.app.height/6-20),
                                (4*self.app.width/5+40), (5*self.app.height/6+20),
                                fill="light green", onClick=self.onClickInfinite)
        canvas.create_text(4*self.app.width/5, 5*self.app.height/6, font="Times 11 bold", text="INFINITE\nMODE")
        canvas.create_rectangle((self.app.width/5-40), (4*self.app.height/5-20),
                                (self.app.width/5+40), (4*self.app.height/5+20),
                                fill="light yellow", onClick=self.onClickInstructions)
        canvas.create_text(self.app.width/5, 4*self.app.height/5, font="Times 8 bold", text="INSTUCTIONS")

################################################################################
# Instructions Mode
################################################################################
class Instructions(Mode):
    def appStarted(self):
        self.instructions = """
        Play Mode: Help Mr. Red get to the end of all 3 mazes without touching 
                            the walls or ghosts! Use your cursor to navigate through
                            the mazes. The mazes will increase in difficulty as you 
                            progress through the game. The mazes are randomly 
                            generated each time.
                            Collect power-ups along the way to'shrink' 
                            in size, or get a flashlight to scare the ghosts
                            away. Beware the ghosts, as they get smarter and
                            faster every level.
                            Press 'Backspace' to quit game whenever you like.
                            *Cheat: (Press S to skip a level.)

        Inifinite Mode: Navigate through mazes infinitely until you lose.
                                 All of the mazes will be randomly generated and 
                                 as the difficulty would be random each time as well. 
                                 Great mode to practice your skills.
                                 Press 's' to generate a different maze."""
        
    def onClickPlay(self):
        self.app.setActiveMode('start')

    def redrawAll(self, canvas):
        # create the buttons 
        canvas.create_text(self.app.width/2, self.app.height/2, text=self.instructions, font='Times 14 bold')
        canvas.create_rectangle((self.app.width/2-40), (7*self.app.height/8-20),
                                (self.app.width/2+40), (7*self.app.height/8+20),
                                fill="pink", onClick=self.onClickPlay)
        canvas.create_text(self.app.width/2, 7*self.app.height/8, font="Times 11 bold", text="BACK")

################################################################################
# Infinite mode
################################################################################
class InfiniteMode(Mode):
    def loadImages(self):
        # powerUp image
        self.powerUpSize = 23
        self.powerUpImage = self.loadImage('images/orb.png')
        w,h = self.powerUpImage.size
        self.powerUpImage = self.scaleImage(self.powerUpImage, self.powerUpSize/w)

    def randomRowsAndCols(self):
        # get a radom numer for rows and cols
        num = [8,10,12,14,16,18]
        rowsAndCols = random.choice(num)
        self.rows = rowsAndCols
        self.cols = rowsAndCols
    
    def playerRadius(self):
        # get starting radius for player based on number of rows and cols.
        if self.rows == 8:
            self.playerR = 15
        if self.rows == 10:
            self.playerR = 14
        if self.rows == 12:
            self.playerR = 13
        if self.rows == 14:
            self.playerR = 12    
        if self.rows == 16:
            self.playerR = 11
        if self.rows == 18:
            self.playerR = 10

    def appStarted(self):
        self.uBounds = 0
        self.dBounds = 600
        self.lBounds = 0
        self.rBounds = 900
        self.randomRowsAndCols()
        self.cellW = self.rBounds/self.rows
        self.cellH = self.dBounds/self.cols
        self.playerRadius()
        self.playerX = self.cellW/2
        self.playerY = self.cellH/2
        self.loadImages()
        self.powerUps = []
        self.powerUpCounter = 0
        self.ghosts = []
        self.powerUpFreq = 3000
        self.ghostFreq = 10000
        self.ghostMoveFreq = 100
        self.minFreq = 60000
        self.secFreq = 1000
        self.min = 0
        self.sec = 0
        self.timeTillComplete = ""
        self.timerCounter = 0
        self.isFollowing = False
        self.keys = set()
        self.flashlight = False
        self.activateLight = False
        self.lightR = (3/2)*self.playerR
        self.maze = randomMazeLevel3(self.rows, self.cols)

    def modeActivated(self):
        self.appStarted()

    def keyPressed(self, event):
        if event.key == 's':
            self.appStarted()
        if event.key == "Backspace":
            self.app.setActiveMode("infGOver")
        if event.key == "r":
            if self.powerUpCounter >= 3:
                if self.playerR > 7:
                    self.playerR -= 1
                    self.powerUpCounter -= 3
        if event.key == "f" and self.flashlight == False:
            if self.powerUpCounter >= 5:
                self.powerUpCounter -= 5
                self.flashlight = True
        self.keys.add(event.key)
        for key in self.keys:
            if event.key == "Space" and self.flashlight == True:
                self.activateLight = True

    def keyReleased(self, event):
        self.keys.remove(event.key)
        # turns flashlight on and off
        self.activateLight = False

    def mouseMoved(self, event):
        # by clicking on player, enable mouse follow
        if self.isFollowing:
            self.playerX = event.x
            self.playerY = event.y
            # if the player touches the outside boundaries
            if (self.playerX-self.playerR == self.lBounds or
                self.playerX+self.playerR == self.rBounds or
                self.playerY-self.playerR == self.uBounds or
                self.playerY+self.playerR == self.dBounds):
                self.app.setActiveMode('infGOver')
            # when player gets to goal, win
            x0, y0, x1, y1 = self.getCellBounds(self.rows-1, self.cols-1)
            if (self.playerY >= y0 and x0 < self.playerX-self.playerR < x1):
                self.appStarted()
            for row in range(self.rows):
                for col in range(self.cols):
                    self.wallCollision(row, col)

    def onClick(self):
        # toogles the player mouse  follow on or off by clicking on player
        self.isFollowing = not self.isFollowing

    def getMazePath(self):
        # finds the rows and cols of the randomly generated path for the maze
        path = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] == True:
                    path.append((row, col))
        return path

    def spawnPowerUps(self):
        # spawns power-up randomly on maze path
        path = self.getMazePath()
        row, col = random.choice(path)
        if not (row == 0 and col == 0 or row == self.rows-1 and col == self.cols-1):
            cx = col*self.cellW + self.cellW/2
            cy = row*self.cellH + self.cellH/2 
            self.powerUps.append(PowerUps(self, cx, cy, self.powerUpImage))

    def spawnGhosts(self):
        # spawns ghost randomly on maze path
        path = self.getMazePath()
        row, col = random.choice(path)
        if not (row == 0 and col == 0 or row == self.rows-1 and col == self.cols-1):
            ghostCX = col*self.cellW + self.cellW/2
            ghostCY = row*self.cellH + self.cellH/2
            self.ghosts.append(InfiGhosts(self, ghostCX, ghostCY))

    def updatePowerUps(self):
        # gets rid of power-ups that have collided
        notTaken = []
        for powerUp in self.powerUps:
            if powerUp.checkCollision() == False:
                notTaken.append(powerUp)
            else:
                self.powerUpCounter += 1
        self.powerUps = notTaken
    
    def updateGhosts(self):
        # game over when player collides with ghost
        notHit = []
        for ghost in self.ghosts:
            if ghost.checkPlayerCollision():
                self.app.setActiveMode("infGOver")
            else:
                notHit.append(ghost)
        self.ghosts = notHit

    def updateKilledGhosts(self):
        # if a ghost touches the light, it goes away
        if self.activateLight == True:
            for ghost in self.ghosts:
                if ghost.checkLightCollision():
                    self.ghosts.remove(ghost)

    def powUpGhostCollision(self):
        # when a ghost collects a power-up
        for ghost in self.ghosts:
            for powerUp in self.powerUps:
                dist = distance(ghost.ghostCX, ghost.ghostCY, powerUp.cx, powerUp.cy)
                if dist <= ghost.ghostR + powerUp.r:
                    self.powerUps.remove(powerUp)
                    # increase speed and size if collected
                    if ghost.speed < 6:
                        ghost.speed += 1
                    if ghost.ghostR < 15:
                        ghost.ghostR += 1

    def timerFired(self):
        self.updatePowerUps()
        self.updateGhosts()
        self.updateKilledGhosts()
        self.timerCounter += 1
        powerUpLim = self.powerUpFreq/self.timerDelay
        ghostLim = self.ghostFreq/self.timerDelay
        minLim = self.minFreq/self.timerDelay
        secLim = self.secFreq/self.timerDelay
        ghostMoveLim = self.ghostMoveFreq/self.timerDelay
        if self.timerCounter % powerUpLim == 0:
            # spawn power-up every 3 sec
            self.spawnPowerUps()
        if self.timerCounter % ghostLim == 0:
            # spawn ghost every 10 sec
            self.spawnGhosts()
        if self.timerCounter % minLim == 0:
            self.min += 1
            self.sec = 0
        if self.timerCounter % secLim == 0:
            self.sec += 1
        if self.timerCounter % ghostMoveLim == 0:
            for ghost in self.ghosts:
                ghost.followPlayer()
                ghost.getItem()
                self.powUpGhostCollision()

    def updateTime(self):
        # update time till player completes the game.
        if self.sec < 10:
            time = f"{self.min}:0{self.sec}"
        else:
            time = f"{self.min}:{self.sec}"
        self.timeTillComplete = time
        return self.timeTillComplete

    def getCellBounds(self, row, col):
        # gets cell boundaries at given row and col
        x0 = self.cellW*col
        y0 = self.cellH*row
        x1 = x0 + self.cellW
        y1 = y0 + self.cellH
        return x0, y0, x1, y1

    def checkCollision(self, row, col):
        # checks if player if hitting the wall or not
        x0, y0, x1, y1 = self.getCellBounds(row, col)
        if y0 <= self.playerY <= y1:
            if self.playerX > x1:
                if self.playerX-self.playerR <= x1:
                    return True
            if self.playerX < x0: 
                if self.playerX+self.playerR >= x0:
                    return True
        if x0 <= self.playerX <= x1: 
            if self.playerY > y1: 
                if self.playerY-self.playerR <= y1:
                    return True
            if self.playerY < y0: 
                if self.playerY+self.playerR >= y0:
                    return True
        if (self.playerX-self.playerR <= self.lBounds or
            self.playerY-self.playerR <= self.uBounds or 
            self.playerX+self.playerR >= self.rBounds or
            self.playerY+self.playerR >= self.dBounds):
            return True
        return False
    
    def wallCollision(self, row, col):
        if self.maze[row][col] == False:
            if self.checkCollision(row, col) == True:
                self.app.setActiveMode('infGOver')

    def drawMaze(self, canvas):
        # create outer boundary of maze
        x0 = self.lBounds
        y0 = self.uBounds
        x1 = self.rBounds
        y1 = self.dBounds
        canvas.create_rectangle(x0,y0,x1,y1,fill="white", width=3)
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col]:
                    if row == 0 and col == 0:  # when the cell is the start cell
                        color = "light yellow"
                        text = "Start"
                    elif row == self.rows-1 and col == self.cols-1:  # when the cell is the goal cell
                        color = "light yellow"
                        text = "End"
                    else:  # cells with True label
                        color = "light blue"
                        text = ""
                else:  # cells with False label
                    color = "black"
                x0, y0, x1, y1 = self.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)
                canvas.create_text((x0+x1)/2, (y0+y1)/2, text=text)
    
    def drawFlashlight(self, canvas):
        # animate the light from the flashlight
        if self.activateLight == True:
            canvas.create_oval(self.playerX-self.lightR, self.playerY-self.lightR,
                               self.playerX+self.lightR, self.playerY+self.lightR,
                               fill="yellow", width=0)

    def displayPowUpCharge(self, canvas):
        # create the buttons showing the player if the power-up can be used or not
        if self.powerUpCounter < 3: # if not charged
            color = 'light gray'
            text = f"{3-self.powerUpCounter} more" # show how many more power-ups needed to activate
        else: # if charged
            color = 'green'
            text = "CHARGED"
        canvas.create_oval(950-30, 3*self.app.height/5-30, 950+30, 3*self.app.height/5+30,
                                fill=color)
        canvas.create_text(950, 3*self.app.height/5, text=text, font="Arial 8 bold")
        canvas.create_text(950, 3*self.app.height/5+70, text="   'r' to\nSHRINK",
                           font="Arial 10 bold")
        if self.powerUpCounter < 5: # if not charged
            if self.flashlight == False:
                color = "light gray"
                text = f"{5-self.powerUpCounter} more"
            else: # if already in use
                color = "yellow"
                text = "EQUIPPED"
        else: # if charged and not yet used
            if self.flashlight == False:
                color = 'red'
                text = "CHARGED"
            else: # already activated
                color = "yellow"
                text = "EQUIPPED"
        canvas.create_oval(1050-30, 3*self.app.height/5-30, 1050+30, 3*self.app.height/5+30,
                                fill=color)
        canvas.create_text(1050, 3*self.app.height/5, text=text, font="Arial 8 bold")
        canvas.create_text(1000, 9*self.app.height/10, text="Press 'Backspace' to quit", font="Arial 9 bold")
        if self.flashlight == False:
            canvas.create_text(1050, 3*self.app.height/5+70, text="     'f' for\nFLASHLIGHT",
                               font="Arial 10 bold")
        else:
            canvas.create_text(1050, 3*self.app.height/5+70, text="  'Space' to\nTurn on light",
                               font="Arial 10 bold")

    def redrawAll(self, canvas):
        self.drawMaze(canvas)
        for powerUp in self.powerUps:
            powerUp.render(canvas)
        self.drawFlashlight(canvas)
        # draw player
        canvas.create_oval(self.playerX-self.playerR, self.playerY-self.playerR,
                           self.playerX+self.playerR, self.playerY+self.playerR,
                           fill="red", width=0, onClick = self.onClick)
        for ghost in self.ghosts:
            ghost.render(canvas)
        # display the time laps during game
        if 0 <= self.sec < 10:
            time = f"Time:\n{self.min}:0{self.sec}"
        else:
            time = f"Time:\n{self.min}:{self.sec}"
        # show the time and number of power-ups collected
        canvas.create_text(1000, self.app.height/5, text=time, font="Arial 20 bold")
        canvas.create_text(1000, self.app.height/2, 
                           text=f"Power-Up Charge:\n            {self.powerUpCounter}",
                           font="Arial 10 bold")
        self.displayPowUpCharge(canvas)
        
################################################################################
# level 1 -> Go to level 2 if cleared           *Cheat: 's' to skip level
################################################################################
class PlayMode(Mode):
    def loadImages(self):
        # player image
        self.playerSize = 70
        self.playerImage = self.loadImage('images/player.png')
        w,h = self.playerImage.size
        self.playerImage = self.scaleImage(self.playerImage, self.playerSize/w)
        # powerUp image
        self.powerUpSize = 23
        self.powerUpImage = self.loadImage('images/orb.png')
        w,h = self.powerUpImage.size
        self.powerUpImage = self.scaleImage(self.powerUpImage, self.powerUpSize/w)
        # ghost image
        self.ghostSize = 35
        self.ghostImage = self.loadImage('images/ghost.png')
        w,h = self.ghostImage.size
        self.ghostImage = self.scaleImage(self.ghostImage, self.ghostSize/w)

    def appStarted(self):
        self.uBounds = 0
        self.dBounds = 600
        self.lBounds = 0
        self.rBounds = 900
        self.rows = 8
        self.cols = 8
        self.cellW = self.rBounds/self.rows
        self.cellH = self.dBounds/self.cols
        self.playerR = 15
        self.playerX = self.cellW/2
        self.playerY = self.cellH/2
        self.loadImages()
        self.powerUps = []
        self.powerUpCounter = 0
        self.ghosts = []
        self.powerUpFreq = 3000
        self.ghostFreq = 10000
        self.ghostMoveFreq = 100
        self.minFreq = 60000
        self.secFreq = 1000
        self.min = 0
        self.sec = 0
        self.timeTillComplete = ""
        self.timerCounter = 0
        self.isFollowing = False
        self.keys = set()
        self.flashlight = False
        self.activateLight = False
        self.lightR = (3/2)*self.playerR
        self.maze = randomMazeLevel1(self.rows, self.cols)

    def modeActivated(self):
        self.appStarted()  # initialize starting conditions each time new game starts.

    def keyPressed(self, event):
        # skip level
        if event.key == "s":
            self.app.setActiveMode("play2")
        if event.key == "Backspace":
            self.app.setActiveMode("gameOver")
        if event.key == "r":
            if self.powerUpCounter >= 3:
                if self.playerR > 7:
                    self.playerR -= 1
                    self.powerUpCounter -= 3
        if event.key == "f" and self.flashlight == False:
            if self.powerUpCounter >= 5:
                self.powerUpCounter -= 5
                self.flashlight = True
        self.keys.add(event.key)
        for key in self.keys:
            if event.key == "Space" and self.flashlight == True:
                self.activateLight = True

    def keyReleased(self, event):
        self.keys.remove(event.key)
        # turn flashlight on and off
        self.activateLight = False

    def mouseMoved(self, event):
        if self.isFollowing:
            self.playerX = event.x
            self.playerY = event.y
            # if the player touches the outside boundaries
            if (self.playerX-self.playerR == self.lBounds or
                self.playerX+self.playerR == self.rBounds or
                self.playerY-self.playerR == self.uBounds or
                self.playerY+self.playerR == self.dBounds):
                self.app.setActiveMode('gameOver')
            # when player gets to goal, win
            x0, y0, x1, y1 = self.getCellBounds(self.rows-1, self.cols-1)
            if (self.playerY >= y0 and x0 < self.playerX-self.playerR < x1):
                self.app.setActiveMode('play2')
            for row in range(self.rows):
                for col in range(self.cols):
                    self.wallCollision(row, col)


    def onClick(self):
        # toogles the player mouse  follow on or off by clicking on player
        self.isFollowing = not self.isFollowing

    def getMazePath(self):
        # finds the maze path
        path = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] == True:
                    path.append((row, col))
        return path

    def spawnPowerUps(self):
        # spawns power-up randomly on maze path
        path = self.getMazePath()
        row, col = random.choice(path)
        if not (row == 0 and col == 0 or row == self.rows-1 and col == self.cols-1):
            cx = col*self.cellW + self.cellW/2
            cy = row*self.cellH + self.cellH/2 
            self.powerUps.append(PowerUps(self, cx, cy, self.powerUpImage))

    def spawnGhosts(self):
        # spawns ghost randomly on maze path
        path = self.getMazePath()
        row, col = random.choice(path)
        if not (row == 0 and col == 0 or row == self.rows-1 and col == self.cols-1):
            ghostCX = col*self.cellW + self.cellW/2
            ghostCY = row*self.cellH + self.cellH/2
            self.ghosts.append(Ghosts(self, ghostCX, ghostCY, self.ghostImage))

    def updatePowerUps(self):
        # gets rid of power-ups that have collided
        notTaken = []
        for powerUp in self.powerUps:
            if powerUp.checkCollision() == False:
                notTaken.append(powerUp)
            else:
                self.powerUpCounter += 1
        self.powerUps = notTaken
    
    def updateGhosts(self):
        # game over when player collides with ghost
        notHit = []
        for ghost in self.ghosts:
            if ghost.checkPlayerCollision():
                self.app.setActiveMode("gameOver")
            else:
                notHit.append(ghost)
        self.ghosts = notHit

    def updateKilledGhosts(self):
        # remove ghosts that have collided with light
        if self.activateLight == True:
            for ghost in self.ghosts:
                if ghost.checkLightCollision():
                    self.ghosts.remove(ghost)

    def timerFired(self):
        self.updatePowerUps()
        self.updateGhosts()
        self.updateKilledGhosts()
        self.timerCounter += 1
        powerUpLim = self.powerUpFreq/self.timerDelay
        ghostLim = self.ghostFreq/self.timerDelay
        minLim = self.minFreq/self.timerDelay
        secLim = self.secFreq/self.timerDelay
        ghostMoveLim = self.ghostMoveFreq/self.timerDelay
        if self.timerCounter % powerUpLim == 0:
            # spawn power-up every 3 sec
            self.spawnPowerUps()
        if self.timerCounter % ghostLim == 0:
            # spawn ghost every 10 sec
            self.spawnGhosts()
        if self.timerCounter % minLim == 0:
            self.min += 1
            self.sec = 0
        if self.timerCounter % secLim == 0:
            self.sec += 1
        if self.timerCounter % ghostMoveLim == 0:
            for ghost in self.ghosts:
                ghost.followPlayer() # ghost only follows player
            
    def updateTime(self):
        # gets the time it took in total to complete all three levels 
        if self.sec < 10:
            time = f"{self.min}:0{self.sec}"
        else:
            time = f"{self.min}:{self.sec}"
        self.timeTillComplete = time
        return self.timeTillComplete

    def getCellBounds(self, row, col):
        # gets cell boundaries at given row and col
        x0 = self.cellW*col
        y0 = self.cellH*row
        x1 = x0 + self.cellW
        y1 = y0 + self.cellH
        return x0, y0, x1, y1

    def checkCollision(self, row, col):
        # checks collision with player and wall
        x0, y0, x1, y1 = self.getCellBounds(row, col)
        if y0 <= self.playerY <= y1:
            if self.playerX > x1:
                if self.playerX-self.playerR <= x1:
                    return True
            if self.playerX < x0: 
                if self.playerX+self.playerR >= x0:
                    return True
        if x0 <= self.playerX <= x1: 
            if self.playerY > y1: 
                if self.playerY-self.playerR <= y1:
                    return True
            if self.playerY < y0: 
                if self.playerY+self.playerR >= y0:
                    return True
        if (self.playerX-self.playerR <= self.lBounds or
            self.playerY-self.playerR <= self.uBounds or 
            self.playerX+self.playerR >= self.rBounds or
            self.playerY+self.playerR >= self.dBounds):
            return True
        return False
    
    def wallCollision(self, row, col):
        if self.maze[row][col] == False:
            if self.checkCollision(row, col) == True:
                self.app.setActiveMode('gameOver')

    def drawMaze(self, canvas):
        x0 = self.lBounds
        y0 = self.uBounds
        x1 = self.rBounds
        y1 = self.dBounds
        canvas.create_rectangle(x0,y0,x1,y1,fill="white", width=3)
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col]:
                    if row == 0 and col == 0:  # when the cell is the start cell
                        color = "light yellow"
                        text = "Start"
                    elif row == self.rows-1 and col == self.cols-1:  # when the cell is the goal cell
                        color = "light yellow"
                        text = "End"
                    else:  # cells with True label
                        color = "light blue"
                        text = ""
                else:  # cells with False label
                    color = "black"
                x0, y0, x1, y1 = self.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)
                canvas.create_text((x0+x1)/2, (y0+y1)/2, text=text)

    def drawLight(self, canvas):
        if self.activateLight == True:
            canvas.create_oval(self.playerX-self.lightR, self.playerY-self.lightR,
                               self.playerX+self.lightR, self.playerY+self.lightR,
                               fill="yellow", width=0)

    def displayPowerUpCharge(self, canvas):
        if self.powerUpCounter < 3:
            color = 'light gray'
            text = f"{3-self.powerUpCounter} more"
        else:
            color = 'green'
            text = "CHARGED"
        canvas.create_oval(950-30, 3*self.app.height/5-30, 950+30, 3*self.app.height/5+30,
                                fill=color)
        canvas.create_text(950, 3*self.app.height/5, text=text, font="Arial 8 bold")
        canvas.create_text(950, 3*self.app.height/5+70, text="   'r' to\nSHRINK",
                           font="Arial 10 bold")
        if self.powerUpCounter < 5:
            if self.flashlight == False:
                color = "light gray"
                text = f"{5-self.powerUpCounter} more"
            else:
                color = "yellow"
                text = "EQUIPPED"
        else:
            if self.flashlight == False:
                color = 'red'
                text = "CHARGED"
            else:
                color = "yellow"
                text = "EQUIPPED"
        canvas.create_oval(1050-30, 3*self.app.height/5-30, 1050+30, 3*self.app.height/5+30,
                                fill=color)
        canvas.create_text(1050, 3*self.app.height/5, text=text, font="Arial 8 bold")
        canvas.create_text(1000, 9*self.app.height/10, text="Press 'Backspace' to quit", font="Arial 9 bold")
        if self.flashlight == False:
            canvas.create_text(1050, 3*self.app.height/5+70, text="     'f' for\nFLASHLIGHT",
                               font="Arial 10 bold")
        else:
            canvas.create_text(1050, 3*self.app.height/5+70, text="  'Space' to\nTurn on light",
                               font="Arial 10 bold")

    def redrawAll(self, canvas):
        self.drawMaze(canvas)
        for powerUp in self.powerUps:
            powerUp.render(canvas)
        # draw player light if equipped
        self.drawLight(canvas)
        # draw player
        canvas.create_oval(self.playerX-self.playerR, self.playerY-self.playerR,
                           self.playerX+self.playerR, self.playerY+self.playerR,
                           fill="red", width=0, onClick = self.onClick)
        canvas.create_image(self.playerX+2, self.playerY-2, image=ImageTk.PhotoImage(self.playerImage))
        for ghost in self.ghosts:
            ghost.render(canvas)
        # display time laps
        if 0 <= self.sec < 10:
            time = f"Time:\n{self.min}:0{self.sec}"
        else:
            time = f"Time:\n{self.min}:{self.sec}"
        canvas.create_text(1000, self.app.height/5, text=time, font="Arial 20 bold")
        canvas.create_text(1000, self.app.height/2, 
                           text=f"Power-Up Charge:\n            {self.powerUpCounter}",
                           font="Arial 10 bold")
        self.displayPowerUpCharge(canvas)

################################################################################
# level 2 -> Go to level 3 if cleared           *Cheat: 's' to skip level
################################################################################      
class PlayMode2(Mode):
    def loadImages(self):
        # player image
        self.playerSize = 70
        self.playerImage = self.loadImage('images/player.png')
        w,h = self.playerImage.size
        self.playerImage = self.scaleImage(self.playerImage, self.playerSize/w)
        # powerUp image
        self.powerUpSize = 23
        self.powerUpImage = self.loadImage('images/orb.png')
        w,h = self.powerUpImage.size
        self.powerUpImage = self.scaleImage(self.powerUpImage, self.powerUpSize/w)
        # ghost image
        self.ghostSize = 35
        self.ghostImage = self.loadImage('images/ghost.png')
        w,h = self.ghostImage.size
        self.ghostImage = self.scaleImage(self.ghostImage, self.ghostSize/w)

    def appStarted(self):
        self.uBounds = 0
        self.dBounds = 600
        self.lBounds = 0
        self.rBounds = 900
        self.rows = 10
        self.cols = 10
        self.cellW = self.rBounds/self.rows
        self.cellH = self.dBounds/self.cols
        self.playerR = 15
        self.playerX = (self.rows-1)*self.cellW + self.cellW/2
        self.playerY = (self.cols-1)*self.cellH + self.cellH/2
        self.loadImages()
        self.powerUps = []
        self.ghosts = []
        self.powerUpFreq = 3000
        self.ghostFreq = 10000
        self.ghostMoveFreq = 100
        self.timerCounter = 0
        self.play = self.getMode('play')
        self.isFollowing = False
        self.lightR = (3/2)*self.playerR
        self.maze = randomMazeLevel2(self.rows, self.cols)

    def modeActivated(self):
        self.appStarted()  # initialize starting conditions each time new game starts.

    def keyPressed(self, event):
        # skip level
        if event.key == "s":
            self.app.setActiveMode("play3")
        if event.key == "Backspace":
            self.app.setActiveMode("gameOver")
        if event.key == "r":
            if self.play.powerUpCounter >= 3:
                if self.playerR > 7:
                    self.playerR -= 1
                    self.play.powerUpCounter -= 3
        if event.key == "f" and self.play.flashlight == False:
            if self.play.powerUpCounter >= 5:
                self.play.powerUpCounter -= 5
                self.play.flashlight = True
        self.play.keys.add(event.key)
        for key in self.play.keys:
            if event.key == "Space" and self.play.flashlight == True:
                self.play.activateLight = True

    def keyReleased(self, event):
        if event.key == "Space":
            self.play.keys.remove(event.key)
            self.play.activateLight = False

    def mousePressed(self, event):
        pass

    def mouseMoved(self, event):
        if self.isFollowing:
            self.playerX = event.x
            self.playerY = event.y
            # if the player touches the outside boundaries
            if (self.playerX-self.playerR == self.lBounds or
                self.playerX+self.playerR == self.rBounds or
                self.playerY-self.playerR == self.uBounds or
                self.playerY+self.playerR == self.dBounds):
                self.app.setActiveMode('gameOver')
            # when player gets to goal, win
            x0, y0, x1, y1 = self.getCellBounds(0, 0)
            if (self.playerY <= y1 and x0 < self.playerX-self.playerR < x1):
                self.app.setActiveMode('play3')
            for row in range(self.rows):
                for col in range(self.cols):
                    self.wallCollision(row, col)

    def powUpGhostCollision(self):
        # remove power up if ghost collides with it
        for ghost in self.ghosts:
            for powerUp in self.powerUps:
                dist = distance(ghost.ghostCX, ghost.ghostCY, powerUp.cx, powerUp.cy)
                if dist <= ghost.ghostR + powerUp.r:
                    self.powerUps.remove(powerUp)

    def onClick(self):
        # toogles the player mouse  follow on or off by clicking on player
        self.isFollowing = not self.isFollowing

    def getMazePath(self):
        path = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] == True:
                    path.append((row, col))
        return path

    def spawnPowerUps(self):
        # spawns power-up randomly on maze path
        path = self.getMazePath()
        row, col = random.choice(path)
        if not (row == 0 and col == 0 or row == self.rows-1 and col == self.cols-1):
            cx = col*self.cellW + self.cellW/2
            cy = row*self.cellH + self.cellH/2 
            self.powerUps.append(PowerUps(self, cx, cy, self.powerUpImage))

    def spawnGhosts(self):
        # spawns ghost randomly on maze path
        path = self.getMazePath()
        row, col = random.choice(path)
        if not (row == 0 and col == 0 or row == self.rows-1 and col == self.cols-1):
            ghostCX = col*self.cellW + self.cellW/2
            ghostCY = row*self.cellH + self.cellH/2
            self.ghosts.append(SmartBoi(self, ghostCX, ghostCY, self.ghostImage))

    def updatePowerUps(self):
        # gets rid of power-ups that have collided
        notTaken = []
        for powerUp in self.powerUps:
            if powerUp.checkCollision() == False:
                notTaken.append(powerUp)
            else:
                self.play.powerUpCounter += 1
        self.powerUps = notTaken

    def updateGhosts(self):
        # game over when player collides with ghost
        notHit = []
        for ghost in self.ghosts:
            if ghost.checkPlayerCollision():
                self.app.setActiveMode("gameOver")
            else:
                notHit.append(ghost)
        self.ghosts = notHit

    def updateKilledGhosts(self):
        # remove ghost if collides with light
        if self.play.activateLight == True:
            for ghost in self.ghosts:
                if ghost.checkLightCollision():
                    self.ghosts.remove(ghost)

    def timerFired(self):
        self.updatePowerUps()
        self.updateGhosts()
        self.updateKilledGhosts()
        self.play.timerCounter += 1
        powerUpLim = self.powerUpFreq/self.timerDelay
        ghostLim = self.ghostFreq/self.timerDelay
        minLim = self.play.minFreq/self.timerDelay
        secLim = self.play.secFreq/self.timerDelay
        ghostMoveLim = self.ghostMoveFreq/self.timerDelay
        if self.play.timerCounter % powerUpLim == 0:
            # spawn power-up every 3 sec
            self.spawnPowerUps()
        if self.play.timerCounter % ghostLim == 0:
            # spawn ghost every 10 sec
            self.spawnGhosts()
        if self.play.timerCounter % minLim == 0:
            self.play.min += 1
            self.play.sec = 0
        if self.play.timerCounter % secLim == 0:
            self.play.sec += 1
        if self.play.timerCounter % ghostMoveLim == 0:
            # follow the player or get the power up depending on player position
            for ghost in self.ghosts:   
                ghost.followPlayer()
                ghost.getItem()
                self.powUpGhostCollision()

    def updateTime(self):
        # find time laps continuing from level 1
        if self.play.sec < 10:
            time = f"{self.play.min}:0{self.play.sec}"
        else:
            time = f"{self.play.min}:{self.play.sec}"
        self.play.timeTillComplete = time
        return self.play.timeTillComplete

    def getCellBounds(self, row, col):
        # gets cell boundaries at given row and col
        x0 = self.cellW*col
        y0 = self.cellH*row
        x1 = x0 + self.cellW
        y1 = y0 + self.cellH
        return x0, y0, x1, y1

    def checkCollision(self, row, col):
        # check player and wall collision
        x0, y0, x1, y1 = self.getCellBounds(row, col)
        if y0 <= self.playerY <= y1:
            if self.playerX > x1:
                if self.playerX-self.playerR <= x1:
                    return True
            if self.playerX < x0: 
                if self.playerX+self.playerR >= x0:
                    return True
        if x0 <= self.playerX <= x1: 
            if self.playerY > y1: 
                if self.playerY-self.playerR <= y1:
                    return True
            if self.playerY < y0: 
                if self.playerY+self.playerR >= y0:
                    return True
        if (self.playerX-self.playerR <= self.lBounds or
            self.playerY-self.playerR <= self.uBounds or 
            self.playerX+self.playerR >= self.rBounds or
            self.playerY+self.playerR >= self.dBounds):
            return True
        return False
    
    def wallCollision(self, row, col):
        if self.maze[row][col] == False:
            if self.checkCollision(row, col) == True:
                self.app.setActiveMode('gameOver')

    def drawMaze(self, canvas):
        x0 = self.lBounds
        y0 = self.uBounds
        x1 = self.rBounds
        y1 = self.dBounds
        canvas.create_rectangle(x0,y0,x1,y1,fill="white", width=3)
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col]:
                    if row == 0 and col == 0:  # when the cell is the start cell
                        color = "light yellow"
                        text = "End"
                    elif row == self.rows-1 and col == self.cols-1:  # when the cell is the goal cell
                        color = "light yellow"
                        text = "Start"
                    else:  # cells with True label
                        color = "light blue"
                        text = ""
                else:  # cells with False label
                    color = "black"
                x0, y0, x1, y1 = self.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)
                canvas.create_text((x0+x1)/2, (y0+y1)/2, text=text)

    def drawLight(self, canvas):
        if self.play.activateLight == True:
            canvas.create_oval(self.playerX-self.lightR, self.playerY-self.lightR,
                               self.playerX+self.lightR, self.playerY+self.lightR,
                               fill="yellow", width=0)

    def displayPowerUpCharge(self, canvas):
        if self.play.powerUpCounter < 3:
            color = 'light gray'
            text = f"{3-self.play.powerUpCounter} more"
        else:
            color = 'green'
            text = "CHARGED"
        canvas.create_oval(950-30, 3*self.app.height/5-30, 950+30, 3*self.app.height/5+30,
                                fill=color)
        canvas.create_text(950, 3*self.app.height/5, text=text, font="Arial 8 bold")
        canvas.create_text(950, 3*self.app.height/5+70, text="   'r' to\nSHRINK",
                           font="Arial 10 bold")
        if self.play.powerUpCounter < 5:
            if self.play.flashlight == False:
                color = "light gray"
                text = f"{5-self.play.powerUpCounter} more"
            else:
                color = "yellow"
                text = "EQUIPPED"
        else:
            if self.play.flashlight == False:
                color = 'red'
                text = "CHARGED"
            else:
                color = "yellow"
                text = "EQUIPPED"
        canvas.create_oval(1050-30, 3*self.app.height/5-30, 1050+30, 3*self.app.height/5+30,
                                fill=color)
        canvas.create_text(1050, 3*self.app.height/5, text=text, font="Arial 8 bold")
        canvas.create_text(1000, 9*self.app.height/10, text="Press 'Backspace' to quit", font="Arial 9 bold")
        if self.play.flashlight == False:
            canvas.create_text(1050, 3*self.app.height/5+70, text="     'f' for\nFLASHLIGHT",
                               font="Arial 10 bold")
        else:
            canvas.create_text(1050, 3*self.app.height/5+70, text="  'Space' to\nTurn on light",
                               font="Arial 10 bold")

    def redrawAll(self, canvas):
        self.drawMaze(canvas)
        for powerUp in self.powerUps:
            powerUp.render(canvas)
        self.drawLight(canvas)
        # draw player
        canvas.create_oval(self.playerX-self.playerR, self.playerY-self.playerR,
                           self.playerX+self.playerR, self.playerY+self.playerR,
                           fill="red", width=0, onClick = self.onClick)
        canvas.create_image(self.playerX+2, self.playerY-2, image=ImageTk.PhotoImage(self.playerImage))
        for ghost in self.ghosts:
            ghost.render(canvas)
        # display time laps
        if 0 <= self.play.sec < 10:
            time = f"Time:\n{self.play.min}:0{self.play.sec}"
        else:
            time = f"Time:\n{self.play.min}:{self.play.sec}"
        canvas.create_text(1000, self.app.height/5, text=time, font="Arial 20 bold")
        canvas.create_text(1000, self.app.height/2, 
                           text=f"Power-Up Charge:\n            {self.play.powerUpCounter}",
                           font="Arial 10 bold")
        self.displayPowerUpCharge(canvas)

################################################################################
# Level 3 -> Go to win mode if cleared          *Cheat: 's' to automatically win
################################################################################
class PlayMode3(Mode):
    def loadImages(self):
        # player image
        self.playerSize = 70
        self.playerImage = self.loadImage('images/player.png')
        w,h = self.playerImage.size
        self.playerImage = self.scaleImage(self.playerImage, self.playerSize/w)
        # powerUp image
        self.powerUpSize = 23
        self.powerUpImage = self.loadImage('images/orb.png')
        w,h = self.powerUpImage.size
        self.powerUpImage = self.scaleImage(self.powerUpImage, self.powerUpSize/w)
        # ghost image
        self.ghostSize = 35
        self.ghostImage = self.loadImage('images/ghost.png')
        w,h = self.ghostImage.size
        self.ghostImage = self.scaleImage(self.ghostImage, self.ghostSize/w)

    def appStarted(self):
        self.uBounds = 0
        self.dBounds = 600
        self.lBounds = 0
        self.rBounds = 900
        self.rows = 12
        self.cols = 12
        self.cellW = self.rBounds/self.rows
        self.cellH = self.dBounds/self.cols
        self.playerR = 15
        self.playerX = self.cellW/2
        self.playerY = self.cellH/2
        self.loadImages()
        self.powerUps = []
        self.ghosts = []
        self.powerUpFreq = 3000
        self.ghostFreq = 10000
        self.ghostMoveFreq = 100
        self.timerCounter = 0
        self.play = self.getMode('play')
        self.isFollowing = False
        self.lightR = (3/2)*self.playerR
        self.maze = randomMazeLevel3(self.rows, self.cols)

    def modeActivated(self):
        self.appStarted()  # initialize starting conditions each time new game starts.

    def keyPressed(self, event):
        # skip level/automatic win
        if event.key == "s":
            self.app.setActiveMode("win")
        if event.key == "Backspace":
            self.app.setActiveMode("gameOver")
        if event.key == "r":
            if self.play.powerUpCounter >= 3:
                if self.playerR > 7:
                    self.playerR -= 1
                    self.play.powerUpCounter -= 3
        if event.key == "f" and self.play.flashlight == False:
            if self.play.powerUpCounter >= 5:
                self.play.powerUpCounter -= 5
                self.play.flashlight = True
        self.play.keys.add(event.key)
        for key in self.play.keys:
            if event.key == "Space" and self.play.flashlight == True:
                self.play.activateLight = True

    def keyReleased(self, event):
        self.play.keys.remove(event.key)
        self.play.activateLight = False

    def mousePressed(self, event):
        pass

    def mouseMoved(self, event):
        if self.isFollowing:
            self.playerX = event.x
            self.playerY = event.y
            # if the player touches the outside boundaries
            if (self.playerX-self.playerR == self.lBounds or
                self.playerX+self.playerR == self.rBounds or
                self.playerY-self.playerR == self.uBounds or
                self.playerY+self.playerR == self.dBounds):
                self.app.setActiveMode('jumpscare')
            # when player gets to goal, win
            x0, y0, x1, y1 = self.getCellBounds(self.rows-1, self.cols-1)
            if (self.playerY <= y1 and x0 < self.playerX-self.playerR < x1):
                self.app.setActiveMode('win')
            for row in range(self.rows):
                for col in range(self.cols):
                    # if player collides with wall, game over
                    self.wallCollision(row, col)

    def powUpGhostCollision(self):
        # check if ghost collides with power-up
        for ghost in self.ghosts:
            for powerUp in self.powerUps:
                dist = distance(ghost.ghostCX, ghost.ghostCY, powerUp.cx, powerUp.cy)
                if dist <= ghost.ghostR + powerUp.r:
                    self.powerUps.remove(powerUp)
                    if ghost.speed < 6:
                        ghost.speed += 1

    def onClick(self):
        # toogles the player mouse  follow on or off by clicking on player
        self.isFollowing = not self.isFollowing

    def getMazePath(self):
        path = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] == True:
                    path.append((row, col))
        return path

    def spawnPowerUps(self):
        # spawns power-up randomly on maze path
        path = self.getMazePath()
        row, col = random.choice(path)
        if not (row == 0 and col == 0 or row == self.rows-1 and col == self.cols-1):
            cx = col*self.cellW + self.cellW/2
            cy = row*self.cellH + self.cellH/2 
            self.powerUps.append(PowerUps(self, cx, cy, self.powerUpImage))

    def spawnGhosts(self):
        # spawns ghost randomly on maze path
        path = self.getMazePath()
        row, col = random.choice(path)
        if not (row == 0 and col == 0 or row == self.rows-1 and col == self.cols-1):
            ghostCX = col*self.cellW + self.cellW/2
            ghostCY = row*self.cellH + self.cellH/2
            self.ghosts.append(SmartBoi2(self, ghostCX, ghostCY, self.ghostImage))

    def updatePowerUps(self):
        # gets rid of power-ups that have collided
        notTaken = []
        for powerUp in self.powerUps:
            if powerUp.checkCollision() == False:
                notTaken.append(powerUp)
            else:
                self.play.powerUpCounter += 1
        self.powerUps = notTaken

    def updateGhosts(self):
        # game over when player collides with ghost
        notHit = []
        for ghost in self.ghosts:
            if ghost.checkPlayerCollision():
                self.app.setActiveMode("jumpscare")
            else:
                notHit.append(ghost)
        self.ghosts = notHit

    def updateKilledGhosts(self):
        # remove ghosts that collided with light
        if self.play.activateLight == True:
            for ghost in self.ghosts:
                if ghost.checkLightCollision():
                    self.ghosts.remove(ghost)

    def timerFired(self):
        self.updatePowerUps()
        self.updateGhosts()
        self.updateKilledGhosts()
        self.play.timerCounter += 1
        powerUpLim = self.powerUpFreq/self.timerDelay
        ghostLim = self.ghostFreq/self.timerDelay
        minLim = self.play.minFreq/self.timerDelay
        secLim = self.play.secFreq/self.timerDelay
        ghostMoveLim = self.ghostMoveFreq/self.timerDelay
        if self.play.timerCounter % powerUpLim == 0:
            # spawn power-up every 3 sec
            self.spawnPowerUps()
        if self.play.timerCounter % ghostLim == 0:
            # spawn ghost every 10 sec
            self.spawnGhosts()
        if self.play.timerCounter % minLim == 0:
            self.play.min += 1
            self.play.sec = 0
        if self.play.timerCounter % secLim == 0:
            self.play.sec += 1
        if self.play.timerCounter % ghostMoveLim == 0:
            for ghost in self.ghosts:
                # follow player or get power-up based on player position
                ghost.followPlayer()
                ghost.getItem()
                self.powUpGhostCollision()

    def updateTime(self):
        # get time laps continuing from level 2
        if self.play.sec < 10:
            time = f"{self.play.min}:0{self.play.sec}"
        else:
            time = f"{self.play.min}:{self.play.sec}"
        self.play.timeTillComplete = time
        return self.play.timeTillComplete

    def getCellBounds(self, row, col):
        # gets cell boundaries at given row and col
        x0 = self.cellW*col
        y0 = self.cellH*row
        x1 = x0 + self.cellW
        y1 = y0 + self.cellH
        return x0, y0, x1, y1

    def checkCollision(self, row, col):
        # check collision of player and wall
        x0, y0, x1, y1 = self.getCellBounds(row, col)
        if y0 <= self.playerY <= y1:
            if self.playerX > x1:
                if self.playerX-self.playerR <= x1:
                    return True
            if self.playerX < x0: 
                if self.playerX+self.playerR >= x0:
                    return True
        if x0 <= self.playerX <= x1: 
            if self.playerY > y1: 
                if self.playerY-self.playerR <= y1:
                    return True
            if self.playerY < y0: 
                if self.playerY+self.playerR >= y0:
                    return True
        if (self.playerX-self.playerR <= self.lBounds or
            self.playerY-self.playerR <= self.uBounds or 
            self.playerX+self.playerR >= self.rBounds or
            self.playerY+self.playerR >= self.dBounds):
            return True
        return False
    
    def wallCollision(self, row, col):
        if self.maze[row][col] == False:
            if self.checkCollision(row, col) == True:
                self.app.setActiveMode('jumpscare')

    def drawMaze(self, canvas):
        x0 = self.lBounds
        y0 = self.uBounds
        x1 = self.rBounds
        y1 = self.dBounds
        canvas.create_rectangle(x0,y0,x1,y1,fill="white", width=3)
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col]:
                    if row == 0 and col == 0:  # when the cell is the start cell
                        color = "light yellow"
                        text = "Start"
                    elif row == self.rows-1 and col == self.cols-1:  # when the cell is the goal cell
                        color = "light yellow"
                        text = "End"
                    else:  # cells with True label
                        color = "light blue"
                        text = ""
                else:  # cells with False label
                    color = "black"
                x0, y0, x1, y1 = self.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)
                canvas.create_text((x0+x1)/2, (y0+y1)/2, text=text)

    def drawLight(self, canvas):
        if self.play.activateLight == True:
            canvas.create_oval(self.playerX-self.lightR, self.playerY-self.lightR,
                               self.playerX+self.lightR, self.playerY+self.lightR,
                               fill="yellow", width=0)

    def displayPowerUpCharge(self, canvas):
        if self.play.powerUpCounter < 3:
            color = 'light gray'
            text = f"{3-self.play.powerUpCounter} more"
        else:
            color = 'green'
            text = "CHARGED"
        canvas.create_oval(950-30, 3*self.app.height/5-30, 950+30, 3*self.app.height/5+30,
                                fill=color)
        canvas.create_text(950, 3*self.app.height/5, text=text, font="Arial 8 bold")
        canvas.create_text(950, 3*self.app.height/5+70, text="   'r' to\nSHRINK",
                           font="Arial 10 bold")
        if self.play.powerUpCounter < 5:
            if self.play.flashlight == False:
                color = "light gray"
                text = f"{5-self.play.powerUpCounter} more"
            else:
                color = "yellow"
                text = "EQUIPPED"
        else:
            if self.play.flashlight == False:
                color = 'red'
                text = "CHARGED"
            else:
                color = "yellow"
                text = "EQUIPPED"
        canvas.create_oval(1050-30, 3*self.app.height/5-30, 1050+30, 3*self.app.height/5+30,
                                fill=color)
        canvas.create_text(1050, 3*self.app.height/5, text=text, font="Arial 8 bold")
        canvas.create_text(1000, 9*self.app.height/10, text="Press 'Backspace' to quit", font="Arial 9 bold")
        if self.play.flashlight == False:
            canvas.create_text(1050, 3*self.app.height/5+70, text="     'f' for\nFLASHLIGHT",
                               font="Arial 10 bold")
        else:
            canvas.create_text(1050, 3*self.app.height/5+70, text="  'Space' to\nTurn on light",
                               font="Arial 10 bold")

    def redrawAll(self, canvas):
        self.drawMaze(canvas)
        for powerUp in self.powerUps:
            powerUp.render(canvas)
        self.drawLight(canvas)
        # draw player
        canvas.create_oval(self.playerX-self.playerR, self.playerY-self.playerR,
                           self.playerX+self.playerR, self.playerY+self.playerR,
                           fill="red", width=0, onClick = self.onClick)
        canvas.create_image(self.playerX+2, self.playerY-2, image=ImageTk.PhotoImage(self.playerImage))
        for ghost in self.ghosts:
            ghost.render(canvas)
        # display time laps
        if 0 <= self.play.sec < 10:
            time = f"Time:\n{self.play.min}:0{self.play.sec}"
        else:
            time = f"Time:\n{self.play.min}:{self.play.sec}"
        canvas.create_text(1000, self.app.height/5, text=time, font="Arial 20 bold")
        canvas.create_text(1000, self.app.height/2, 
                           text=f"Power-Up Charge:\n            {self.play.powerUpCounter}",
                           font="Arial 10 bold")
        self.displayPowerUpCharge(canvas)

################################################################################
# If all 3 levels passed
################################################################################
class WinMode(Mode):
    def appStarted(self):
        self.play = self.getMode('play')
        self.play2 = self.getMode('play2')
        self.play3 = self.getMode('play3')
        self.scores = self.getMode('scores')
        self.title = 'Congrats, you won!'
        # background image
        self.backgroundSize = 1100
        self.backgroundImage = self.loadImage('images/fireworks.jpg')
        w,h = self.backgroundImage.size
        self.backgroundImage = self.scaleImage(self.backgroundImage, self.backgroundSize/w)

    def modeActivated(self):
        self.play.updateTime()
    
    def onClickHome(self):
        self.app.setActiveMode('start')

    def onClickScoreBoard(self):
        self.app.setActiveMode('scores')
    
    def onClickPlay(self):
        self.app.setActiveMode('play')

    def redrawAll(self, canvas):
        # insert background pic
        canvas.create_image(self.app.width/2, self.app.height/2, image=ImageTk.PhotoImage(self.backgroundImage))
        canvas.create_text(self.app.width/2, self.app.height/3, 
                           text=self.title, fill='white', font="Times 80 bold")
        # home button
        canvas.create_rectangle((self.app.width/4-40), (2*self.app.height/3-20),
                                (self.app.width/4+40), (2*self.app.height/3+20),
                                fill="orange", onClick=self.onClickHome)
        canvas.create_text(self.app.width/4, 2*self.app.height/3, font="Times 10 bold", text="HOME")
        # play button
        canvas.create_rectangle((3*self.app.width/4-40), (2*self.app.height/3-20),
                                (3*self.app.width/4+40), (2*self.app.height/3+20),
                                fill="pink", onClick=self.onClickPlay)
        canvas.create_text(3*self.app.width/4, 2*self.app.height/3, font="Times 10 bold", text="PLAY AGAIN")
        # Scoreboard button
        canvas.create_rectangle((self.app.width/2-40), (4*self.app.height/5-20),
                                (self.app.width/2+40), (4*self.app.height/5+20),
                                fill="light blue", onClick=self.onClickScoreBoard)
        canvas.create_text(self.app.width/2, 4*self.app.height/5, font="Times 8 bold", text="SCOREBOARD")
        # display player time till completed
        canvas.create_text(self.app.width/2, self.app.height/2, 
                           text="Time: " + self.play.timeTillComplete, fill='White',
                           font="Times 20 bold")

################################################################################
# If fail to pass level 1 or 2
################################################################################
class GameOverMode(Mode):
    def appStarted(self):
        self.title = "Game Over"
        # background image
        self.backgroundSize = 1100
        self.backgroundImage = self.loadImage('images/black.jpg')
        w,h = self.backgroundImage.size
        self.backgroundImage = self.scaleImage(self.backgroundImage, self.backgroundSize/w)

    def onClickPlay(self):
        self.app.setActiveMode('play')

    def onClickHome(self):
        self.app.setActiveMode('start')
        
    def redrawAll(self, canvas):
        canvas.create_image(self.app.width/2, self.app.height/2, image=ImageTk.PhotoImage(self.backgroundImage))
        canvas.create_text(self.app.width/2, self.app.height/2, 
                           text=self.title, fill="white", font="Times 70 bold")
        # home button
        canvas.create_rectangle((4*self.app.width/5-40), (5*self.app.height/6-20),
                                (4*self.app.width/5+40), (5*self.app.height/6+20),
                                fill="orange", onClick=self.onClickHome)
        canvas.create_text(4*self.app.width/5, 5*self.app.height/6, font="Chiller 11 bold", text="HOME")
        # play button
        canvas.create_rectangle((self.app.width/5-40), (5*self.app.height/6-20),
                                (self.app.width/5+40), (5*self.app.height/6+20),
                                fill="pink", onClick=self.onClickPlay)
        canvas.create_text(self.app.width/5, 5*self.app.height/6, font="Chiller 11 bold", text="PLAY AGAIN")

################################################################################
# If fail to pass level3
################################################################################
class Jumpscare(Mode):
    def appStarted(self):
        self.title = "BOOOOO!!!      GOT'EEEM"
        # background image
        self.backgroundSize = 1100
        self.backgroundImage = self.loadImage('images/jumpscare.jpg')
        w,h = self.backgroundImage.size
        self.backgroundImage = self.scaleImage(self.backgroundImage, self.backgroundSize/w)

    def onClickPlay(self):
        self.app.setActiveMode('play')

    def onClickHome(self):
        self.app.setActiveMode('start')

    def redrawAll(self, canvas):
        canvas.create_image(self.app.width/2, self.app.height/2, image=ImageTk.PhotoImage(self.backgroundImage))
        canvas.create_text(self.app.width/2, 11*self.app.height/12, 
                           text=self.title, fill="red2", font="Chiller 40 bold")
        # home button
        canvas.create_rectangle((4*self.app.width/5-40), (5*self.app.height/6-20),
                                (4*self.app.width/5+40), (5*self.app.height/6+20),
                                fill="orange", onClick=self.onClickHome)
        canvas.create_text(4*self.app.width/5, 5*self.app.height/6, font="Chiller 11 bold", text="HOME")
        # play button
        canvas.create_rectangle((self.app.width/5-40), (5*self.app.height/6-20),
                                (self.app.width/5+40), (5*self.app.height/6+20),
                                fill="pink", onClick=self.onClickPlay)
        canvas.create_text(self.app.width/5, 5*self.app.height/6, font="Chiller 11 bold", text="PLAY AGAIN")

################################################################################
# Infinite Mode Game Over
################################################################################
class InfiGameOver(Mode):
    # game over screen for infinite mode
    def appStarted(self):
        self.title = "Game Over"
        # background image
        self.backgroundSize = 1100
        self.backgroundImage = self.loadImage('images/black.jpg')
        w,h = self.backgroundImage.size
        self.backgroundImage = self.scaleImage(self.backgroundImage, self.backgroundSize/w)

    def onClickPlay(self):
        self.app.setActiveMode('inf')

    def onClickHome(self):
        self.app.setActiveMode('start')
        
    def redrawAll(self, canvas):
        canvas.create_image(self.app.width/2, self.app.height/2, image=ImageTk.PhotoImage(self.backgroundImage))
        canvas.create_text(self.app.width/2, self.app.height/2, 
                           text=self.title, fill="white", font="Times 70 bold")
        # home button
        canvas.create_rectangle((self.app.width/3-40), (4*self.app.height/5-20),
                                (self.app.width/3+40), (4*self.app.height/5+20),
                                fill="orange", onClick=self.onClickHome)
        canvas.create_text(self.app.width/3, 4*self.app.height/5, font="Chiller 11 bold", text="HOME")
        # play button
        canvas.create_rectangle((2*self.app.width/3-40), (4*self.app.height/5-20),
                                (2*self.app.width/3+40), (4*self.app.height/5+20),
                                fill="pink", onClick=self.onClickPlay)
        canvas.create_text(2*self.app.width/3, 4*self.app.height/5, font="Chiller 11 bold", text="PLAY AGAIN")

################################################################################
# Scoreboard screen
################################################################################
class Scoreboard(Mode):
    # create scoreboard by storing player time into txt file
    def appStarted(self):
        self.play = self.getMode('play')
        self.play2 = self.getMode('play2')
        self.play3 = self.getMode('play3')
        self.start = self.getMode('start')
        self.title = "Scoreboard"
        self.score = ""
        # background image
        self.backgroundSize = 1100
        self.backgroundImage = self.loadImage('images/scoreboard.jpg')
        w,h = self.backgroundImage.size
        self.backgroundImage = self.scaleImage(self.backgroundImage, self.backgroundSize/w)

    def onClick(self):
        self.app.setActiveMode('start')
    
    def modeActivated(self):
        self.play.updateTime()
        self.createBoard()

    def createBoard(self):
        # read and rewrite scoreboard.txt
        self.score = readFile('scoreboard.txt')
        if len(self.score) == 0:
            writeFile('scoreboard.txt', self.play.timeTillComplete)
        else:
            if int(self.score[0]) > int(self.play.timeTillComplete[0]):
                writeFile('scoreboard.txt', self.play.timeTillComplete)
            elif int(self.score[0]) == int(self.play.timeTillComplete[0]):
                if int(self.score[2:]) > int(self.play.timeTillComplete[2:]):
                    writeFile('scoreboard.txt', self.play.timeTillComplete)
                else:
                    writeFile('scoreboard.txt', self.score)

    def redrawAll(self, canvas):
        canvas.create_image(self.app.width/2, self.app.height/2, image=ImageTk.PhotoImage(self.backgroundImage))
        canvas.create_text(self.app.width/2, 40, text=self.title, 
                           font="Times 50 bold")
        # home button
        canvas.create_rectangle(self.app.width/2-40, 4*self.app.height/5-20, 
                                self.app.width/2+40, 4*self.app.height/5+20,
                                fill='red', onClick=self.onClick)
        canvas.create_text(self.app.width/2, 4*self.app.height/5, text="HOME", font='Times 10 bold')
        # display best time
        canvas.create_text(self.app.width/2, 5*self.app.height/12, 
                           text="Best Time: " + self.score, font="Times 40 bold")

################################################################################
# Set up environment, run game
################################################################################
class Game(ModalApp):
    def appStarted(self):
        """Initializes the modes in the game."""
        self.addMode(PlayMode(name="play"))
        self.addMode(PlayMode2(name='play2'))
        self.addMode(PlayMode3(name='play3'))
        self.addMode(StartMode(name="start"))
        self.addMode(Instructions(name='instr'))
        self.addMode(Scoreboard(name="scores"))
        self.addMode(InfiniteMode(name='inf'))
        self.addMode(InfiGameOver(name='infGOver'))
        self.addMode(GameOverMode(name="gameOver"))
        self.addMode(Jumpscare(name='jumpscare'))
        self.addMode(WinMode(name="win"))
        self.setActiveMode("start")

Game(width=1100, height=600)
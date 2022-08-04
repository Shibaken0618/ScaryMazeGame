################################################################################
# Functions for generating random mazes.
# level 1 being the most simple to level 3 being the most complex.
################################################################################
import random

# random maze generation for level 1
def randomMazeLevel1(rows, cols):
    # initialize board as a board with rows x cols falses 
    # maze level 1 would have 2 vertical block and 2 horizontal blocks 
    # combined as one path.
    board = [[False for i in range(rows)] for j in range(cols)]
    randomRow = []
    randomCol = []
    for i in range(rows//2):
        randomRow.append(i)
    for j in range(1,cols//2):
        randomCol.append(j)
    rand1 = random.choice(randomRow)
    rand2 = random.choice(randomCol)
    # (0,0) to (rand1, 0)
    for row in range(rand1+1):
        for col in range(0,2):
            board[row][col] = True
    # (rand1,1) to (rand1, rand2)
    for col in range(2,rand2+1):
        board[rand1][col] = True     
     # (rand1,rand2+1) to (rows, rand2+1)
    for row in range(rand1, rows):
        board[row][rand2] = True
    # (rows, rand2+1) to (rows, cols)
    for col in range(rand2+1, cols):
        board[rows-1][col] = True         
    return board

# random maze generation for level 2
def randomMazeLevel2(rows, cols):
    # same as random maze level 1, but with 2 vertical blocks and 3 horizontal blocks
    board = [[False for i in range(rows)] for j in range(cols)]
    randomRow1 = []
    randomCol1 = []
    randomRow2 = []
    randomCol2 = []
    for i in range(cols//3+1): # if cols = 10: 0,1,2
        randomCol1.append(i) 
    for j in range(rows//3+1): # if rows = 10: 0,1,2
        randomRow1.append(j)
    for k in range(cols//3+1, 2*cols//3+1): # if cols = 10: 3,4,5
        randomCol2.append(k)
    for l in range(rows//3+1, 2*rows//3+1): # if rows = 10: 3,4,5
        randomRow2.append(l)
    rand1 = random.choice(randomCol1) # 0,1,2
    rand2 = random.choice(randomRow1) # 0,1,2
    rand3 = random.choice(randomCol2) # 3,4,5
    # (0,0) to (0, rand1)
    for col in range(rand1+1):
        board[0][col] = True
    # (0,rand1+1) to (rand2, rand1+1)
    for row in range(rand2+1):
        board[row][rand1] = True     
     # (rand2,rand1+2) to (rand2, rand3)
    for col in range(rand1+1, rand3+1):
        board[rand2][col] = True
    # (rand2, rand3+1) to (rows, rand3+1)
    for row in range(rand2, rows):
        board[row][rand3] = True
    # (rows, rand3+2) to (rows, cols)
    for col in range(rand3+1, cols):
        board[rows-1][col] = True    
    return board

# random maze generation for level 3
def randomMazeLevel3(rows, cols):
    #same as random maze 1 and 2, but with 3 vertical and horizontal blocks 
    board = [[False for i in range(rows)] for j in range(cols)]
    randomRow1 = []
    randomCol1 = []
    randomRow2 = []
    randomCol2 = []
    for i in range(rows//3): # if cols = 12: 0,1,2,3
        randomRow1.append(i) 
    for j in range(cols//3): # if rows = 12: 0,1,2,3
        randomCol1.append(j)
    for k in range(rows//3, 2*rows//3): # if cols = 12: 4,5,6,7
        randomRow2.append(k)
    for l in range(cols//3, 2*cols//3): # if rows = 12: 4,5,6,7
        randomCol2.append(l)
    rand1 = random.choice(randomRow1) # 0,1,2,3
    rand2 = random.choice(randomCol1) # 0,1,2,3
    rand3 = random.choice(randomRow2) # 4,5,6,7
    rand4 = random.choice(randomCol2) # 4,5,6,7
    # (0,0) to (rand1, o)
    for row in range(rand1+1):
        board[row][0] = True
    # (rand1, 1) to (rand1, rand2)
    for col in range(1,rand2+1):
        board[rand1][col] = True     
     # (rand1,rand2+1) to (rand3, rand2+1)
    for row in range(rand1+1, rand3+1):
        board[row][rand2] = True
    # (rand3, rand2+1) to (rand3, rand4)
    for col in range(rand2+1, rand4+1):
        board[rand3][col] = True
    # (rand3, rand4+1) to (rows, rand4+1)
    for row in range(rand3+1, rows):
        board[row][rand4] = True    
    for col in range(rand4+1, cols):
        board[rows-1][col] = True
    return board
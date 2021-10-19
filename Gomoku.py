#Import modules and libraries
from random import randint
from string import ascii_uppercase, ascii_lowercase
from itertools import permutations

#Define board mapping function
def mapBoard(col, row, value):
    board = [[value for x in range(col)] for y in range(row)]
    return board

#Define metaboard mapping function
def mapMetaBoard(col, row):
    metaboard = [[[[0, 0, 0, 0], [0, 0, 0, 0]] for x in range(col)] for y in range(row)]
    return metaboard

#Define view board function
def viewBoard(board):
    alphabet = ascii_uppercase
    col = len(board[0])
    row = len(board)
    border = ""
    topBorder = "#||"
    for i in range(col):
        border += "_" * 2
        topBorder += alphabet[i]
        topBorder += " "
    border += "___"
    print(topBorder)
    print(border)
    for i in range(row):
        print(alphabet[i] + "||" + " ".join(board[i]) + "|")

#Define mark function
def mark(board, signature):
    alphabet = ascii_uppercase
    alphabet1 = ascii_lowercase
    dimensionY = len(board)
    dimensionX = len(board[0])
    valid = False
    while (not valid):
        print("\n\nWhere do you want to mark?\n\n")
        x = input(f"Column (A - {alphabet[dimensionX - 1]})? ")
        y = input(f"Row (A - {alphabet[dimensionY - 1]})? ")
        try:
            x = alphabet.index(x)
            y = alphabet.index(y)
        except ValueError:
            x = alphabet1.index(x)
            y = alphabet1.index(y)
        if (board[y][x] == ' '):
            valid = True
        else:
            print('That position has already been marked. Please try again.\n')
    board[y][x] = signature
    print('\n')
    viewBoard(board)

#Define function to find all occurences of 'X'
#Value is [opponentSignature]
#Return [[col1, row1], [col2, row2], ...]
def locate(value, board):
    dimensionY = len(board)
    dimensionX = len(board[0])

    returnList = []
    for row in range(dimensionY):
        for col in range(dimensionX):
            if (board[row][col] in value): returnList.append([col, row])
    
    return returnList

#Define computer's turn
def play(board, selfSignature, opponentSignature, difficulty):

    #AI
    #Each of metaboard's position is a list [danger, opportunity]
    #Define function to update metaboard
    def meta(board, opponentSignature, selfSignature, winCond, difficulty):

        #Define function to sweep perimeter of a position's coordinates and add attributes to them
        #coord = [col, row]
        def sweep(metaboard, coord, keyword, opponentSignature, selfSignature, winCond):
            if (keyword == 'danger'):
                type = 0
                otherType = 1
                signature = opponentSignature
            else:
                type = 1
                otherType = 0
                signature = selfSignature
            coordVars = list(permutations([-1, 0, 1], 2))
            coordVars.extend(((-1, -1), (1, 1)))
            for coordVar in coordVars:
                try:
                    if (coordVar in [(-1, -1), (1, 1)]):
                        pos = 2
                    elif (coordVar in [(0, -1), (0, 1)]):
                        pos = 0
                    elif (coordVar in [(-1, 0), (1, 0)]):
                        pos = 1
                    else:
                        pos = 3
                    row = coord[1] + coordVar[0]
                    if (row < 0 or row > len(metaboard)): raise IndexError
                    col = coord[0] + coordVar[1]
                    if (col < 0 or col > len(metaboard[0])): raise IndexError
                    #Ripple effect
                    if (not isinstance(metaboard[row][col], str)):
                        for i in range(winCond - 1):
                            if (not isinstance(metaboard[row][col], str)):
                                metaboard[row][col][type][pos] += (1 - i/(winCond - 1))
                                metaboard[row][col][otherType][pos] -= (1 - i/(winCond - 1))
                                row += coordVar[0]
                                if (row < 0 or row > len(metaboard)): raise IndexError
                                col += coordVar[1]
                                if (col < 0 or col > len(metaboard[0])): raise IndexError
                            elif (metaboard[row][col] == signature):
                                row += coordVar[0]
                                if (row < 0 or row > len(metaboard)): raise IndexError
                                col += coordVar[1]
                                if (col < 0 or col > len(metaboard[0])): raise IndexError
                            else:
                                raise IndexError
                        #alphabet = ascii_uppercase
                        #print(f'Metaboard at column {alphabet[col]} and row {alphabet[row]} has a {keyword} level of {metaboard[row][col][type]}.')
                    #Resonance effect
                    if (metaboard[row][col] == signature):
                        alignment = 0
                        while (metaboard[row][col] == signature):
                            row += coordVar[0]
                            if (row < 0 or row > len(metaboard)): raise IndexError
                            col += coordVar[1]
                            if (col < 0 or col > len(metaboard[0])): raise IndexError
                            alignment += 1
                        if (isinstance(metaboard[row][col], list)):
                            metaboard[row][col][type][pos] += alignment
                except IndexError: pass

        #Define function to screen entire metaboard for invalidation
        def screen(metaboard, selfSignature, opponentSignature, winCond):

            #Define function to rotate board 90 degree counter-clockwise with perspective to keeping OG board intact
            def rotate(board):
                #Define function to inverse board vertically
                def invertY(board):
                    invertYBoard = []
                    dimensionY = len(board)
                    for row in range(dimensionY):
                        invertYBoard.append(board[dimensionY - row - 1])
                    return invertYBoard
                rotateBoard = []
                dimensionY = len(board)
                dimensionX = len(board[0])
                for col in range(dimensionX):
                    column = [board[row][col] for row in range(dimensionY)]
                    rotateBoard.append(column)
                return invertY(rotateBoard)

            #Define function to screen the top left corner of the board
            def screenTopLeftCorner(metaboard, winCond, pos, name):
                for row in range(winCond - 1):
                    for col in range(winCond - 1 - row):
                        if (isinstance(metaboard[row][col], list)):
                            #print(f'nullify {row}:{col}\'s danger and potential in the {name} diagonal')
                            metaboard[row][col][0][pos] = 0
                            metaboard[row][col][1][pos] = 0

            #Define function to screen metaboard to invalidate 'type' from signature (e.g, invalidate dangers between two blocked self) horizontally
            def screenHorizontal(metaboard, signature, type, winCond, pos):

                dimensionX = len(metaboard[0])
                if type == 'danger': type = 0
                else: type = 1

                #Format all selfSignature's coords found in each row
                #sus = [susRow1, susRow3, ...]
                #susRow1 = [[col1, row], [col3, row], ...]
                sus = []
                for row in metaboard:
                    susEachRow = []
                    for col in row:
                        if (col == signature): susEachRow.append([row.index(col), metaboard.index(row)])
                    sus.append(susEachRow)
                
                sus = [susEachRow for susEachRow in sus if len(susEachRow) != 0]

                #Filter out all invalid segments between two blocked self horizontally
                for susEachRow in sus:
                    for i in range(len(susEachRow) - 1):
                        if (2 <= susEachRow[i + 1][0] - susEachRow[i][0] <= winCond):
                            for k in range(0, susEachRow[i + 1][0] - susEachRow[i][0]):
                                if (isinstance(metaboard[susEachRow[i][1]][susEachRow[i][0] + k], list)):
                                    #print(f'Due to being blocked on both ends by {signature} at coordinates {susEachRow[i][0]}:{susEachRow[i][1]} and {susEachRow[i + 1][0]}:{susEachRow[i + 1][1]}, the position with the coordinates {susEachRow[i][1]}:{susEachRow[i][0] + k} has been nullified of its {type}\'s {pos}.')
                                    metaboard[susEachRow[i][1]][susEachRow[i][0] + k][type][pos] = 0

                #Filter out all invalid segments between self and border
                for susEachRow in sus:
                    start = susEachRow[0]
                    end = susEachRow[-1]
                    if (1 <= start[0] < winCond):
                        for k in range(0, start[0]):
                            if (isinstance(metaboard[start[1]][k], list)):
                                #print(f'Due to being blocked on both ends by {signature} at coordinates {start[0]}:{start[1]} and the border, the position with the coordinates {start[1]}:{k} has been nullified of its {type}\'s {pos}.')
                                metaboard[start[1]][k][type][pos] = 0
                    if (1 <= dimensionX - end[0] - 1 < winCond):
                        for k in range(0, dimensionX - end[0] - 1):
                            if (isinstance(metaboard[end[1]][end[0] + k], list)):
                                #print(f'Due to being blocked on both ends by {signature} at coordinates {end[0]}:{end[1]} and the border, the position with the coordinates {end[1]}:{end[0] + k} has been nullified of its {type}\'s {pos}.')
                                metaboard[end[1]][end[0] + k][type][pos] = 0

                return metaboard

            #Define function to screen metaboard to invalidate 'type' from signature (e.g, invalidate dangers between two blocked self) diagonally
            def screenDiagonal(metaboard, signature, type, winCond, pos):
                dimensionY = len(metaboard)
                dimensionX = len(metaboard[0])
                if type == 'danger': type = 0
                else: type = 1

                #Format all selfSignature's coords found in each diagonal
                #susDiagDown, Up, sus = [susDiag1, susDiag3, ...]
                #susDiag1 = [[col1, row1], [col3, row3], ...]
                sus = []
                susDiagDown = []
                lenSusDiagDown = []
                susDiagUp = []
                lenSusDiagUp = []
                susDuplicate = []
                for i in range(dimensionY):
                    susEachDiagDown = []
                    originalDiagLen = 0
                    for j in range(dimensionY):
                        try:
                            if (metaboard[i + j][j] == signature): susEachDiagDown.append([i + j, j])
                            originalDiagLen += 1
                        except IndexError:
                            pass
                    susDiagDown.append(susEachDiagDown)
                    if (len(susEachDiagDown) != 0):
                        lenSusDiagDown.append(originalDiagLen)
                    else: lenSusDiagDown.append(0)
                for i in range(dimensionX):
                    susEachDiagUp = []
                    originalDiagLen = 0
                    for j in range(dimensionX):
                        try:
                            if (metaboard[j][i + j] == signature): susEachDiagUp.append([j, i + j])
                            originalDiagLen += 1
                        except IndexError: pass
                    susDiagUp.append(susEachDiagUp)
                    if (len(susEachDiagUp) != 0):
                        lenSusDiagUp.append(originalDiagLen)
                    else: lenSusDiagUp.append(0)
                sus.extend(susDiagDown)
                sus.extend(susDiagUp)
                for i in range(min(dimensionX, dimensionY)):
                    if (metaboard[i][i] == signature): susDuplicate.append([i, i])
                sus.remove(susDuplicate)

                susDiagUp = [susEachDiag for susEachDiag in susDiagUp if len(susEachDiag) != 0]
                lenSusDiagUp = [eachLen for eachLen in lenSusDiagUp if eachLen != 0]
                susDiagDown = [susEachDiag for susEachDiag in susDiagDown if len(susEachDiag) != 0]
                lenSusDiagDown = [eachLen for eachLen in lenSusDiagDown if eachLen != 0]

                #Filter out all invalid segments between two blocked self diagontally
                for susEachDiag in sus:
                    for i in range(len(susEachDiag) - 1):
                        if (2 <= susEachDiag[i + 1][0] - susEachDiag[i][0] <= winCond):
                            for k in range(0, susEachDiag[i + 1][0] - susEachDiag[i][0]):
                                if (isinstance(metaboard[susEachDiag[i][0] + k][susEachDiag[i][1] + k], list)):
                                    #print(f'Due to being blocked on both ends by {signature} at coordinates {susEachDiag[i][0]}:{susEachDiag[i][1]} and {susEachDiag[i + 1][0]}:{susEachDiag[i + 1][1]}, the position with the coordinates {susEachDiag[i][0] + k}:{susEachDiag[i][1] + k} has been nullified of its {type}\'s {pos}.')
                                    metaboard[susEachDiag[i][0] + k][susEachDiag[i][1] + k][type][pos] = 0

                #Filter out all invalid segments between self and border for susDiagUp
                for susEachDiag in susDiagUp:
                    start = susEachDiag[0]
                    end = susEachDiag[-1]
                    if (1 <= min(start[0], start[1]) < winCond):
                        for k in range(0, min(start[0], start[1]) + 1):
                            if (isinstance(metaboard[start[0] - k][start[1] - k], list)):
                                #print(f'Due to being blocked on both ends by {signature} at coordinates {start[0]}:{start[1]} and the corner, the position with the coordinates {start[0] + k}:{start[1] + k} has been nullified of its {type}\'s {pos}.')
                                metaboard[start[0] - k][start[1] - k][type][pos] = 0
                    if (1 <= lenSusDiagUp[susDiagUp.index(susEachDiag)] - min(end[0], end[1]) <= winCond):
                        for k in range(0, lenSusDiagUp[susDiagUp.index(susEachDiag)] - min(end[0], end[1])):
                            if (isinstance(metaboard[end[0] + k][end[1] + k], list)):
                                #print(f'Due to being blocked on both ends by {signature} at coordinates {end[0]}:{end[1]} and the corner, the position with the coordinates {end[0] + k}:{end[1] + k} has been nullified of its {type}\'s {pos}.')
                                metaboard[end[0] + k][end[1] + k][type][pos] = 0
                
                #Filter out all invalid segments between self and border for susDiagDown
                for susEachDiag in susDiagDown:
                    start = susEachDiag[0]
                    end = susEachDiag[-1]
                    if (1 <= min(start[0], start[1]) < winCond):
                        for k in range(0, min(start[0], start[1]) + 1):
                            if (isinstance(metaboard[start[0] - k][start[1] - k], list)):
                                #print(f'Due to being blocked on both ends by {signature} at coordinates {start[0]}:{start[1]} and the corner, the position with the coordinates {start[0] + k}:{start[1] + k} has been nullified of its {type}\'s {pos}.')
                                metaboard[start[0] - k][start[1] - k][type][pos] = 0
                    if (1 <= lenSusDiagDown[susDiagDown.index(susEachDiag)] - min(end[0], end[1]) <= winCond):
                        for k in range(0, lenSusDiagDown[susDiagDown.index(susEachDiag)] - min(end[0], end[1])):
                            if (isinstance(metaboard[end[0] + k][end[1] + k], list)):
                                #print(f'Due to being blocked on both ends by {signature} at coordinates {end[0]}:{end[1]} and the corner, the position with the coordinates {end[0] + k}:{end[1] + k} has been nullified of its {type}\'s {pos}.')
                                metaboard[end[0] + k][end[1] + k][type][pos] = 0

                return metaboard
            
            #pos: index of relevant value (0: horizontal, 1: vertical, 2: NW - SE, 3: NE - SW)
            #Screen top left corner
            screenTopLeftCorner(metaboard, winCond, 3, 'top left')
            metaboard = rotate(metaboard)
            #Screen top right corner
            screenTopLeftCorner(metaboard, winCond, 2, 'top right')
            metaboard = rotate(metaboard)
            #Screen bottom right corner
            screenTopLeftCorner(metaboard, winCond, 3, 'bottom right')
            metaboard = rotate(metaboard)
            #Screen bottom left corner
            screenTopLeftCorner(metaboard, winCond, 2, 'bottom left')
            metaboard = rotate(metaboard)
            #Screen horizontally
            screenHorizontal(metaboard, selfSignature, 'danger' , winCond, 0)
            screenHorizontal(metaboard, opponentSignature, 'opportunity' , winCond, 0)
            metaboard = rotate(metaboard)
            #Screen vertically
            screenHorizontal(metaboard, selfSignature, 'danger' , winCond, 1)
            screenHorizontal(metaboard, opponentSignature, 'opportunity' , winCond, 1)
            for i in range(3): metaboard = rotate(metaboard)
            #Screen NW-SE diagonally
            screenDiagonal(metaboard, selfSignature, 'danger' , winCond, 2)
            screenDiagonal(metaboard, opponentSignature, 'opportunity' , winCond, 2)
            metaboard = rotate(metaboard)
            #Screen NE-SW diagonally
            screenDiagonal(metaboard, selfSignature, 'danger' , winCond, 3)
            screenDiagonal(metaboard, opponentSignature, 'opportunity' , winCond, 3)
            for i in range(3): metaboard = rotate(metaboard)

        metaboard = mapMetaBoard(len(board[0]), len(board))
        dangerCoords = locate([opponentSignature], board)
        opportunityCoords = locate([selfSignature], board)
        for coord in dangerCoords:
            metaboard[coord[1]][coord[0]] = opponentSignature
        for coord in opportunityCoords:
            metaboard[coord[1]][coord[0]] = selfSignature
        for coord in dangerCoords:
            sweep(metaboard, coord, 'danger', opponentSignature, selfSignature, winCond)
        for coord in opportunityCoords:
            sweep(metaboard, coord, 'opportunity', opponentSignature, selfSignature, winCond)

        #Screening applies for difficulty 2 and up
        if (difficulty >= 2):
            screen(metaboard, selfSignature, opponentSignature, winCond)

        return metaboard
    
    #Define function to choose between aggresive or defensive
    def stance(metaboard, difficulty):
        dangerList = []
        opportunityList = []
        for row in metaboard:
            for col in row:
                if (isinstance(col, list)):
                    dangerList.append(max(col[0]))
                    opportunityList.append(max(col[1]))
        pressingDanger = max(dangerList)
        pressingOpportunity = max(opportunityList)
        #print(f'Highest danger is {pressingDanger}, whilst highest opportunity is {pressingOpportunity}.')
        #'Tactical' playstyle applies only for difficulty 3
        if (difficulty >= 3):
            if (pressingOpportunity > pressingDanger):
                return 'aggressive', pressingOpportunity
            elif (pressingOpportunity == pressingDanger):
                return 'tactical', pressingOpportunity
            else:
                return 'defensive', pressingDanger
        else:
            if (pressingOpportunity >= pressingDanger):
                return 'aggressive', pressingOpportunity
            else:
                return 'defensive', pressingDanger

    #Define function to make a play
    def decide(style, value, metaboard, difficulty):
        if (value != 0):
            if (style == 'aggressive'):
                type = 1
            elif (style == 'defensive'):
                type = 0
            else:
                type = 2
            if (type in [0, 1]):
                for row in metaboard:
                    for col in row:
                        if (isinstance(col, list)):
                            if max(col[type]) == value:
                                #print(col[type].index(value))
                                return row.index(col), metaboard.index(row)
            if (style == 'tactical'):
                returnList = []
                maxTracker = []
                for row in range(len(metaboard)):
                    for col in range(len(metaboard[0])):
                        if (isinstance(metaboard[row][col], list)):
                            if (max(metaboard[row][col][0]) == value) or (max(metaboard[row][col][1]) == value):
                                #print(col[type].index(value))
                                returnList.append([col, row])
                                maxTracker.append(sum(metaboard[row][col][0]) + sum(metaboard[row][col][1]))
                return returnList[maxTracker.index(max(maxTracker))][0], returnList[maxTracker.index(max(maxTracker))][1]
        else:
            return randint(0, len(metaboard[0]) - 1), randint(0, len(metaboard) - 1)

    #dimension = len(board)
    metaboard = meta(board, opponentSignature, selfSignature, winCond, difficulty)
    style, value = stance(metaboard, difficulty)
    invalid = True
    while (invalid):
        x, y = decide(style, value, metaboard, difficulty)
        if (board[y][x] == ' '): invalid = False
    alphabet = ascii_uppercase
    print(f'Computer has decided to play at column {alphabet[x]} and row {alphabet[y]}.\n\n')
    #print(f'Assessing risk and opportunity, taking {style} move this turn at col {x}, row {y}.')
    # valid = False
    # while (not valid):
    #     x = randint(0, dimension - 1)
    #     y = randint(0, dimension - 1)
    #     if board[y][x] == ' ': valid = True
    board[y][x] = selfSignature
    viewBoard(board)

#Define winning
def win(board, winCond, signature, opponentSignature):

    #Define function to determine box containing played area
    def box(board):

        #Define function to find first occurence of 'X' or 'O', row-wise
        #Value is [signature, opponentSignature]
        def locate(value, board):
            dimensionY = len(board)
            dimensionX = len(board[0])
            for row in range(dimensionY):
                for col in range(dimensionX):
                    if (board[row][col] in value): return row

        #Define function to inverse board vertically
        def invertY(board):
            invertYBoard = []
            dimensionY = len(board)
            for row in range(dimensionY):
                invertYBoard.append(board[dimensionY - row - 1])
            return invertYBoard

        #Define function to rotate board 90 degree
        def rotate(board):
            rotateBoard = []
            dimensionY = len(board)
            dimensionX = len(board[0])
            for col in range(dimensionX):
                column = [board[row][col] for row in range(dimensionY)]
                rotateBoard.append(column)
            return rotateBoard

        dimensionY = len(board)
        dimensionX = len(board[0])

        boundaryN = locate([signature, opponentSignature], board)
        boundaryS = dimensionY - locate([signature, opponentSignature], invertY(board)) - 1
        boundaryW = locate([signature, opponentSignature], rotate(board))
        boundaryE = dimensionX - locate([signature, opponentSignature], invertY(rotate(board))) - 1

        box = []
        for row in range(boundaryN, boundaryS + 1):
            boxRow = [board[row][col] for col in range(boundaryW, boundaryE + 1)]
            box.append(boxRow)
        return box

    #Create as many winCond x winCond grids as needed to cover the entire played area
    def grid(box, winCond):

        dimensionY = len(box)
        dimensionX = len(box[0])
        gridY = dimensionY - winCond + 1
        if (gridY < 1): gridY = 1
        gridX = dimensionX - winCond + 1
        if (gridX < 1): gridX = 1

        #List of grids
        grids = []
        for offsetX in range(gridX):
            for offsetY in range(gridY):
                grid = []
                for row in range(offsetY, offsetY + winCond):
                    rowY = []
                    for col in range(offsetX, offsetX + winCond):
                        try:
                            rowY.append(box[row][col])
                        except IndexError: pass
                    grid.append(rowY)
                grids.append(grid)
        return grids

    for board in grid(box(board), winCond):

        #Within each grid:
        dimensionY = len(board)
        dimensionX = len(board[0])

        #Count 'O's in a row
        for row in range(dimensionY):
            if (board[row].count(signature) >= winCond):
                return True

        #Count 'O's in a column
        columns = []
        for col in range(dimensionX):
            try:
                columns.append([row[col] for row in board])
            except IndexError: pass
        for col in columns:
            if (col.count(signature) >= winCond):
                return True
        
        #Count 'O's in a diagonal line
        dimension = min(dimensionX, dimensionY)
        diagonalsNW = []
        diagonalsNE = []
        for i in range(dimension):
            diagonalNW = []
            diagonalNE = []
            for j in range(dimension):
                try:
                    diagonalNW.append(board[j][j])
                except IndexError: pass
                try:
                    diagonalNE.append(board[j][dimension - j - 1])
                except IndexError: pass
            diagonalsNW.append(diagonalNW)
            diagonalsNE.append(diagonalNE)
        for diagonalNW in diagonalsNW:
            if (diagonalNW.count(signature) >= winCond):
                return True
        for diagonalNE in diagonalsNE:
            if (diagonalNE.count(signature) >= winCond):
                return True

#Game loop
print('Welcome to a game of Gomoku!\nThe rule is simple: block your opponent before they can get a long enough streak in a continuous row, column or diagonal to win.\n')
mode = True
while (mode):
    gamemode = input('Before we start, there are two gamemodes: custom and preset. Which one would you prefer?\n(c) for custom, (p) for preset. ')
    if (gamemode not in ['c', 'p']):
        print('Unrecognized input command. Please read the instructions carefully and try again.\n')
    else:
        mode = False
print('\n\n')

#Configuration settings for custom gamemode
configure = True
while (configure):

    #Set custom dimension
    invalid = True
    while (invalid and gamemode == 'c'):
        dimensionX, dimensionY = input('Input dimension for game initialization:\n(width x length): ').split('x')        
        try:
            dimensionX = int(dimensionX)
            dimensionY = int(dimensionY)
            invalid = False
        except TypeError:
            print('Invalid input detected. Please try again.\n')
    #Preset dimension
    if (gamemode == 'p'):
        print('Default grid set to 26x26.')
        dimensionX = 26
        dimensionY = 26

    #Set win condition
    valid = False
    while (not valid and gamemode == 'c'):
        winCond = input('Input streak size to count as win: ')
        try:
            winCond = int(winCond)
            if (not isinstance(winCond, int) or 3 > winCond > min(dimensionX, dimensionY)): raise TypeError
            valid = True
        except TypeError:
            print('Invalid input detected. Please try again.\n')
    #Preset win condition
    if (gamemode == 'p'):
        print('Default win streak set to 5.')
        winCond = 5

    #Set difficulty
    chose = False
    while (not chose and gamemode == 'c'):
        try:
            difficulty = int(input('Choose difficulty (easiest: 1 - hardest: 3): '))
            if (3 < difficulty or difficulty < 1): raise TypeError
            chose = True
        except TypeError:
            print('Invalid input detected. Please try again.\n')
    #Preset difficulty
    if (gamemode == 'p'):
        print('Default difficulty set to 3.')
        difficulty = 3

    #Set player's marker    
    proper = False
    while (not proper and gamemode == 'c'):
        marker = input('Choose your prefered marker:\n(o) for \'O\', (x) for \'X\': ')
        if (marker not in ['x', 'o']):
            print('Invalid input detected. Please try again.\n')
        else:
            proper = True
            if (marker == 'o'):
                opponentSignature = 'O'
                selfSignature = 'X'
            else:
                opponentSignature = 'X'
                selfSignature = 'O'
    #Preset marker
    if (gamemode == 'p'):
        print('Default player marker set to \'X\'.')
        opponentSignature = 'X'
        selfSignature = 'O'

    #Choose who goes first
    ok = False
    while (not ok and gamemode == 'c'):
        playerGoesFirst = input('Do you want to go first?\n(y) for yes, (n) for no: ')
        if (playerGoesFirst not in ['y', 'n']):
            print('Invalid input detected. Please try again.\n')
        else:
            ok = True
            playerGoesFirst = (playerGoesFirst == 'y')
    #Preset first play
    if (gamemode == 'p'):
        print('Default: computer goes first.')
        playerGoesFirst = False

    #Replay loop
    replay = True
    while (replay):
        print('\n\n')
        board = mapBoard(int(dimensionX), int(dimensionY), ' ')
        viewBoard(board)
        while (True):
            try:
                locate([' '], board)[0]
            except IndexError:
                print('\nIt\'s a tie!')
                break

            #Player plays
            if (playerGoesFirst):
                mark(board, opponentSignature)
                if (win(board, winCond, opponentSignature, selfSignature)):
                    print('Congratulations, you won!')
                    break
            playerGoesFirst = True
            try:
                locate([' '], board)[0]
            except IndexError:
                print('\nIt\'s a tie!')
                break
            print('\n\nComputer is calculating...')

            #Computer plays
            play(board, selfSignature, opponentSignature, difficulty)
            if (win(board, winCond, selfSignature, opponentSignature)):
                print('Sorry, you lost!')
                break
        
        #Replay choice
        choice = input('\n\nDo you want to replay?\n(y) to replay with current configurations, (n) to quit, (p) to play with recommended configurations, or (c) to replay with different configurations.\n')
        if (choice == 'y'):
            replay = True
            configure = False
            print('\n\n')
        elif (choice == 'n'):
            replay = False
            configure = False
        elif (choice == 'p'):
            replay = False
            configure = True
            gamemode = 'p'
            print('\n\n')
        elif (choice == 'c'):
            replay = False
            configure = True
            gamemode = 'c'
            print('\n\n')

input('\nPress any key to quit.')
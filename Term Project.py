#################################################
# Term project!

# Your name: Yu-An(Aaron) Chen
# Your andrew id: yuanche2

#################################################
import math, copy, random
from cmu_112_graphics import *
import random

class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.gameMode = GameMode()
        app.setActiveMode(app.splashScreenMode)
        app.timerDelay = 50

class SplashScreenMode(Mode):
    def appStarted(app):
        app.play = False
        app.howToPlay = False
        app.analytics = False

    def mousePressed(app, event):
        if app.howToPlay == False and app.analytics == False:
            cx, cy = app.width/2, app.height/2
            if ((cx-120 <= event.x <= cx+120) and
                (280 <= event.y <= 360)):
                app.howToPlay = True
            elif ((cx - 120 <= event.x <= cx + 120) and
                390 <= event.y <= 470):
                app.analytics = True
            elif ((cx - 120 <= event.x <= cx + 120) and
                170<= event.y <= 250):
                app.play = True
                app.app.setActiveMode(app.app.gameMode)
        else:
            if ((20 <= event.x <= 100) and
                20<= event.y <= 60):
                app.howToPlay = False
                app.analytics = False

    def drawSplash(app, canvas):
        canvas.create_rectangle(0,0, app.width, app.height, fill = 'light grey')
        canvas.create_text(app.width/2, 80, text = "Gravity Guy 2.0", font = 'Arial 36 bold')
        #button height = 80, width = 240
        #play
        canvas.create_rectangle(app.width/2 - 120, 170, app.width/2 + 120, 250, fill = 'grey')
        canvas.create_text(app.width/2, 210, text = 'Play', font = 'Arial 30 bold')
        #help
        canvas.create_rectangle(app.width/2 - 120, 280, app.width/2 + 120, 360, fill = 'grey')
        canvas.create_text(app.width/2, 320, text = 'How to Play', font = 'Arial 30 bold')
        #AI Guidance
        canvas.create_rectangle(app.width/2 - 120, 390, app.width/2 + 120, 470, fill = 'grey')
        canvas.create_text(app.width/2, 430, text = 'AI Guidance', font = 'Arial 30 bold')

        #return to game, how to play, quit. After finish chuck this code into game mode

    def drawTutorial(app, canvas):
        canvas.create_rectangle(0,0, app.width, app.height, fill = 'light grey')

        canvas.create_rectangle(20,20,100,60, fill = 'light grey', width = 2)
        canvas.create_text(60,40, text = 'back', font = "Arial 18 bold")

        canvas.create_text(app.width/2, 80, text = "Tutorial", font = 'Arial 36 bold')
        canvas.create_text(app.width/2 - 15, 350, 
                        text = """\
        1. In this enhanced version of "Gravity Guy", players can press the space bar to 
            change the direction of gravity for 10 energy points to work across the map.

        2. Collecting coins increases energy by 5. Energy decreases by 5 for every half 
           second out of the map and 50 for every enemy hit. Players can press "right" 
           to teleport back onto the screen.

        3. Without powerups, hitting a wall or enemy on the side knocks the player back.

        4. As players collect coins, powerups become available upon activation.

            Q (5 coins): Angel -- Turns all Wall Blocks and enemies on screen into coins

            W (10 coins): Zap -- Grants players a laser that automatically destroy a row
                                  if the row is going to knock the player back

            E (15 coins): Sniper -- Grants players a sniper bullet to kill an enemy
                                  and fully regenerate energy

            R (20 coins): Disable -- Stops time and allows players to build their own map.
                                    Drag = add walls, click = add coin
        """, font = "Arial 18 bold")

    def drawAnalytics(app, canvas):
        canvas.create_rectangle(0,0, app.width, app.height, fill = 'light grey')

        canvas.create_rectangle(20,20,100,60, fill = 'light grey', width = 2)
        canvas.create_text(60,40, text = 'back', font = "Arial 18 bold")

        canvas.create_text(app.width/2, 80, text = "AI Guidance", font = 'Arial 36 bold')
        canvas.create_text(app.width/2 - 15, 360, 
                        text = """\
        This toggle-based AI Mode provides the best possible path

        that the player can take given the current gravity orientiation.

        This guiding system prioritizes paths that would grant the most 

        coins, and avoids hitting both enemies and walls on the side. 


        Note: it's not meant to be a perfect AI, so treat it more like 
                  a guide. 


        Press 'A' to activate/deactivate.  
        """, font = "Arial 24 bold")

    def redrawAll(app, canvas):
        app.drawSplash(canvas)
        if app.howToPlay:
            app.drawTutorial(canvas)
        if app.analytics:
            app.drawAnalytics(canvas)

class GameMode(Mode):
    def appStarted(app): 
        app.rows = 15
        app.cols = 20
        app.counter = 0 

        #powerups
        app.angel = False
        app.birdPower = 0
        app.zapped = []
        app.disable = False
        app.sniper = False
        app.crossHairX = None
        app.crossHairY = None
        app.bestPath = [7,2,7,3]
        app.bestPathCorrected = [0,0,1,1]
        app.timer = 0

        #golden path 
        app.endGoldRow = 6
        app.goldCounter = 0

        #display information
        app.energy = 100
        app.score = 0
        app.coinsCollected = 0
        app.accuracyCoins = 0
        app.coinsMissed = 0
        app.pause = False
        app.gameOver = False
        app.ai = False

        #screenboard
        app.screenBoard = [[False]* app.cols for i in range(app.rows)]

        app.getPictures()
        #create a wall board that's next to / after player board 
        app.startWallBoard()
        app.startScreenWalls()

        #person information
        app.r = 10 
        app.x = 100
        app.returnCounter = 0
        app.gravity = True 
        app.gForce = 37/2
        app.change = 0
        app.timerDelay = 45
        app.startCheckForReturn = False
        app.createImage()
        app.createEnemy()
    
    # Note: I did not draw any of the pictures, their links are commented above the url assignment
    def getPictures(app):
        #Taken from: https://pngimg.com/uploads/square/square_PNG24.png
        url = "wallBlock.png"
        app.brick = app.loadImage(url)
        app.brick = app.scaleImage(app.brick, 1/28)

        #coins, taken from: https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Lol_circle.png/479px-Lol_circle.png
        url = "coin.png"
        app.coin = app.loadImage(url)
        app.coin = app.scaleImage(app.coin, 1/15)

        #runner, taken from: https://i.stack.imgur.com/dUH5P.png
        url = 'runner.png'
        app.image = app.loadImage(url)
        app.image = app.scaleImage(app.image, 1/3)
        app.image = app.image.transpose(Image.FLIP_TOP_BOTTOM)

        #enemy, taken from: https://www.feplanet.net/media/sprites/7/battle/sheets/enemy/enemy_knight_lance.gif
        url = 'enemy.gif'
        app.enemy = app.loadImage(url)
        app.enemy = app.scaleImage(app.enemy, 1.2)
        app.enemy = app.enemy.transpose(Image.FLIP_LEFT_RIGHT)

        #sniper, taken from: https://cdn.hipwallpaper.com/i/22/33/asHdQ2.png
        url = 'crosshair.png'
        app.crosshair = app.loadImage(url)
        app.crosshair = app.scaleImage(app.crosshair, 1/15)

        #wrench, taken from: https://lh3.googleusercontent.com/proxy/LB81Cay2-SE5k4-sNaHYaP5wTpiSMGHz1H5jCvBgOLFivKNRWqr-_iTCx1D4eVoj47MJgdACLKXM5j7pggqsfTli2LcPkbnk0t8XT9PNViQQG0Y31AobT6QeWsQQ29DzhCl4BAY
        url = 'wrench.png'
        app.wrench = app.loadImage(url)
        app.wrench = app.scaleImage(app.wrench, 1/18)
    # Note: I did not draw the spritestrip. I found it on the website below.
    # https://itqna.net/questions/11540/how-animate-sprite-sheets
    def createImage(app):
        app.image = app.image.transpose(Image.FLIP_TOP_BOTTOM)
        app.picWidth, app.picHeight = app.image.size 
        app.sprites = [ ]
        for i in range(5):
            sprite = app.image.crop(((i/5) * app.picWidth, app.picHeight/2, 
                                ((i+1)/5) * app.picWidth , app.picHeight-1))
            app.sprites.append(sprite)
        app.spriteCounter = 0
    
    def createEnemy(app):
        thisPicWidth, thisPicHeight = app.enemy.size 
        app.enemySprites = []
        for i in range(6):
            enemy = app.enemy.crop(((i/6) * thisPicWidth, thisPicHeight *0.17, 
                                ((i+1)/6) * thisPicWidth , thisPicHeight * 0.33))
            spriteWidth, spriteHeight = enemy.size
            enemy = enemy.crop((0,0,spriteWidth-7,spriteHeight))
            app.enemySprites.append(enemy)
        app.enemySpriteCounter = 0

    def startScreenWalls(app):
        app.screenBoard[5] = [True]* app.cols
        app.screenBoard[10] = [True] * app.cols

    def startWallBoard(app):
        app.goldCounter += 1
        app.wallBoard = [[False]* app.cols for i in range(app.rows)]
        if app.score % 400 < 130: 
            (app.wallRow1, app.length1) = (random.randint(2, app.rows-1), 
                                            random.randint(5,14))
            app.wallRow3, app.length3 = (random.randint(2, app.rows-1), 
                                        random.randint(3,7))
            while True: 
                (app.wallRow2, app.length2) = (random.randint(2, app.rows-1),
                                                random.randint(5,14))
                if app.legalWallDist: break  
            app.wallBoard[app.wallRow1] = ([False]*2 + [True]* app.length1 + 
                                            [False] * (app.cols - app.length1-2))
            app.wallBoard[app.wallRow2] = ([True] * app.length2 + 
                                            [False] * (app.cols - app.length2)) 
            app.wallBoard[app.wallRow3] = ([False] * (app.cols - app.length3)+ 
                                            [True] * app.length3 )
        else: 
            app.newRows = (random.randint(3,14), random.randint(3,14),
            random.randint(3,14))
            for row in range(len(app.wallBoard)):
                if row in app.newRows:
                    numOfBlocks = random.randint(3,4)
                    while True:
                        b1, b2 = (random.randint(0,19), random.randint(0,19))
                        b3, b4 = random.randint(0,19), random.randint(0,19)
                        if (numOfBlocks == 4 and 
                            app.legalBlockDist(numOfBlocks, b1, b2, b3, b4)): 
                            app.wallBoard[row][b1] = True
                            app.wallBoard[row][b2] = False
                            app.wallBoard[row][b3] = True
                            app.wallBoard[row][b4] = True
                            app.wallBoard[7][9], app.wallBoard[4][3] = (True, True)
                            break
                        if (numOfBlocks == 3 and 
                            app.legalBlockDist(numOfBlocks, b1, b2, b3, b4)): 
                            app.wallBoard[row][b1] = True
                            app.wallBoard[row][b2] = True
                            app.wallBoard[row][b3] = True
                            app.wallBoard[7][9], app.wallBoard[4][3] = (True, True)
                            break

        if app.goldCounter % 2 ==0:
            app.addGoldRing() 
            #spawns enemy
            legalEnemySpots = []
            for row in range(app.rows-1):
                for col in range(app.cols):
                    if app.wallBoard[row+1][col] == True and app.wallBoard[row][col] == False:
                        legalEnemySpots.append((row,col))
            enemyLocation = random.randint(0,len(legalEnemySpots)-1)
            enemyRow, enemyCol = legalEnemySpots[enemyLocation]
            app.wallBoard[enemyRow][enemyCol] = 'enemy'
        else: 
            coinsPlaced = 0
            while coinsPlaced < 5:
                row = random.randint(0, app.rows -1)
                col = random.randint(0, app.cols -1)
                if app.wallBoard[row][col] == False:
                    app.wallBoard[row][col] = 'Gold'
                    coinsPlaced +=1 
                    
    def addGoldRing(app):
        col = 0
        row = app.endGoldRow
        L = [1,-1,0]
        while col < 19:
            newDot = False
            for drow in L:
                testSpotRow = row + drow
                if testSpotRow == 15:
                    testSpotRow -=1
                    L = [-1,1,0]
                elif testSpotRow == 2: 
                    L = [1,-1,0]
                if (not app.wallBoard[testSpotRow][col + 1] and (not newDot)):
                    if col % 1 == 0 :
                        app.wallBoard[testSpotRow][col + 1] = "Gold"
                    newDot = True
                    if col == 14: 
                        app.endGoldRow = testSpotRow
                        return
                    col += 1
                    row = testSpotRow
            
    def legalWallDist(app):
        return abs(app.wallRow2 - app.wallRow1) >= 5

    def legalBlockDist(app, numOfBlocks, b1, b2, b3, b4):
        if numOfBlocks == 4:
            return (abs(b2-b1) > 2 and abs(b3-b2) > 2 and abs(b1 - b3) > 1 
                    and abs(b4 - b3) > 2 and  abs(b4-b2) > 2 and abs (b4-b1)>1)
        elif numOfBlocks == 3: 
            return (abs(b2-b1) > 2 and abs(b3-b2) > 1 
                    and abs(b1 - b3) > 1)

    def defineBoard(app):
        if len(app.wallBoard[app.rows-1]) == 0:
            app.startWallBoard()
        for row in range(app.rows):
            app.screenBoard[row].pop(0)
            if app.wallBoard[row][0] == 'Gold':
                app.screenBoard[row].append("Gold")
            elif app.wallBoard[row][0] == True: 
                app.screenBoard[row].append(True)
            elif app.wallBoard[row][0] == 'enemy': 
                app.screenBoard[row].append('enemy')
            else: app.screenBoard[row].append(False)
            app.wallBoard[row].pop(0)
        if app.ai: 
            app.findBestPath()

    def checkAngel(app):
        if app.angel: 
            for row in range(app.rows):
                for col in range(app.cols):
                    if app.screenBoard[row][col] != False: 
                        app.screenBoard[row][col] = 'Gold'
                    
                    if len(app.wallBoard[0]) > 0 and app.wallBoard[row][0] != False:
                        app.wallBoard[row][0] = "Gold"
            app.angel = False

    def checkMissedCoins(app):
        for row in range(app.rows):
            if app.screenBoard[row][1] == 'Gold':
                app.coinsMissed += 1

    def mousePressed(app, event):
        if app.pause:
            cx, cy = app.width/2, app.height/2
            if cx-120 <= event.x <= cx+120 and cy-120 <= event.y <= cy -50:
                app.pause = False
            elif cx-120 <= event.x <= cx+120 and cy-20 <= event.y <= cy + 50:
                app.appStarted()
            elif cx-120 <= event.x <= cx+120 and cy + 80 <= event.y <= cy + 150:
                app.appStarted()
                app.app.setActiveMode(app.app.splashScreenMode)
        elif app.disable:
            row, col = app.getCell(event.x, event.y)
            app.screenBoard[row][col] = 'Gold'
            app.savedBoard = app.screenBoard

        elif app.sniper:
            for row in range(app.rows):
                for col in range(app.cols):
                    if app.screenBoard[row][col] == 'enemy':
                        enemyRow, enemyCol = row, col
            try:
                x0,y0,x1,y1 = app.getCellBounds(enemyRow, enemyCol)
                if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                    app.screenBoard[enemyRow][enemyCol] = False
                    app.sniper = False
                    app.energy = 100
            except: pass
            app.sniper = False

    def mouseMoved(app, event):
        if app.sniper:
            app.crossHairX, app.crossHairY = event.x, event.y
        else: app.crossHairX, app.crossHairY = None, None

    def mouseDragged(app, event):
        if app.disable:
            row, col = app.getCell(event.x, event.y)
            app.screenBoard[row][col] = True
            app.savedBoard = app.screenBoard

    def keyPressed(app, event):
        if event.key == "Space" and app.energy > 12 and not app.pause:
            app.gravity = not app.gravity
            app.createImage()
            if app.energy > 0: 
                app.energy -= 10 
        elif event.key =="Right":
            if app.x <= 100: 
                app.x = 100
                app.energy -=5
        elif (event.key == 'q' and app.coinsCollected >= 5) or event.key == '1':
            app.angel = True
            if not event.key == '1':
                app.coinsCollected -= 5
        elif (event.key == 'w' and app.coinsCollected >= 10) or event.key == '2':
            app.birdPower += 1
            if not event.key == '2':
                app.coinsCollected -= 10
        elif (event.key == 'e' and app.coinsCollected >= 15) or event.key == '3': 
            app.sniper = True
            if not event.key == '3':
                app.coinsCollected -= 15
        elif (event.key == 'r' and app.coinsCollected >= 20) or event.key =='4':
            app.disable = True 
            if not event.key == '4':
                app.coinsCollected -= 20
        elif event.key == 'h':
            app.pause = not app.pause
        elif event.key == 'a':
            app.ai = not app.ai

    def timerFired(app):
        if app.energy <= 0:
            app.gameOver = True
            app.pause = True
        if not app.disable and not app.pause:
            app.counter +=1
            app.score +=1 
            app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
            app.enemySpriteCounter = (1 + app.enemySpriteCounter) % len(app.enemySprites)

            if app.gravity: 
                app.change += app.gForce
                if app.hitBlock():
                    app.change -= (app.gForce)
                    CurrY = app.height/2 + app.change 
                    CurrRow, CurrCol = app.getCell(app.x, CurrY)
                    x0,y0,x1,y1 = app.getCellBounds(CurrRow + 1, CurrCol)
                    Difference = (y0+y1)/2 - CurrY 
                    Adjustment = 50 - Difference
                    app.change -= Adjustment    
            else: 
                app.change -= app.gForce
                if app.hitBlock(): 
                    app.change += app.gForce
                    CurrY = app.height/2 + app.change 
                    CurrRow, CurrCol = app.getCell(app.x, CurrY)
                    x0,y0,x1,y1 = app.getCellBounds(CurrRow - 1, CurrCol)
                    Difference = -((y0+y1)/2 - CurrY)
                    Adjustment = 50 - Difference
                    app.change += Adjustment    


            if app.hitBlockSide():
                if app.birdPower > 0: 
                    app.birdPower -= 1
                    row =int((app.height/2 + app.change)/app.height * len(app.screenBoard))
                    app.zapped = []
                    for i in range(3):
                        if (row - 1 + i < len(app.screenBoard) and (app.screenBoard[row-1+i][3] == True
                            or app.screenBoard[row-1+i][2] == True or app.screenBoard[row-1+i][3] == 'enemy'
                            or app.screenBoard[row-1+i][2] == 'enemy')):
                            app.screenBoard[row-1 + i] = [[False]]*len(app.screenBoard[0])
                            app.zapped.append((row-1+i, 0))
                    app.startZap = True
                else:
                    row, col = app.getCell(app.x, app.height/2 + app.change)
                    app.screenBoard[row][col] = False
                    app.x -= (app.width/app.rows +10)

            app.checkAngel()
            app.checkMissedCoins()

            if app.counter % 2 == 0:
                app.defineBoard()

            for i in range(len(app.zapped)):
                row, timer = app.zapped[i]
                timer +=1
                app.zapped[i] = (row, timer)
            
            if ((not 40 <= app.height/2 + app.change <= app.height or app.x < 0)
                and app.counter %2 == 0):
                app.energy -= 5
        else:
            app.timer +=1
            if app.timer % 110 == 0:
                app.disable = False 
                app.timer = 0 

    def hitBlockSide(app):
        for row in range(app.rows):
            for col in range(app.cols):
                if app.screenBoard[row][col] == True or app.screenBoard[row][col] == 'enemy':
                    x0,y0,x1,y1 = app.getCellBounds(row, col)
                    (cx, cy) = (app.x, app.height/2 + app.change)
                    if (x0 < (cx + app.r) < x1 and (y0 < cy < y1 or 
                        y0 < cy+1.7*app.r < y1 or y0 < cy-1.7*app.r < y1)):
                        if app.birdPower <= 0 and app.screenBoard[row][col] == 'enemy':
                            app.energy -= 50
                        return True
                elif app.screenBoard[row][col] == 'Gold':
                    x0,y0,x1,y1 = app.getCellBounds(row, col)
                    (cx, cy) = (app.x, app.height/2 + app.change)
                    if (x0 < (cx + app.r) < x1 and (y0 < cy < y1 or 
                        y0 < cy+1.5*app.r < y1 or y0 < cy-1.5*app.r < y1)):
                        app.screenBoard[row][col] = False
                        app.coinsCollected += 1
                        app.accuracyCoins += 1
                        if app.energy <= 97: 
                            app.energy += 5
                    
    def hitBlock(app):
        for row in range(app.rows):
            for col in range(app.cols):
                if app.screenBoard[row][col]== True:
                    x0,y0,x1,y1 = app.getCellBounds(row, col)
                    (cx, cy) = (app.x, app.height/2 + app.change)
                    if (app.distance(cx, (x0+x1)/2, cy, (y0+y1)/2) 
                    <= 1.3*(app.r + (app.height/app.rows)/2)):
                        return True
                elif app.screenBoard[row][col]== 'Gold':
                    x0,y0,x1,y1 = app.getCellBounds(row, col)
                    (cx, cy) = (app.x , app.height/2 + app.change)
                    if (app.distance(cx, (x0+x1)/2, cy, (y0+y1)/2) 
                    <= 1.5*(app.r + (app.height/app.rows)/2)):
                        app.screenBoard[row][col] = False
                        app.coinsCollected +=1
                        app.accuracyCoins +=1
                        if app.energy <= 98:
                            app.energy += 5
        return False

    def checkForReturn(app):
        for row in range(app.rows):
            for col in range(app.cols):
                if app.screenBoard[row][col]:
                    x0,y0,x1,y1 = app.getCellBounds(row, col)
                    (cx, cy) = (app.x, app.height/2 + app.change)
                    if not (x0 < (cx + app.r) < x1 and y0 < cy < y1):
                        app.x += 1
                    if app.x > 100: 
                        app.x = 100
                        break

    def distance(app, x0,x1,y0,y1):
        return math.sqrt((x0-x1)**2 + (y0-y1)**2)

    def drawBoard(app, canvas):
        for row in range(app.rows):
            for col in range(app.cols):
                if app.screenBoard[row][col] and app.screenBoard[row][col] == True:
                    x0,y0,x1,y1 = app.getCellBounds( row, col) 
                    #canvas.create_rectangle(x0,y0,x1,y1, fill = '#6bebff')
                    canvas.create_image((x0 + x1)/2, (y0+y1)/2, image=ImageTk.PhotoImage(app.brick))
                elif app.screenBoard[row][col] == "Gold":
                    x0,y0,x1,y1 = app.getCellBounds(row, col) 
                    canvas.create_image((x0 + x1)/2, (y0+y1)/2, image=ImageTk.PhotoImage(app.coin))
                elif app.screenBoard[row][col] == 'enemy':
                    sprite = app.enemySprites[app.enemySpriteCounter]
                    x0,y0,x1,y1 = app.getCellBounds(row, col) 
                    canvas.create_image((x0 + x1)/2, (y0+y1)/2, image=ImageTk.PhotoImage(sprite))

    # adapted from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCellBounds(app, row, col):
        gridWidth  = app.width 
        gridHeight = app.height 
        cellHeight = cellWidth = gridHeight / app.rows
        x0 =  col * cellWidth
        x1 = (col+1) * cellWidth
        y0 = row * cellHeight
        y1 = (row+1) * cellHeight
        return (x0, y0, x1, y1)

    # adapted from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    def getCell(app, x, y):
        gridWidth  = app.width 
        gridHeight = app.height 
        cellWidth  = gridWidth / app.cols
        cellHeight = gridHeight / app.rows
        row = int(y / cellHeight)
        col = int(x / cellWidth)
        return (row, col)

    def drawGuy(app, canvas):
        #location: (100, app.height/2)
        r = app.r
        x0,y0,x1,y1 = (app.x-r, (app.height/2 - r) + app.change, app.x + r, 
        app.height/2 + r + app.change)
        sprite = app.sprites[app.spriteCounter]
        canvas.create_image((x0 + x1)/2, (y0+y1)/2 +5, image=ImageTk.PhotoImage(sprite))

    def drawEnemy(app, canvas):
        r = app.r
        x0,y0,x1,y1 = (app.x-r, (app.height/2 - r) + app.change, app.x + r, 
        app.height/2 + r + app.change)
        sprite = app.enemySprites[app.enemySpriteCounter]
        canvas.create_image((x0 + x1)/2, (y0+y1)/2 +5, image=ImageTk.PhotoImage(sprite))
    
    def drawCrossHair(app, canvas):
        if app.sniper and app.crossHairX != None and app.crossHairY != None: 
            canvas.create_image(app.crossHairX, app.crossHairY, image=ImageTk.PhotoImage(app.crosshair))

    def drawTop(app, canvas):
        #white
        canvas.create_rectangle(0,0,app.width, 45, fill = 'white', width = 0)

        #Energy
        canvas.create_text(40,20, text = f'Energy: ', font = "Arial 18 bold")
        canvas.create_rectangle(85, 10, 240, 30, fill = 'white', width = 3)
        if app.energy > 0: 
            canvas.create_rectangle(86, 11, 153 * (app.energy/100) + 86, 29, 
                                    fill = 'green', width = 0)
        #score
        canvas.create_text(app.width - 60, 20, text = f'Score: {app.score}', 
                        font = "Arial 18 bold")
        
        #abilities
        canvas.create_rectangle(355,7,385,37, fill = 'white', width = 2)
        canvas.create_rectangle(395,7,425,37, fill = 'white', width = 2)
        canvas.create_rectangle(435,7,465,37, fill = 'white', width = 2)
        canvas.create_rectangle(475,7,505,37, fill = 'white', width = 2)
        if app.coinsCollected >= 5: 
            picCoin = app.scaleImage(app.coin, 0.8)
            canvas.create_image(370, 22, image=ImageTk.PhotoImage(picCoin))
        if app.coinsCollected >= 10:
            canvas.create_rectangle(396, 18, 424, 26, fill = 'red', width = 0)
        if app.coinsCollected >= 15:
            picCrosshair = app.scaleImage(app.crosshair, 0.55)
            canvas.create_image(450, 22, image=ImageTk.PhotoImage(picCrosshair))
        if app.coinsCollected >= 20:
            canvas.create_image(490, 22, image = ImageTk.PhotoImage(app.wrench))
        if app.timer != 0 and not app.pause and not app.gameOver:
            canvas.create_text(720, 70, text = f'Time left: {int(8 - 8*(app.timer/110)+ 1)}', font = 'Arial 24 bold')
        canvas.create_text(435, 30, text = ' Q         W         E          R', font = "Arial 12 bold")
        if app.ai:
            canvas.create_text(80,60, text = 'AI Mode Activated', font = 'Arial 16 bold')


        #collected coins
        canvas.create_text(600, 20, text = f'Coins: {app.coinsCollected}', 
                            font = "Arial 18 bold")

    def drawZap(app, canvas):
        if len(app.zapped) > 0:
            for row, timer in app.zapped:
                if timer < 4:
                    x0,y0,x1,y1 = app.getCellBounds(row, 15)
                    canvas.create_rectangle(app.x,y0+15,app.width,y1-15, fill = 'red')

    def drawPause(app, canvas):
        if app.pause:
            canvas.create_rectangle(app.width/2- 150, app.height/2 - 200, app.width/2 + 150, app.height/2 + 200,
                                    fill = 'white', width = 2)
            canvas.create_rectangle(app.width/2 - 120, app.height/2 -20, app.width/2 + 120, app.height/2 +50,
                                    fill = 'light grey', width = 1)
            canvas.create_text(app.width/2, app.height/2 +15, text = 'Restart', font = 'Arial 24 bold')

            canvas.create_rectangle(app.width/2 - 120, app.height/2 +80, app.width/2 + 120, app.height/2 +150,
                                    fill = 'light grey', width = 1)
            canvas.create_text(app.width/2, app.height/2 +115 , text = 'Quit ', font = 'Arial 24 bold')
            if app.gameOver == False: 
                canvas.create_text(app.width/2, app.height/2 - 160, text = 'Paused', font = 'Arial 30 bold')
                canvas.create_rectangle(app.width/2 - 120, app.height/2 -120, app.width/2 + 120, app.height/2 -50,
                                        fill = 'light grey', width = 1)
                canvas.create_text(app.width/2, app.height/2 - 85, text = 'Return to Game', font = 'Arial 24 bold')
            else:
                if app.coinsMissed == 0:
                    app.coinsMissed = 1
                canvas.create_text(app.width/2, app.height/2 - 150, text = 'Game Over!', font = 'Arial 30 bold')
                canvas.create_text(app.width/2, app.height/2 - 85, text = f'Score: {app.score}, Accuracy: {int((app.accuracyCoins / (app.accuracyCoins + app.coinsMissed)) * 100)}%', font = 'Arial 20 bold')

    def findBestPath(app):
        currRow, currCol = app.getCell(app.x, app.height/2 + app.change)
        if app.gravity:
            app.bestPath = app.helper(currRow, currCol, [], [1, 0, -1])
        else: 
            app.bestPath = app.helper(currRow, currCol, [], [-1, 0, 1])
        app.bestPathCorrected = []
        tempList = []
        if app.bestPath != None:
            for elem in app.bestPath:
                tempList += [elem]
                if len(tempList) == 2:
                    x0,y0,x1,y1 = app.getCellBounds(tempList[0],tempList[1])
                    app.bestPathCorrected += [(x0 + x1)/2, (y0 + y1)/2]
                    tempList = []

    def helper(app, startRow, startCol, L, priority):
        if startCol == app.cols -1:
            return L
        elif startRow == 1: 
            L+= [startRow, startCol]
            return app.helper(startRow + 1, startCol + 1, L, [1,-1, 0])
        elif startRow == app.rows -1: 
            L += [startRow, startCol]
            return app.helper(startRow -1 , startCol + 1, L, [-1,1,0])
        elif 0<=startRow <= app.rows -1 and app.screenBoard[startRow][startCol] == 'enemy':
            L += [startRow-1, startCol]
            return app.helper(startRow -1 , startCol + 1, L, [1,-1,0])
        if 0<=startRow <= app.rows -1 and app.screenBoard[startRow][startCol] == True and startRow-1 in L:
            L+= [startRow-1, startCol]
            return app.helper(startRow-1, startCol +1, L, priority)
        if startRow -1 >= 0 and startRow + 1 <= app.rows - 1 and (app.screenBoard[startRow-1][startCol] == True or app.screenBoard[startRow+1][startCol] == True):
            L += [startRow, startCol]
            return app.helper(startRow, startCol + 1, L, priority)

        for dRow in priority:
            if app.isGoldMove(startRow + dRow, startCol + 1):
                L += [startRow + dRow, startCol + 1]
                result = app.helper(startRow + dRow, startCol + 1, L, priority)
                if result != None:
                    return L 
                else: 
                    L.remove(startRow + dRow)
                    L.remove(startCol + 1)
            
        for dRow in priority:
            if app.isLegalMove(startRow + dRow, startCol + 1):
                L += [startRow + dRow, startCol + 1]
                result = app.helper(startRow + dRow, startCol + 1, L, priority)
                if result != None:
                    return L 
                else: 
                    L.remove(startRow + dRow)
                    L.remove(startCol + 1)
        return None

    def isLegalMove(app, thisRow, thisCol):
        return 1<= thisRow <= app.rows - 1 and 0 <= thisCol <= app.cols and app.screenBoard[thisRow][thisCol] == False

    def isGoldMove(app, thisRow, thisCol):
        return 1<= thisRow <= app.rows - 1 and 0 <= thisCol <= app.cols and app.screenBoard[thisRow][thisCol] == 'Gold'

    def redrawAll(app, canvas):
        canvas.create_rectangle(0,45, app.width, app.height, fill = 'light grey', width = 0)
        app.drawBoard(canvas)
        app.drawZap(canvas)
        app.drawGuy(canvas)
        if app.bestPath != None and app.ai:
            canvas.create_line(app.bestPathCorrected, fill = 'purple', width = 2)
        app.drawTop(canvas)
        app.drawCrossHair(canvas)
        app.drawPause(canvas)

app = MyModalApp(width= 800, height= 600)
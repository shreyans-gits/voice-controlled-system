import cv2
from HandTracker import HandDetector, GestureTracker, THUMB, INDEX, MIDDLE, RING, PINKY
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import time
from whiteboard import Whiteboard
from airmouse import AirMouse
from shapes3d import Shapes3D

# Screen and app state
SCREEN_W, SCREEN_H = 1280, 720
FONT_PATH = "GUI/open_sans.ttf"
notification = ""
notificationTimer = 0
# subPanelOpen = False
hoveredSubBtn = -1
whiteboard = Whiteboard(SCREEN_W, SCREEN_H)
airmouse = AirMouse(SCREEN_W, SCREEN_H)
shapes3d = Shapes3D(SCREEN_W, SCREEN_H)

# Mode management
modes = ["Whiteboard", "Air Mouse", "3D Shapes"]
subOptions = {
    "Whiteboard": ["Red", "Green", "Blue", "Yellow", "White", "Eraser"],
    "Air Mouse": [],
    "3D Shapes": ["Cube", "Sphere", "Import"]
}

currentMode = 0
# currentSubOption = 0
PANEL_W = 160
PANEL_TAB_W = 20
BUTTON_H = 85
BUTTON_PADDING = 40

panelOpen = False
panelX = SCREEN_W - PANEL_TAB_W  # starts as just the tab

#GUI 
panelImgs = [
    cv2.imread("GUI/panel0.png"),
    cv2.imread("GUI/panel1.png"),
    cv2.imread("GUI/panel2.png")
]

# Scale down from 2x to 1x
panelImgs = [cv2.resize(img, (PANEL_W, SCREEN_H)) for img in panelImgs]

#SUB GUI
subPanelImgs = [
    [cv2.resize(cv2.imread(f"GUI/Wpanel{i}.png"), (960, 240)) for i in range(5)],
    [],
    [cv2.resize(cv2.imread(f"GUI/Dpanel{i}.png"), (960, 240)) for i in range(3)]
]

subButtonRects = [
    [(28,50,180,203),(212,50,364,203),(396,50,548,203),(580,50,732,203),(764,50,916,203)],
    [],
    [(59,39,250,230),(385,39,576,230),(711,39,902,230)]
]

subPanelOpen = False
currentSubOption = 0
subPanelY = -240  # starts hidden above screen

# Initialize
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_H)
SCREEN_W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
SCREEN_H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Camera resolution: {SCREEN_W}x{SCREEN_H}")

detector = HandDetector(maxHands=2)

gestureTrackerR = GestureTracker(swipeThreshold=100)   # handles LEFT/RIGHT
gestureTrackerL = GestureTracker()
subHoverTracker = GestureTracker()

def drawText(img, text, pos, fontPath, fontSize, color=(255, 255, 255)):
    imgPil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(imgPil)
    font = ImageFont.truetype(fontPath, fontSize)
    
    # Calculate text width for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    textW = bbox[2] - bbox[0]
    x = pos[0] - textW // 2
    y = pos[1]
    
    draw.text((x, y), text, font=font, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(imgPil), cv2.COLOR_RGB2BGR)

def drawPanel(img, panelOpen, currentMode, modes, panelImgs, hoveredBtn=-1):
    h, w = SCREEN_H, SCREEN_W
    buttons = []
    if panelOpen:
        panelX = w - PANEL_W
        panelImg = panelImgs[currentMode]
        overlay = img.copy()
        overlay[0:h, panelX:panelX + PANEL_W] = panelImg
        cv2.addWeighted(overlay, 0.90, img, 0.10, 0, img)
    else:
        # Draw tab
        overlay = img.copy()
        cv2.rectangle(overlay, (w - PANEL_TAB_W, h//4), (w, 3*h//4), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
        cv2.putText(img, "<", (w - PANEL_TAB_W + 2, h//2),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    return img

def getButtonRects(modes):
    buttons = []
    totalHeight = len(modes) * BUTTON_H + (len(modes) - 1) * BUTTON_PADDING
    startY = (SCREEN_H - totalHeight) // 2
    for i in range(len(modes)):
        btnY = startY + i * (BUTTON_H + BUTTON_PADDING)
        btnX = SCREEN_W - PANEL_W + 10
        buttons.append((btnX, btnY, SCREEN_W - 10, btnY + BUTTON_H))
    return buttons

def drawSubPanel(img, subPanelOpen, currentMode, currentSubOption, subPanelImgs, hoveredSubBtn=-1):
    if not subPanelOpen or not subPanelImgs[currentMode]:
        return img
    
    panelImg = subPanelImgs[currentMode][currentSubOption]
    x_start = (SCREEN_W - 960) // 2
    
    overlay = img.copy()
    overlay[0:240, x_start:x_start+960] = panelImg
    cv2.addWeighted(overlay, 0.75, img, 0.25, 0, img)
    
    return img

cv2.namedWindow("Gesture Lab", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Gesture Lab", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
hoverTracker = GestureTracker()
buttons = getButtonRects(modes)
while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=True, flip=True)

    rightHand = None
    leftHand = None

    for hand in hands:
        if hand.handedness == "Right":
            rightHand = hand
        else:
            leftHand = hand

    gestureTrackerR.update(rightHand)
    gestureTrackerL.update(leftHand)

    if rightHand:
        swipe = gestureTrackerR.detectSwipe(img.shape)
        if swipe == "LEFT" and leftHand and leftHand.isFingerUp(INDEX) and leftHand.isFingerUp(MIDDLE) and sum(leftHand.fingersUp()) == 2:
            panelOpen = True
        if swipe == "RIGHT" and leftHand and leftHand.isFingerUp(INDEX) and leftHand.isFingerUp(MIDDLE) and sum(leftHand.fingersUp()) == 2:
            panelOpen = False
        if swipe == "DOWN" :
            if subPanelImgs[currentMode]:
                subPanelOpen = True
        if swipe == "UP" :
            subPanelOpen = False
    else:
        gestureTrackerR.update(None)

    hoveredBtn = -1
    if panelOpen and rightHand:
        cursor = rightHand.selectionCursor()
        if cursor:
            cx, cy = cursor
            cv2.circle(img, (cx, cy), 10, (0, 255, 255), cv2.FILLED)
            
            hovering = False
            for i, (x1, y1, x2, y2) in enumerate(buttons):
                if x1 < cx < x2 and y1 < cy < y2:
                    hoveredBtn = i
                    hovering = True
                    result = hoverTracker.detectHover(rightHand)
                    if result:
                        currentMode = i
                        currentSubOption = 0
                        panelOpen = False
                        notification = f"Selected: {modes[i]}"
                        notificationTimer = time.time()
                    break
            
            if not hovering:
                hoverTracker.detectHover(None)
        else:
            hoverTracker.detectHover(None)
    
    hoveredSubBtn = -1
    if subPanelOpen and rightHand and subButtonRects[currentMode]:
        cursor = rightHand.selectionCursor()
        if cursor:
            cx, cy = cursor
            
            # offset cursor by panel x start position
            panelStartX = (SCREEN_W - 960) // 2
            
            hovering = False
            for i, (x1, y1, x2, y2) in enumerate(subButtonRects[currentMode]):
                # shift button rects by panel x offset
                if (x1 + panelStartX) < cx < (x2 + panelStartX) and y1 < cy < y2:
                    hoveredSubBtn = i
                    hovering = True
                    if subHoverTracker.detectHover(rightHand):
                        currentSubOption = i
                        subPanelOpen = False
                        notification = f"Selected: {subOptions[modes[currentMode]][i]}"
                        notificationTimer = time.time()
                    break
            
            if not hovering:
                subHoverTracker.detectHover(None)
        else:
            subHoverTracker.detectHover(None)

    img = drawPanel(img, panelOpen, currentMode, modes, panelImgs, hoveredBtn)

    if notification and time.time() - notificationTimer < 1.5:
        img = drawText(img, notification, (SCREEN_W // 2, 30), FONT_PATH, 36)
    img = drawSubPanel(img, subPanelOpen, currentMode, currentSubOption, subPanelImgs)
    if currentMode == 0:
        img = whiteboard.update(img, rightHand, leftHand, currentSubOption)
    elif currentMode == 1:
        airmouse.update(img, rightHand)
    elif currentMode == 2:
        img = shapes3d.update(img, rightHand, leftHand, currentSubOption)

    cv2.imshow("Gesture Lab", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.detector.close()
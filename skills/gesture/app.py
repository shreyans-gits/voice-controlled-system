import cv2
from HandTracker import HandDetector, GestureTracker
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import time
import argparse
import os
from whiteboard import Whiteboard
from shapes3d import Shapes3D

parser = argparse.ArgumentParser(description="NOVA Dedicated Interface Subprocess")
parser.add_argument('--mode', type=str, default='whiteboard', choices=['whiteboard', 'shapes3d'], 
                    help="Target module to lock onto: 'whiteboard' or 'shapes3d'")
parser.add_argument('--sub', type=int, default=0, 
                    help="Sub-option index (Whiteboard: 0-5 color/erase | Shapes3D: 0=Voxel, 1=Sphere, 2=Import)")
parser.add_argument('--file', type=str, default=None, help="Absolute path to an input .obj or .json file")
args = parser.parse_args()

SCREEN_W, SCREEN_H = 1280, 720
FONT_PATH = "GUI/open_sans.ttf"

notification = ""
notificationTimer = 0
hoveredSubBtn = -1

whiteboard = Whiteboard(SCREEN_W, SCREEN_H)
shapes3d = Shapes3D(SCREEN_W, SCREEN_H)

currentMode = args.mode          # 'whiteboard' or 'shapes3d'
currentSubOption = args.sub      # Target index within that module

if args.file and currentMode == 'shapes3d':
    if os.path.exists(args.file):
        shapes3d.loadModel(args.file)
        shapes3d.scale = 200
        shapes3d.currentSubOption = 2  # Match layout state internally to bypass wipe
        currentSubOption = 2           # Force Sub-Option to 2 (Import/Display)
        notification = "Loaded Generated Model"
        notificationTimer = time.time()
    else:
        notification = "Error: File Not Found"
        notificationTimer = time.time()

# Dict maps for human-readable notifications
subOptionsNames = {
    "whiteboard": ["Red", "Green", "Blue", "Yellow", "Eraser"],
    "shapes3d": ["Voxel Editor", "Sphere Wireframe", "Imported Asset View"]
}

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_and_resize_gui(relative_path, target_size=(960, 240)):
    full_path = os.path.join(CURRENT_DIR, relative_path)
    img = cv2.imread(full_path)
    if img is None:
        print(f"Warning: GUI asset missing at {full_path}. Generating temporary dark canvas.")
        return np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
    return cv2.resize(img, target_size)

subPanelImgs = {
    "whiteboard": [load_and_resize_gui(f"GUI/Wpanel{i}.png", (960, 240)) for i in range(5)],
    "shapes3d": [load_and_resize_gui(f"GUI/Dpanel{i}.png", (960, 240)) for i in range(3)]
}

subButtonRects = {
    "whiteboard": [(28,50,180,203),(212,50,364,203),(396,50,548,203),(580,50,732,203),(764,50,916,203)],
    "shapes3d": [(59,39,250,230),(385,39,576,230),(711,39,902,230)]
}

subPanelOpen = False

def drawText(img, text, pos, fontPath, fontSize, color=(255, 255, 255)):
    try:
        imgPil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(imgPil)
        font = ImageFont.truetype(fontPath, fontSize)
        bbox = draw.textbbox((0, 0), text, font=font)
        textW = bbox[2] - bbox[0]
        x = pos[0] - textW // 2
        y = pos[1]
        draw.text((x, y), text, font=font, fill=(color[2], color[1], color[0]))
        return cv2.cvtColor(np.array(imgPil), cv2.COLOR_RGB2BGR)
    except Exception:
        return img

def drawSubPanel(img, subPanelOpen, currentMode, currentSubOption, subPanelImgs):
    if not subPanelOpen:
        return img
    
    panelImg = subPanelImgs[currentMode][currentSubOption]
    x_start = (SCREEN_W - 960) // 2
    overlay = img.copy()
    overlay[0:240, x_start:x_start+960] = panelImg
    cv2.addWeighted(overlay, 0.75, img, 0.25, 0, img)
    return img

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_H)

detector = HandDetector(maxHands=2)
gestureTrackerR = GestureTracker(swipeThreshold=100)
gestureTrackerL = GestureTracker()
subHoverTracker = GestureTracker()

cv2.namedWindow("img", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("img", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=True, flip=True)

    rightHand = next((h for h in hands if h.handedness == "Right"), None)
    leftHand = next((h for h in hands if h.handedness == "Left"), None)

    gestureTrackerR.update(rightHand)
    gestureTrackerL.update(leftHand)

    if rightHand:
        swipe = gestureTrackerR.detectSwipe(img.shape)
        if swipe == "DOWN":
            subPanelOpen = True
        if swipe == "UP":
            subPanelOpen = False

    if subPanelOpen and rightHand:
        cursor = rightHand.selectionCursor()
        if cursor:
            cx, cy = cursor
            cv2.circle(img, (cx, cy), 10, (0, 255, 255), cv2.FILLED)
            panelStartX = (SCREEN_W - 960) // 2
            for i, (x1, y1, x2, y2) in enumerate(subButtonRects[currentMode]):
                if (x1 + panelStartX) < cx < (x2 + panelStartX) and y1 < cy < y2:
                    hoveredSubBtn = i
                    if subHoverTracker.detectHover(rightHand):
                        currentSubOption = i
                        subPanelOpen = False
                        notification = f"Selected: {subOptionsNames[currentMode][i]}"
                        notificationTimer = time.time()
                    break

    if notification and time.time() - notificationTimer < 1.5:
        img = drawText(img, notification, (SCREEN_W // 2, 30), FONT_PATH, 36)

    img = drawSubPanel(img, subPanelOpen, currentMode, currentSubOption, subPanelImgs)

    if currentMode == "whiteboard":
        img = whiteboard.update(img, rightHand, leftHand, currentSubOption)
    elif currentMode == "shapes3d":
        img = shapes3d.update(img, rightHand, leftHand, currentSubOption)

    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("img", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
detector.detector.close()
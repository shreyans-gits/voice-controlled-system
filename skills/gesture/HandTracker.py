import cv2
import mediapipe as mp
import math
import os
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from collections import deque
import time

THUMB = 0
INDEX = 1
MIDDLE = 2
RING = 3
PINKY = 4

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]

class Hand:
    def __init__(self, landmarks, handedness, img_shape):
        self.landmarks = landmarks
        self.handedness = handedness
        self.img_shape = img_shape

        self.tipIds = [4,8,12,16,20]
        self.points = []
        self.bbox = ()
        self._extractPoints()
        self._extractBbox()

        self.hoverStart = None
        self.hoverPos = None
        self.hoverThreshold = 40
        self.hoverTime = 2

    def _extractPoints(self):
        h, w, c = self.img_shape
        for lm in self.landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            self.points.append((cx, cy))

    def _extractBbox(self):
        xList = [p[0] for p in self.points]
        yList = [p[1] for p in self.points]
        xmin, xmax = min(xList), max(xList)
        ymin, ymax = min(yList), max(yList)
        self.bbox = (xmin, ymin, xmax, ymax)

    def fingersUp(self):
        fingers = []

        if self.handedness == "Right":
            fingers.append(1 if self.points[4][0] < self.points[3][0] else 0)
        else:
            fingers.append(1 if self.points[4][0] > self.points[3][0] else 0)

        for tipId in self.tipIds[1:]:
            fingers.append(1 if self.points[tipId][1] < self.points[tipId - 2][1] else 0)

        return fingers
    
    def findDistance(self, p1, p2):
        x1, y1 = self.points[p1]
        x2, y2 = self.points[p2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        return length, (x1, y1), (x2, y2), (cx, cy)
    
    def isFingerUp(self, fingerId):
        fingers = self.fingersUp()
        return fingers[fingerId] == 1
    
    def center(self):
        xmin, ymin, xmax, ymax = self.bbox
        return ((xmin + xmax) // 2, (ymin + ymax) // 2)
    
    def selectionCursor(self):
        fingers = self.fingersUp()
        if fingers[INDEX] == 1 and fingers[MIDDLE] == 1:
            x1, y1 = self.points[8]   # index tip
            x2, y2 = self.points[12]  # middle tip
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            return (cx, cy)
        return None
    
    def isPinching(self, threshold=40):
        length, _, _, _ = self.findDistance(4, 8)
        return length < threshold
        

class HandDetector:
    def __init__(self, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        model_path = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            num_hands=maxHands,
            min_hand_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon,
            running_mode=vision.RunningMode.VIDEO
        )

        self.detector = HandLandmarker.create_from_options(options)

    def findHands(self, img, draw=True, flip=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)

        timestamp = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
        results = self.detector.detect_for_video(mp_image, timestamp)

        hands = []

        if results.hand_landmarks:
            for i, handLms in enumerate(results.hand_landmarks):
                handedness = results.handedness[i][0].display_name
                if flip:
                    handedness = "Left" if handedness == "Right" else "Right"
                hand = Hand(handLms, handedness, img.shape)
                hands.append(hand)

                if draw:
                    self._drawHand(img, hand)

        return hands, img
    
    def _drawHand(self, img, hand):
        # Draw landmarks
        for point in hand.points:
            cv2.circle(img, point, 4, (255, 255, 255), cv2.FILLED)

        # Draw connections between landmarks
        for connection in HAND_CONNECTIONS:
            p1 = hand.points[connection[0]]
            p2 = hand.points[connection[1]]
            cv2.line(img, p1, p2, (255, 255, 255), 2)

        # Draw bounding box
        xmin, ymin, xmax, ymax = hand.bbox
        cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 0, 0), 2)

        # Draw handedness label
        cv2.putText(img, hand.handedness, (xmin - 20, ymin - 30),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 0), 2)
        

class GestureTracker:
    def __init__(self, historyLength=10, swipeThreshold=100):
        self.history = deque(maxlen=historyLength)
        self.swipeThreshold = swipeThreshold
        self.hoverStart = None
        self.hoverPos = None
        self.hoverThreshold = 40

    def detectSwipe(self, imgShape):
        if len(self.history) < self.history.maxlen:
            return None
        h, w, c = imgShape
        center = self.history[-1]
        first = self.history[0]
        last = self.history[-1]


        xc1 = first[0]
        xcl = last[0]
        yc1 = first[1]
        ycl = last[1]

        if center[0] > w * 0.7:
            if xcl - xc1 >= self.swipeThreshold:
                return "RIGHT"
            if xcl - xc1 <= -self.swipeThreshold:
                return "LEFT"
        if center[1] < h * 0.3:
            if ycl - yc1 >= self.swipeThreshold:
                return "DOWN"
            if ycl - yc1 <= -self.swipeThreshold:
                return "UP"
        return None
    
    def update(self, hand):
        if hand is not None:
            self.history.append(hand.center())
        else:
            self.history.clear()
    
    def detectHover(self, hand):
        if hand is None:
            self.hoverStart = None
            self.hoverPos = None
            return False
        centre = hand.center()
        if self.hoverPos == None:
            self.hoverPos =  centre
            self.hoverStart = time.time()
            return False   
        else:
            distance = math.hypot(centre[0] - self.hoverPos[0], centre[1] - self.hoverPos[1])
            if distance < self.hoverThreshold:
                if time.time() - self.hoverStart >= 2:
                    return True
            else:
                self.hoverPos = None
                self.hoverStart = time.time()
                return False
        return False
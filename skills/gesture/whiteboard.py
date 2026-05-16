import cv2
import numpy as np
from HandTracker import INDEX, MIDDLE
import time

class Whiteboard:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.imgCanvas = np.zeros((height, width, 3), np.uint8)
        self.xp, self.yp = 0, 0
        self.brushThickness = 15
        self.eraserThickness = 50
        self.colors = {
            0: (0, 0, 255),    # Red
            1: (0, 255, 0),    # Green
            2: (255, 0, 0),    # Blue
            3: (0, 255, 255),  # Yellow
            4: (0, 0, 0)       # Eraser
        }
        self.drawColor = self.colors[0]

        self.stableThickness = 15
        self.lastThickness = 15
        self.thicknessHoldStart = None
        self.holdDuration = 1

    def update(self, img, rightHand, leftHand, currentSubOption):
        self.drawColor = self.colors[currentSubOption]
        
        # Adjust eraser thickness
        thickness = self.eraserThickness if currentSubOption == 4 else self.brushThickness

        if rightHand:
            fingers = rightHand.fingersUp()
            x1, y1 = rightHand.points[8]   # index tip

            # Drawing mode — only index finger up
            if fingers[INDEX] == 1 and fingers[MIDDLE] == 0:
                cv2.circle(img, (x1, y1), thickness // 2, self.drawColor, cv2.FILLED)

                if self.xp == 0 and self.yp == 0:
                    self.xp, self.yp = x1, y1

                cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.drawColor, thickness)
                self.xp, self.yp = x1, y1

            # Selection mode — index and middle up, reset previous point
            elif fingers[INDEX] == 1 and fingers[MIDDLE] == 1:
                self.xp, self.yp = 0, 0

            # Fist or no fingers — reset previous point
            else:
                self.xp, self.yp = 0, 0

        if(
            rightHand and leftHand
            and sum(rightHand.fingersUp()) == 0 and
            sum(leftHand.fingersUp()) == 5
        ) :
            self.imgCanvas[:] = self.drawColor

        if(
            rightHand and leftHand
            and sum(rightHand.fingersUp()) == 5 and
            sum(leftHand.fingersUp()) == 0
        ) :
            self.imgCanvas[:] = (0,0,0) 

        # Left hand controls brush thickness via pinch
        if leftHand:
            length, p1, p2, mid = leftHand.findDistance(4, 8)
            rawThickness = int(np.interp(length, [20, 150], [5, 40]))
            
            # check if thickness is stable within +-10
            if abs(rawThickness - self.lastThickness) <= 10:
                if self.thicknessHoldStart is None:
                    self.thicknessHoldStart = time.time()
                elif time.time() - self.thicknessHoldStart >= self.holdDuration:
                    self.stableThickness = rawThickness
            else:
                self.lastThickness = rawThickness
                self.thicknessHoldStart = None

            self.brushThickness = self.stableThickness

            # Draw line between thumb and index tip
            cv2.line(img, p1, p2, (255, 255, 255), 2)
            
            # Draw circle showing current thickness
            cv2.circle(img, mid, self.brushThickness // 2, self.drawColor, cv2.FILLED)
            
            # Show thickness value
            cv2.putText(img, str(self.brushThickness), 
                        (mid[0] + 15, mid[1]), 
                        cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)

        return self.mergeCanvas(img)

    def mergeCanvas(self, img):
        imgGray = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, self.imgCanvas)
        return img
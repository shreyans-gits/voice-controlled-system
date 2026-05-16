import cv2
import numpy as np
import math
from HandTracker import INDEX, THUMB, MIDDLE, PINKY, RING

class CubeEditor:
    def __init__(self, screenW, screenH):
        self.screenW = screenW
        self.screenH = screenH

        self.cubes = []
        self.tempCubes = []
        self.anchorHand = None
        self.state = "IDLE"
        self.extendAxis = None
        self.extendDir = None
        self.extendBase = None
        self.baseExtendPos = None

        self.angleX = 0
        self.angleY = 0
        self.scale = 50
        self.centerX = screenW // 2
        self.centerY = screenH // 2

        self.prevHandPos = None
        self.prevDist = None
        self.selectedCube = None

    def getRotationX(self, angle):
        return np.array([
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle),  np.cos(angle)]
        ])

    def getRotationY(self, angle):
        return np.array([
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)]
        ])

    def getStructureCenter(self):
        if not self.cubes and not self.tempCubes:
            return (0, 0, 0)
        allCubes = self.cubes + self.tempCubes
        xs = [gx + 0.5 for gx, gy, gz in allCubes]
        ys = [gy + 0.5 for gx, gy, gz in allCubes]
        zs = [gz + 0.5 for gx, gy, gz in allCubes]
        return (np.mean(xs), np.mean(ys), np.mean(zs))

    def projectPoint(self, point):
        Rx = self.getRotationX(self.angleX)
        Ry = self.getRotationY(self.angleY)
        cx, cy, cz = self.getStructureCenter()
        p = np.array(point, dtype=float)
        p = p - np.array([cx, cy, cz])  # center it
        p = Ry @ (Rx @ p)
        px = int(p[0] * self.scale + self.centerX)
        py = int(-p[1] * self.scale + self.centerY)
        return (px, py)

    def renderCubes(self, img):
        allCubes = self.cubes + self.tempCubes
        offsets = [
            (0,0,0),(1,0,0),(1,1,0),(0,1,0),
            (0,0,1),(1,0,1),(1,1,1),(0,1,1)
        ]
        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]

        for cube in allCubes:
            gx, gy, gz = cube
            vertices = [[gx+ox, gy+oy, gz+oz] for ox,oy,oz in offsets]
            projected = [self.projectPoint(v) for v in vertices]

            if cube in self.tempCubes:
                color = (0, 0, 255)      # red preview
            elif cube == self.selectedCube:
                color = (0, 255, 0) if self.anchorHand == "Right" else (0, 165, 255)  # green or orange
            else:
                color = (255, 255, 255)  # white default

            for edge in edges:
                cv2.line(img, projected[edge[0]], projected[edge[1]], color, 2)

        return img

    def updateSelection(self, hand, handedness):
        if hand is None:
            return
        cursor = hand.selectionCursor()
        if not cursor or len(self.cubes) == 0:
            return

        minDist = float("inf")
        closestCube = None

        for cube in self.cubes:
            gx, gy, gz = cube
            px, py = self.projectPoint((gx+0.5, gy+0.5, gz+0.5))
            dist = math.hypot(cursor[0]-px, cursor[1]-py)
            if dist < minDist:
                minDist = dist
                closestCube = cube

        if minDist < 50:
            self.selectedCube = closestCube
            self.anchorHand = handedness

    def update(self, img, rightHand, leftHand):

        # IDLE — wait for first pinch to place cube
        if self.state == "IDLE":
            if rightHand and rightHand.isPinching():
                self.cubes.append((0, 0, 0))
                self.anchorHand = "Right"
                self.selectedCube = (0, 0, 0)
                self.state = "PLACED"
            elif leftHand and leftHand.isPinching():
                self.cubes.append((0, 0, 0))
                self.anchorHand = "Left"
                self.selectedCube = (0, 0, 0)
                self.state = "PLACED"

        # PLACED — selection, rotation, transition to EXTENDING
        if self.state == "PLACED":

            # update selection based on whichever hand has cursor active
            self.updateSelection(rightHand, "Right")
            self.updateSelection(leftHand, "Left")

            # rotation — index finger only, not pinching
            rotHand = rightHand if rightHand else leftHand
            if (rotHand and
                rotHand.isFingerUp(INDEX) and
                not rotHand.isFingerUp(MIDDLE) and
                not rotHand.isFingerUp(RING) and
                not rotHand.isFingerUp(PINKY) and
                not rotHand.isPinching()):

                cx, cy = rotHand.center()
                if self.prevHandPos:
                    dx = cx - self.prevHandPos[0]
                    dy = cy - self.prevHandPos[1]
                    self.angleY += dx * 0.01
                    self.angleX += dy * 0.01
                self.prevHandPos = (cx, cy)
            else:
                self.prevHandPos = None

            # transition to EXTENDING
            if (rightHand and leftHand and
                rightHand.isPinching() and leftHand.isPinching()):

                extender = leftHand if self.anchorHand == "Right" else rightHand
                self.extendBase = self.selectedCube if self.selectedCube else self.cubes[-1]
                self.baseExtendPos = extender.center()
                self.tempCubes = []
                self.extendAxis = None
                self.extendDir = None
                self.state = "EXTENDING"

        # EXTENDING — dynamically add/remove temp cubes
        if self.state == "EXTENDING":
            extender = leftHand if self.anchorHand == "Right" else rightHand

            # if either hand stops pinching, lock in
            if not (rightHand and leftHand and
                    rightHand.isPinching() and leftHand.isPinching()):
                self.cubes += [c for c in self.tempCubes if c not in self.cubes]
                self.tempCubes = []
                self.extendAxis = None
                self.extendDir = None
                self.extendBase = None
                self.baseExtendPos = None
                self.state = "PLACED"

            elif extender is not None:
                cx, cy = extender.center()
                bx, by = self.baseExtendPos
                dx = cx - bx
                dy = cy - by

                deadzone = 15
                if self.extendAxis is None:
                    if abs(dx) < deadzone and abs(dy) < deadzone:
                        img = self.renderCubes(img)
                        return img
                    self.extendAxis = "X" if abs(dx) > abs(dy) else "Y"
                    self.extendDir = (1 if dx > 0 else -1) if self.extendAxis == "X" else (-1 if dy > 0 else 1)

                distance = abs(dx) if self.extendAxis == "X" else abs(dy)
                count = max(0, int(distance / 30))

                gx, gy, gz = self.extendBase
                self.tempCubes = []
                for i in range(1, count + 1):
                    if self.extendAxis == "X":
                        newCube = (gx + i * self.extendDir, gy, gz)
                    else:
                        newCube = (gx, gy + i * self.extendDir, gz)
                    if newCube not in self.cubes:
                        self.tempCubes.append(newCube)

        img = self.renderCubes(img)
        return img
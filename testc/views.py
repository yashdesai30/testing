# Create your views here.
import numpy as np
import cv2
from collections import deque
import time
from django.shortcuts import render, redirect
from django.http.response import StreamingHttpResponse

def index(request):
	return render(request, 'home.html')


def gen():
    bpoints = [deque(maxlen=1024)]
    gpoints = [deque(maxlen=1024)]
    rpoints = [deque(maxlen=1024)]
    ypoints = [deque(maxlen=1024)]
    #assigning index values
    blue_index = 0
    green_index = 0
    red_index = 0
    yellow_index = 0
    kernel = np.ones((5,5),np.uint8)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    colorIndex = 0

    #starting the painting window setup
    paintWindow = np.zeros((471,636,3)) + 255
    paintWindow = cv2.circle(paintWindow, (75,45), 35, (0,0,0), 2)
    paintWindow = cv2.circle(paintWindow, (205,45), 35, colors[0], -1)
    paintWindow = cv2.circle(paintWindow, (280,45), 35, colors[1], -1)
    paintWindow = cv2.circle(paintWindow, (355,45), 35, colors[2], -1)
    paintWindow = cv2.circle(paintWindow, (430,45), 35, colors[3], -1)
    cv2.putText(paintWindow, "CLEAR", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(paintWindow, "BLUE", (185, 50), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(paintWindow, "GREEN", (255, 50), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(paintWindow, "RED", (340, 50), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(paintWindow, "YELLOW", (400, 50), cv2.FONT_ITALIC, 0.5, (150,150,150), 2, cv2.LINE_AA)

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        #Flipping the frame just for convenience
        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        u_hue = 153
        u_saturation = 255
        u_value = 255
        l_hue = 64
        l_saturation = 72
        l_value = 49
        
        Upper_hsv = np.array([u_hue,u_saturation,u_value])
        Lower_hsv = np.array([l_hue,l_saturation,l_value])
        frame = cv2.rectangle(frame, (40,1), (140,65), (122,122,122), -1)
        frame = cv2.rectangle(frame, (160,1), (255,65), colors[0], -1)
        frame = cv2.rectangle(frame, (275,1), (370,65), colors[1], -1)
        frame = cv2.rectangle(frame, (390,1), (485,65), colors[2], -1)
        frame = cv2.rectangle(frame, (505,1), (600,65), colors[3], -1)
        cv2.putText(frame, "CLEAR ALL", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 2, cv2.LINE_AA)
        Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
        Mask = cv2.erode(Mask, kernel, iterations=1)
        Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
        Mask = cv2.dilate(Mask, kernel, iterations=1)
        cnts,_ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        center = None
        # Ifthe contours are formed
        if len(cnts) > 0:
        # sorting the contours to find biggest contour
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            # Get the radius of the enclosing circle around the found contour
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            # Draw the circle around the contour
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            # Calculating the center of the detected contour
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
            #checking if any button above the screen is clicked/cursor hovered to
            if center[1] <= 80:
                if 40 <= center[0] <= 140: # Clear Button
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]
                    blue_index = 0
                    green_index = 0
                    red_index = 0
                    yellow_index = 0
                    paintWindow[82:,:,:] = 255
                elif 205 <= center[0] <= 240:
                        colorIndex = 0 # Blue
                elif 280 <= center[0] <= 315:
                        colorIndex = 1 # Green
                elif 355 <= center[0] <= 390:
                        colorIndex = 2 # Red
                elif 430 <= center[0] <= 465:
                        colorIndex = 3 # Yellow
            else :
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(center)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(center)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(center)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(center)
        else:
            bpoints.append(deque(maxlen=512))
            blue_index += 1
            gpoints.append(deque(maxlen=512))
            green_index += 1
            rpoints.append(deque(maxlen=512))
            red_index += 1
            ypoints.append(deque(maxlen=512))
            yellow_index += 1
        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2,cv2.LINE_AA)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2,cv2.LINE_AA)
        ret, jpeg = cv2.imencode('.jpg', paintWindow)
        cv2.imshow("Tracking", frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + 
                b'\r\n\r\n')
def test(request):
	return StreamingHttpResponse(gen(),content_type='multipart/x-mixed-replace; boundary=frame')

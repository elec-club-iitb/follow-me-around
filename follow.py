import cv2
import numpy as np
from time import time

camera = cv2.VideoCapture(1)
frames = []
center = (0, 0)
centers = []

while True:
    t = time()
    s, im = camera.read()

    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    frames.append(hsv)

    if len(frames) == 3:
        diff1 = cv2.absdiff(frames[0], frames[1])
        diff2 = cv2.absdiff(frames[1], frames[2])
        diff = (diff1 + diff2)/2
        cv2.imshow("Avg", (diff1+diff2)/2)
        diff[:,:,0] = 0
        diff[:,:,1] = 0

        r = diff[:,:,2]
        rt = 50
        mask = r < rt
        diff[mask] = 0
        diff[~mask] = 255

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6,6))
        diff = cv2.erode(diff, kernel)

        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        # diff = cv2.dilate(diff, kernel)

        indices = np.nonzero(diff[:,:,2])
        center = (np.sum(indices[1])/len(indices[1]),
                    np.sum(indices[0])/len(indices[0]))
        centers.append(center)
        if len(centers) > 10:
            centers.pop(0)

        for c in centers:
            cv2.circle(diff, c, 20, [0, 0, 255])
        cv2.imshow("diff", diff)

        frames = []

    im2 = im.copy()
    for c in centers:
        cv2.circle(im2, c, 20, [0,0,0])
    cv2.imshow("Test frame", im2)

    k = cv2.waitKey(5)

    if k & 0xFF == 27:
        break

    print(time() - t)

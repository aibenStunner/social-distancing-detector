# imports
from .config import NMS_THRESH
from .config import MIN_CONF
import numpy as np
import cv2

# function to detect people
def detect_people(frame, net, ln, personIdx=0):
    # grab dimensions of the frame and initialize the list of results
    (H, W) = frame.shape[:2]
    results = []

    # construct a blob from the input frame and then perfrom a forward pass
    # of the YOLO object detector, giving us the bounding boxes and
    # associated probabilities
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    # initialize lists of detected bounding boxes, centroids, and confidence
    boxes = []
    centroids = []
    confidences = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract teh class ID and confidence(probability) of the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            # filter detections by (1) ensuring that the object detected was a person and
            # (2) that the minimum confidence is met
            if classID == personIdx and confidence > MIN_CONF:
                # scale the bounding box coordinates back relative to the size of 
                # the image, keeping in mind that YOLO actually returns the center (x, y)-coordinates
                # of the bounding box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x,y)-coordinates to derive the top and left corner of 
                # the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update the list of bounding box coordinates, centroids and confidences
                boxes.append([x, y, int(width), int(height)])
                centroids.append((centerX, centerY))
                confidences.append(float(confidence))

    # apply non-maxima suppression to suppress weak, overlapping bounding boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONF, NMS_THRESH)

    # ensure at least one detection exists
    if len(idxs) > 0:
        # loop over the indexes being kept
        for i in idxs.flatten():
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            # update the results list to consist of the person prediction probability, 
            # bounding box coordinates, and the centroid
            r = (confidences[i], (x, y, x + w, y + h), centroids[i])
            results.append(r)

    # return the list of results
    return results

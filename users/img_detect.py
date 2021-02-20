import time
import cv2
import argparse
import numpy as np
from urllib.request import urlopen
import os.path as path

names = path.abspath(path.join(__file__ ,"../../YOLOv3/fyp.names"))
weights = path.abspath(path.join(__file__ ,"../../YOLOv3/fyp.weights"))
cfg = path.abspath(path.join(__file__ ,"../../YOLOv3/fyp.cfg"))

net = cv2.dnn.readNet(weights, cfg)
layer_names = net.getLayerNames()   # returns a list of all layer names (conv,bn,relu,yolo, etc)
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()] # creates list of yolo layers using indices of yolo layers


def detect_object(img_link):
    detected = False
    start = time.time()

    def draw_prediction(img, class_id, x, y, x_plus_w, y_plus_h):
        label = str(classes[class_id])
        color = (255,0,0)
        cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
        cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    try:
        resp = urlopen(img_link)
    except Exception:
        print("Error in accessing image")
        return False

    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    width = image.shape[1]
    height = image.shape[0]

    # Create a list of all classes in names file
    classes = None
    with open(names, 'r') as f:
        classes = [line.strip() for line in f.readlines()] 

    blob = cv2.dnn.blobFromImage(image, scalefactor=0.00392, size=(416, 416), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)
    # outputs contains all information in the image

    class_ids = []
    confidences = []
    boxes = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                print("Object detected, Confidence:", confidence)
                detected = True
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # Applying non-max suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4) # returns indices of labels that are not suppressed

    # Putting bounding boxes and label
    no_objects_detected = len(boxes)
    for i in range(no_objects_detected):
        if i in indices:
            x, y, w, h = boxes[i]
            draw_prediction(image, class_ids[i], round(x), round(y), round(x + w), round(y + h))

    cv2.imshow("object detection", image)

    end = time.time()
    print("YOLO Execution time: " + str(end-start) + "\n")

    cv2.waitKey(2000)

    cv2.destroyAllWindows()

    return detected
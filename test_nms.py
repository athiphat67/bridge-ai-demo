import cv2
import numpy as np

boxes = []
scores = []
keep = cv2.dnn.NMSBoxes(boxes, scores, 0.25, 0.7)
print("keep:", keep)
print("np.array(keep):", np.array(keep))
print("np.array(keep).reshape(-1):", np.array(keep).reshape(-1))


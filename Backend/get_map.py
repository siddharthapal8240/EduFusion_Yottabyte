import pickle
import cv2
import numpy as np

cam_id = 1
width, height = 1920, 1080


cap = cv2.VideoCapture(cam_id)
cap.set(3, width)
cap.set(4, height)
points = np.zeros((4, 2), int)
counter = 0
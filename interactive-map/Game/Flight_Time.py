import pickle
import cv2
import cvzone
import numpy as np
from cvzone.HandTrackingModule import HandDetector

cam_id = 0
width, height = 1920, 1080
map_file_path = "../GetCornerPoints/map.p"
countries_file_path = "../Get_Country_Polygon/countries.p"


file_obj = open(map_file_path, 'rb')
map_points = pickle.load(file_obj)
file_obj.close()
print(f"Loaded map coordinates.")

if countries_file_path:
    file_obj = open(countries_file_path, 'rb')
    polygons = pickle.load(file_obj)
    file_obj.close()
    print(f"Loaded {len(polygons)} countries.")
else:
    polygons = []

cap = cv2.VideoCapture(cam_id)
cap.set(3, width)
cap.set(4, height)
counter = 0
detector = HandDetector(staticMode=False,
                        maxHands=2,
                        modelComplexity=1,
                        detectionCon=0.5,
                        minTrackCon=0.5)

flight_time_list = [["Russia", "Australia", "22 hours"],
                    ["USA", "Canada", "3 hours"],
                    ["Australia", "India", "13 hours"],
                    ["Australia", "Pakistan", "13 hours"],
                    ["Saudi Arabia", "USA", "14 hours"],
                    ]


def warp_image(img, points, size=[1920, 1080]):
    pts1 = np.float32([points[0], points[1], points[2], points[3]])
    pts2 = np.float32([[0, 0], [size[0], 0], [0, size[1]], [size[0], size[1]]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgOutput = cv2.warpPerspective(img, matrix, (size[0], size[1]))
    return imgOutput, matrix


def warp_single_point(point, matrix):

    point_homogeneous = np.array([[point[0], point[1], 1]], dtype=np.float32)

    point_homogeneous_transformed = np.dot(matrix, point_homogeneous.T).T


    point_warped = point_homogeneous_transformed[0, :2] / point_homogeneous_transformed[0, 2]
    point_warped = int(point_warped[0]), int(point_warped[1])

    return point_warped


def inverse_warp_image(img, imgOverlay, map_points):
    map_points = np.array(map_points, dtype=np.float32)

    destination_points = np.array([[0, 0], [imgOverlay.shape[1] - 1, 0], [0, imgOverlay.shape[0] - 1],
                                   [imgOverlay.shape[1] - 1, imgOverlay.shape[0] - 1]], dtype=np.float32)

    M = cv2.getPerspectiveTransform(destination_points, map_points)

    warped_overlay = cv2.warpPerspective(imgOverlay, M, (img.shape[1], img.shape[0]))

    result = cv2.addWeighted(img, 1, warped_overlay, 0.65, 0, warped_overlay)

    return result


def get_finger_location(img, imgWarped):

    hands, img = detector.findHands(img, draw=False, flipType=True)
    if hands:
        hand1 = hands[0]
        indexFinger = hand1["lmList"][8][0:2]
        warped_point = warp_single_point(indexFinger, matrix)
        warped_point = int(warped_point[0]), int(warped_point[1])
        print(indexFinger, warped_point)
        cv2.circle(imgWarped, warped_point, 5, (255, 0, 0), cv2.FILLED)
        if len(hands) == 2:
            hand2 = hands[1]
            indexFinger2 = hand2["lmList"][8][0:2]  # List of 21 landmarks for the first hand
            warped_point2 = warp_single_point(indexFinger2, matrix)
            cv2.circle(imgWarped, warped_point2, 5, (255, 0, 255), cv2.FILLED)
            warped_point = [warped_point, warped_point2]

    else:
        warped_point = None

    return warped_point


def create_overlay_image(polygons, warped_point, imgOverlay):
    if isinstance(warped_point, list):
        check = []
        for warp_point in warped_point:
            for polygon, name in polygons:
                polygon_np = np.array(polygon, np.int32).reshape((-1, 1, 2))
                result = cv2.pointPolygonTest(polygon_np, warp_point, False)
                if result >= 0:
                    cv2.polylines(imgOverlay, [np.array(polygon)], isClosed=True, color=(0, 255, 0), thickness=2)
                    cv2.fillPoly(imgOverlay, [np.array(polygon)], (0, 255, 0))
                    cvzone.putTextRect(imgOverlay, name, polygon[0], scale=1, thickness=1)
                    check.append(name)
        if len(check) == 2:
            cv2.line(imgOverlay, warped_point[0], warped_point[1], (0, 255, 0), 10)
            for flight_time in flight_time_list:
                if check[0] in flight_time and check[1] in flight_time:
                    cvzone.putTextRect(imgOverlay, flight_time[1] + " to " + flight_time[0], (0, 100), scale=8,
                                       thickness=5)
                    cvzone.putTextRect(imgOverlay, flight_time[2], (0, 200), scale=8, thickness=5)
    else:
        for polygon, name in polygons:
            polygon_np = np.array(polygon, np.int32).reshape((-1, 1, 2))
            result = cv2.pointPolygonTest(polygon_np, warped_point, False)
            if result >= 0:
                cv2.polylines(imgOverlay, [np.array(polygon)], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.fillPoly(imgOverlay, [np.array(polygon)], (0, 255, 0))
                cvzone.putTextRect(imgOverlay, name, polygon[0], scale=1, thickness=1)
                cvzone.putTextRect(imgOverlay, name, (0, 100), scale=8, thickness=5)

    return imgOverlay


while True:
    success, img = cap.read()
    imgWarped, matrix = warp_image(img, map_points)
    imgOutput = img.copy()

    warped_point = get_finger_location(img, imgWarped)

    h, w, _ = imgWarped.shape
    imgOverlay = np.zeros((h, w, 3), dtype=np.uint8)

    if warped_point:
        imgOverlay = create_overlay_image(polygons, warped_point, imgOverlay)
        imgOutput = inverse_warp_image(img, imgOverlay, map_points)

    cv2.imshow("Output Image", imgOutput)

    key = cv2.waitKey(1)
import cv2
import mediapipe as mp
import numpy as np
import math
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


camera = cv2.VideoCapture(0)
# use mediapipe to detect hands in a live camera feed
all_points = []
thickness_arr = []
size = (640, 480)
MAX_THICKNESS = 13
THUMB_INDEX_STRETCH = 0.25
thickness = 4

def draw_all_points():
  for i in range(len(all_points) - 1):
    cv2.circle(image, all_points[i], thickness_arr[i], (0, 255, 0), -1)

def fingers_up(up_fingers):
  fingers = [4, 8, 12, 16, 20]
  down_fingers = list(set(fingers) - set(up_fingers))
  palm_id = [0, 1, 2, 5, 9, 13, 17]
  points = []
  for palm in palm_id:
      points.append([hand_landmarks.landmark[palm].x * size[0], hand_landmarks.landmark[palm].y * size[1]])
  palm = np.array(points).reshape((-1,1,2)).astype(np.int32)
  kernel = np.ones((2,2),np.uint8)
  dilated_palm = cv2.dilate(palm.astype(np.uint8), kernel, iterations = 1).astype(np.int32)
  dilated_palm = cv2.convexHull(dilated_palm, False)
  
  for finger in up_fingers:
    cv2.circle(image, (int(hand_landmarks.landmark[finger].x * size[0]), int(hand_landmarks.landmark[finger].y * size[1])), 5, (0, 0, 255), -1)
    if cv2.pointPolygonTest(palm, (hand_landmarks.landmark[finger].x * size[0], hand_landmarks.landmark[finger].y * size[1]), False) > 0:
      return False
  for finger in down_fingers:
    cv2.circle(image, (int(hand_landmarks.landmark[finger].x * size[0]), int(hand_landmarks.landmark[finger].y * size[1])), 5, (0, 0, 255), -1)
    if cv2.pointPolygonTest(palm, (hand_landmarks.landmark[finger].x * size[0], hand_landmarks.landmark[finger].y * size[1]), False) < 0:
        return False
  return True 


with mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as hands:
  while camera.isOpened():
    success, image = camera.read()
    if not success:
      print("Ignoring empty camera frame.")
      continue

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, size)
    image.flags.writeable = False
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())

        handedness = results.multi_handedness[0].classification[0].label
        if handedness == "Right":
          if fingers_up([8]):
            all_points.append((int(hand_landmarks.landmark[8].x * image.shape[1]), int(hand_landmarks.landmark[8].y * image.shape[0])))
            thickness_arr.append(thickness)
          elif fingers_up([4, 8, 20]):
            THUMB_INDEX_STRETCH = math.sqrt((hand_landmarks.landmark[4].x - hand_landmarks.landmark[8].x) ** 2 + (hand_landmarks.landmark[4].y - hand_landmarks.landmark[8].y) ** 2)
          elif fingers_up([4, 8]):
            length = math.sqrt((hand_landmarks.landmark[4].x - hand_landmarks.landmark[8].x) ** 2 + (hand_landmarks.landmark[4].y - hand_landmarks.landmark[8].y) ** 2)
            thickness = int(length * MAX_THICKNESS / THUMB_INDEX_STRETCH)
    draw_all_points()
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
  

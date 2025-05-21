# Imports
import cv2
# import RPi.GPIO as GPIO
from picamera2 import Picamera2
from ultralytics import YOLO
import time

from mobile import robotMovements as rMove

# Set up the camera with Picam
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 1280)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Load YOLOv8
# model_objects = YOLO("yolov8n.pt")
model_pose  = YOLO("yolo11n-pose.pt")

# Buzzer set
# BUZZER_PIN = 17  # GPIO17 (pin 11)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(BUZZER_PIN, GPIO.OUT)


def init_variables():
    # Variables
    global init_time, dicc_body_parts, person_detected, horizont_point, head_point, laying_dow
    global sitting, pre_left_ankle, pre_rigth_ankle, buzzer, fall_down, count_down
    fall_down = False
    buzzer = True
    init_time = 0
    count_down = 0
    dicc_body_parts = {
        "nose": {"num": 0, "detected": False, "x": 0, "y": 0},
        "left_eye": {"num": 1, "detected": False, "x": 0, "y": 0},
        "right_eye": {"num": 2, "detected": False, "x": 0, "y": 0},
        "left_ear": {"num": 3, "detected": False, "x": 0, "y": 0},
        "right_ear": {"num": 4, "detected": False, "x": 0, "y": 0},
        "left_shoulder": {"num": 5, "detected": False, "x": 0, "y": 0},
        "right_shoulder": {"num": 6, "detected": False, "x": 0, "y": 0},
        "left_elbow": {"num": 7, "detected": False, "x": 0, "y": 0},
        "right_elbow": {"num": 8, "detected": False, "x": 0, "y": 0},
        "left_wrist": {"num": 9, "detected": False, "x": 0, "y": 0},
        "right_wrist": {"num": 10, "detected": False, "x": 0, "y": 0},
        "left_hip": {"num": 11, "detected": False, "x": 0, "y": 0},
        "right_hip": {"num": 12, "detected": False, "x": 0, "y": 0},
        "left_knee": {"num": 13, "detected": False, "x": 0, "y": 0},
        "right_knee": {"num": 14, "detected": False, "x": 0, "y": 0},
        "left_ankle": {"num": 15, "detected": False, "x": 0, "y": 0},
        "right_ankle": {"num": 16, "detected": False, "x": 0, "y": 0},
    }
    person_detected = False
    horizont_point = 0.84
    head_point = 0.1
    laying_dow = False
    sitting = False
    pre_left_ankle = 0
    pre_rigth_ankle = 0

def dictionary_body_parts():
    global dicc_body_parts, person_detected
    person_detected = False
    for clave, valor in dicc_body_parts.items():
        lista = get_keypoint_position(dicc_body_parts[clave]["num"])
        dicc_body_parts[clave]["detected"] = lista[0]
        dicc_body_parts[clave]["x"] = lista[1]
        dicc_body_parts[clave]["y"] = lista[2]
        if lista[0]:
            person_detected = True

# def detection_especial_object(object_to_detect):
#     # Get the classes of detected objects
#     detected_objects = results_objects[0].boxes.cls
#     # Check if the object is detected
#     return object_to_detect in detected_objects

def get_keypoint_position(keypoint_num=0, dic=True, axis='y'):
    global results_pose
    """ 
    Keypoint reference:
        0: nose          5: left_shoulder  10: right_wrist    15: left_ankle
        1: left_eye      6: right_shoulder 11: left_hip       16: right_ankle
        2: right_eye     7: left_elbow     12: right_hip
        3: left_ear		 8: right_elbow    13: left_knee
        4: right_ear	 9: left_wrist     14: right_knee
    """
    if not 0 <= keypoint_num <= 16:
        raise ValueError("Keypoint number must be between 0 and 16")
    if axis.lower() not in ['x', 'y']:
        raise ValueError("Axis must be 'x' or 'y'")

    if not results_pose or len(results_pose[0].keypoints.xyn) == 0 or len(results_pose[0].keypoints.xyn[0]) == 0:
        return False, 0, 0
    
    # Get the keypoint data
    keypoint = results_pose[0].keypoints.xyn[0][keypoint_num]

    # confirm if it's detected
    detected = True
    if keypoint[1].item() == 0:
        detected = False
    
    if dic:
        return detected, keypoint[0].item(),  keypoint[1].item()
    # Return x or y coordinate based on axis parameter
    return [keypoint[0].item(), detected] if axis.lower() == 'x' else [keypoint[1].item(), detected]

def point_detection():
    print("point detection **********")
    global pre_left_ankle, pre_rigth_ankle
    # El robot siempre verá el suelo a un punto fijo. Lo primero que el robot podrá ver serán los pies de una persona y cuanto más se aleje,
    # podrá ir viendo mejor el cuerpo completo de la persona.
    found_person = True
    if not person_detected:
        # MOVER EL ROBOT
        found_person = searching_person()
    if found_person:
        if not face_detection():
            print("Not face detection ******")
            # if feet_detection():
            #     # si una persona se agacha a recoger algo de valdas inferiores, o incluso del suelo, es posible que no se pueda reconocer la cara, pero estará en el mismo sitio (los pies) que el momento en que estaba estirado
            #     fall_check() 
            # else:
            #     print("****** move ****")
                # si los pies (tobillos) no están en el mismo sitio con un 10% de error es que la persona se ha movido del sitio y es posible que se haya acercado al robot y por eso, éste no puede detectar su cara
                # MOVER EL ROBOT
            move_robot_back()
        else: # si el robot detecta la cara de la persona es porque está lo suficiente lejos para poder verlo o se ha caido
            print("Face detection ******")
            if not distance_detection():
                pre_left_ankle = 0
                pre_rigth_ankle = 0
                if dicc_body_parts["left_ankle"]["detected"]:
                    pre_left_ankle = dicc_body_parts["left_ankle"]["x"]
                if dicc_body_parts["right_ankle"]["detected"]:
                    pre_rigth_ankle = dicc_body_parts["right_ankle"]["x"]
                fall_check()
            else:
                move_robot_front()
    
def face_detection():
    return dicc_body_parts["nose"]["detected"] or dicc_body_parts["left_ear"]["detected"] or dicc_body_parts["right_ear"]["detected"] or dicc_body_parts["left_eye"]["detected"] or dicc_body_parts["right_eye"]["detected"]

def feet_detection():
    return dicc_body_parts["left_ankle"]["detected"] and dicc_body_parts["right_ankle"]["detected"] and ((pre_left_ankle + pre_rigth_ankle) / 2 < ((dicc_body_parts["right_ankle"]["x"] + dicc_body_parts["left_ankle"]["x"]) / 2) * 1.01 or (pre_left_ankle + pre_rigth_ankle) / 2 > ((dicc_body_parts["right_ankle"]["x"] + dicc_body_parts["left_ankle"]["x"]) / 2) * 0.99)

def distance_detection():
    return dicc_body_parts["left_eye"]["y"] > head_point or dicc_body_parts["right_eye"]["y"] > head_point or dicc_body_parts["left_ear"]["y"] > head_point or dicc_body_parts["right_ear"]["y"] > head_point or dicc_body_parts["nose"]["y"] > head_point

def searching_person():
    print("Searching person -----------")
    # Dar vuelta 360º detectando persona
    rMove.spin()
    init_time = time.time()
    while init_time + 25 < time.time():
        if take_the_frame():
            dictionary_body_parts()
            if person_detected:
                rMove.stop()
                return True
    rMove.stop()
    return False

def move_robot_back(motive="points"):
    print("*** Move the robot ***")
    # Move the robot back because the person is too much near the robot
    # If there is obstacles -- > 
    if not obstacles_back():
        rMove.go_back()
        # TODO
        while not face_detection(): #or not obstacles_back():
            if take_the_frame():
                dictionary_body_parts()
        rMove.stop()
        if not obstacles_back():
            fall_check()   
            return    
    
    while obstacles_left:
        rMove.turn_left()
        rMove.go_back()
        #wait(5s)
        rMove.stop()
    while obstacles_rigth:
        rMove.turn_rigth()
        rMove.go_back()
        #wait(5s)
        rMove.stop()

def move_robot_front(motive="points"):
    print("*** Move the robot to you ***")
    # Move the robot front because the person is too much far away the robot
    # If there is obstacles -- > 
    if not obstacles_front():
        rMove.go_front()
        # TODO
        while face_detection() and distance_detection(): #and not obstacles_front():
            if take_the_frame():
                dictionary_body_parts()
        rMove.stop()
        if not obstacles_front():
            fall_check()   
            return    
    
    while obstacles_left:
        rMove.turn_rigth()
        rMove.go_front()
        #wait(5s)
        rMove.stop()
    while obstacles_rigth:
        rMove.turn_left()
        rMove.go_front()
        #wait(5s)
        rMove.stop()

def obstacles_left():
    return False

def obstacles_rigth():
    return False

def obstacles_back():
    return False

def obstacles_front():
    return False

def fall_check():
    print("********* Fall_check")
    global cv2, fall_down, count_down
    text = "PERSONA CAIDA"
    if not fall_down:
        # Coger cadera más baja
        print("*** not fall down")
        fall_down = fall_detected()
    else:
        print("*** Fall down")
        if count_down <= 1000:
            if (person_detected and fall_detected()) or not person_detected:
                cv2.putText(annotated_frame, "PELIGROOOO", (90, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
                cv2.putText(annotated_frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
                cv2.imshow("Camera", annotated_frame)
                buzzer_sound()
                count_down +=1
            else:
               fall_down = False 
               count_down = 0
            
    if fall_down:
        buzzer_sound()

def fall_detected():
    hip_y = dicc_body_parts["left_hip"]['y']
    if dicc_body_parts["left_hip"]['y'] > dicc_body_parts["right_hip"]['y']:
        hip_y = dicc_body_parts["right_hip"]['y']
    # Calcular distancia con punto_suelo
    if hip_y > (horizont_point - 0.1 * horizont_point):
        return True
    # Coger hombros más baja
    shoulder_y = dicc_body_parts["left_shoulder"]['y']
    if dicc_body_parts["left_shoulder"]['y'] > dicc_body_parts["right_shoulder"]['y']:
        shoulder_y = dicc_body_parts["right_shoulder"]['y']
    # Calcular distancia con punto_suelo
    if shoulder_y > (horizont_point - 0.1 * horizont_point):
        return True
    return False

def buzzer_sound():
    print("----- Buzzer sound")
    global buzzer
    if buzzer:
        # GPIO.output(BUZZER_PIN, GPIO.HIGH)
        buzzer = False
        print("buzzer = False")
    else:
        # GPIO.output(BUZZER_PIN, GPIO.LOW)
        buzzer = True
        print("buzzer = True")

def print_in_frame(results):
    global cv2, annotated_frame, text_size, font, text_x, text_y
    # Output the visual detection data, we will draw this on our camera preview window
    annotated_frame = results[0].plot()
    # Get inference time
    inference_time = results[0].speed['inference']
    fps = 1000 / inference_time  # Convert to milliseconds
    text = f'FPS: {fps:.1f}'

    # Define font and position
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 1, 2)[0]
    text_x = annotated_frame.shape[1] - text_size[0] - 10  # 10 pixels from the right
    text_y = text_size[1] + 10  # 10 pixels from the top

    # Draw the text on the annotated frame
    cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Display the resulting frame
    cv2.imshow("Camera", annotated_frame)

def take_the_frame():
    global results_pose
    frame = picam2.capture_array()
    if frame is None:
        return False

    # Run YOLO model on the captured frame and store the results
    # results_objects = model_objects(frame, imgsz = 160)
    results_pose = model_pose(frame, imgsz = 160)
    #print_in_frame(results_objects)
    print_in_frame(results_pose)

    return True

def main():
    global results_objects, results_pose, frame, cv2
    init_variables()

    while True:
        # Capture a frame from the camera
        if take_the_frame():
            # Get points
            dictionary_body_parts()
            if not fall_down:
                point_detection()
            else:
                fall_check()
        time.sleep(1)
        # Exit the program if q is pressed
        if cv2.waitKey(1) == ord("q"):
            break

    # Close all windows
    cv2.destroyAllWindows()

# ---------------------------------------
#if __name__ == "__main__":
main()



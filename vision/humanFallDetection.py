# Imports
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
import time

# Set up the camera with Picam
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 1280)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Load YOLOv8
model_objects = YOLO("yolov8n.pt")
model_pose  = YOLO("yolo11n-pose.pt")

def init_variables():
    # Variables
    global flag, init_time, dicc_body_parts, person_detected
    flag = True # primera vez que se activa el aviso de mover el robot
    init_time = 0
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


# ---------------------------------------
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

def detection_especial_object(object_to_detect):
    # Get the classes of detected objects
    detected_objects = results_objects[0].boxes.cls
    # Check if the object is detected
    return object_to_detect in detected_objects


def get_keypoint_position(keypoint_num=0, dic=True, axis='y'):
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

    if not results_pose or len(results_pose[0].keypoints.xyn) == 0:
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
    if not person_detected:
        # MOVER EL ROBOT
        move_robot()
    else:
        if not dicc_body_parts["nose"]["detected"]:
            # MOVER EL ROBOT
            move_robot()      
        else:
            if not dicc_body_parts["left_ankle"]["detected"]:
                # MOVER EL ROBOT
                move_robot()
            else:
                if not dicc_body_parts["right_ankle"]["detected"]:
                    # MOVER EL ROBOT
                    move_robot()
                else:
                    fall_check()
                

def move_robot():
    global flag, init_time, cv2
    if flag:
        init_time = time.time()
        flag = not flag
        cv2.putText(annotated_frame, "MUEVE LA CÁMARA", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
    else:
        now_time = abs(init_time - time.time())
        if now_time >= 10:
            flag = not flag
            # TODO
            fall_check()
        else:
            cv2.putText(annotated_frame, "MUEVE LA CÁMARA", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
            
    cv2.imshow("Camera", annotated_frame)

def fall_check():
    global cv2
    '''
    opcion 1:
        tumbada

    opcion 2:
        sentada

    '''
    mid_hip = abs(dicc_body_parts["left_hip"]['x'] - dicc_body_parts["right_hip"]['x']) / 2
    mid_ankle = abs(dicc_body_parts["left_ankle"]['x'] - dicc_body_parts["right_ankle"]['x']) / 2

    laying_dow = False
    sitting = False
    cv2.putText(annotated_frame, "BIENNN", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
    cv2.imshow("Camera", annotated_frame)

def main():
    global results_objects, results_pose, frame, cv2
    init_variables()

    while True:
        # Capture a frame from the camera
        frame = picam2.capture_array()

        if frame is None:
            print("Error: No se capturó un frame.")

        # Run YOLO model on the captured frame and store the results
        results_objects = model_objects(frame, imgsz = 160)
        results_pose = model_pose(frame, imgsz = 160)
        print_in_frame(results_objects)
        print_in_frame(results_pose)

        # Get points
        dictionary_body_parts()
        point_detection()

        # Exit the program if q is pressed
        if cv2.waitKey(1) == ord("q"):
            break

    # Close all windows
    cv2.destroyAllWindows()

# ---------------------------------------
if __name__ == "__main__":
    main()
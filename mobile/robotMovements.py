from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

def go_back():
    print("Atras...")
    kit.continuous_servo[0].throttle = 1.0
    kit.continuous_servo[1].throttle = -1.0

def go_front():
    print("Adelante...")
    kit.continuous_servo[0].throttle = -1.0
    kit.continuous_servo[1].throttle = 1.0

def stop():
    print("Parar...")
    kit.continuous_servo[0].throttle = 0.0
    kit.continuous_servo[1].throttle = 0.0

def spin():
    print("spin...")
    kit.continuous_servo[0].throttle = 0.8
    kit.continuous_servo[1].throttle = 0.8

def turn_rigth():
    kit.servo[2].angle = 45

def turn_left():
    kit.servo[2].angle = -45

def turn_straight():
    kit.servo[2].angle = 0



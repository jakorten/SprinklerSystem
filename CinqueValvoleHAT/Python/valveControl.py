import Adafruit_PCA9685
from enum import Enum     # for enum34, or the stdlib version
import pigpio
import time
import sys
import os
from threading import Timer,Thread,Event

deviceAddress = 0x60
enableDebugPrints = False

'''

J.A. Korten June 2019
V1.0 Controller for 5x Tap Valve (DC Motor) Controller

For TapController 12V v1.0:

+------------+------------+------------+------------+------------+
| Motor 1    | Motor 2    | Motor 3    | Motor 4    | Motor 5    |
+------------+------------+------------+------------+------------+
| PWM0 IN1.1 | PWM2 IN2.1 | PWM8 IN3.1 | PWM4 IN4.1 | PWM6 IN4.1 |
| PWM1 IN1.2 | PWM3 IN2.2 | PWM9 IN3.2 | PWM5 IN4.2 | PWM7 IN5.2 |
+------------+------------+------------+------------+------------+

For TapController 12V v1.1+:

+------------+------------+------------+------------+------------+
| Motor 1    | Motor 2    | Motor 3    | Motor 4    | Motor 5    |
+------------+------------+------------+------------+------------+
| PWM0 IN1.1 | PWM2 IN2.1 | PWM4 IN3.1 | PWM6 IN4.1 | PWM8 IN4.1 |
| PWM1 IN1.2 | PWM3 IN2.2 | PWM5 IN3.2 | PWM7 IN4.2 | PWM9 IN5.2 |
+------------+------------+------------+------------+------------+

https://www.tutorialspoint.com/python3/python_multithreading.htm

   Uses DRV8871 (Max 3.6A, limited at 2A)
   Theoretical Voltage limit 50V=.
   Board was intended for 5-12V

   Truth table for DRV8871:
   +------+------+-------+-------+----------+
   | IN 1 | IN 2 | OUT 1 | OUT 2 |          |
   +------+------+-------+-------+----------+
   |   0  |   0  | SLEEP | SLEEP | Disabled |
   |   0  |   1  | LOW   | HIGH  | Reverse  |
   |   1  |   0  | HIGH  | HIGH  | Forward  |
   |   1  |   1  | LOW   | LOW   | Brake    |
   +------+------+-------+-------+----------+


'''

class tapState(Enum):
    open = 1
    closed = 0

tapDelay = 15.0

def debugPrint(message):
    if (enableDebugPrints):
        print(message)

class motorTimer():

   def __init__(self,t,hFunction,name):
      self.t=t
      self.hFunction = hFunction
      self._name = str(name)
      debugPrint("Thread " + name + " initialized...")
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      debugPrint("Thread " + self._name + " function called...")
      self.thread = Timer(self.t,self.handle_function)
      self.thread.cancel()

   def start(self):
      debugPrint("Thread " + self._name + " started...")
      self.thread.start()

   def cancel(self):
      debugPrint("Thread " + self._name + " cancelled...")
      self.thread.cancel()

class DRV8871_Valve:
    # expects a kit# / motor#
    pwmPins_1_1 = [0, 2, 4, 6, 8] # for V1.1+
    pwmPins = [0, 2, 8, 4, 6]     # strange but is due to HAT v1.0 configuration...
    # Function with the timer

    def motorTimeout(self):
        debugPrint("Timeout issued (motorStop)")
        debugPrint("Delay: " + str(self._delay))
        self._mT = motorTimer(self._delay, self.motorStop, str(self._motor))
        self._mT.start()
        #self.motorStop()
        #self._motorTimeout.cancel()

    def __init__(self, motor, delay, state, version=1.0):
         if (version > 1.0):
             pwmPins = pwmPins_1_1
         self._motor = motor
         self._delay = delay
         self._state = state
         self._default_state = state
         self._pwm_controller = Adafruit_PCA9685.PCA9685(address=deviceAddress, busnum=1)

    def open(self):
        debugPrint(str(self))
        if (self._state == tapState.closed):
            self._motor.throttle = 1.0
            sleep(self._delay)
            self._state = tapState.open
            self._motor.throttle = 0

    def close(self):
        debugPrint(str(self))
        if (self._state == tapState.open):
            self._motor.throttle = -1.0
            sleep(self._delay)
            self._state = tapState.closed
            self._motor.throttle = 0

    def isClosed(self):
        return self._state == tapState.closed

    def isOpen(self):
        return self._state == tapState.open

    def release(self):
        self.release()

    def motorForward(self):
        in1 = 1
        in2 = 0
        self.sendCommand(in1, in2)

    def motorBackward(self):
        in1 = 0
        in2 = 1
        self.sendCommand(in1, in2)

    def motorBrake(self):
        in1 = 1
        in2 = 1
        self.sendCommand(in1, in2)

    def motorStop(self):
        in1 = 0
        in2 = 0
        self.sendCommand(in1, in2)
        debugPrint("Motorstop issued (" + str(self._motor) + ")")

    def setStateTimer(self, toState):
        try:
            self._mT.cancel() # just in case...
        except:
            # do nothing
            enableDebugPrints("Error: Timer exception")
        if (toState == self._default_state):
            self.motorBackward()
        else:
            self.motorForward()
        try:
            self.motorTimeout()
        except:
            debugPrint("Timeout issue...")

    def sendCommand(self, in1, in2):
        debugPrint("Send command...")
        # pwm frequency?!
        _pins0 = self.pwmPins[self._motor]   # get pwmPins + 0
        _pins1 = self.pwmPins[self._motor]+1 # get pwmPins + 1
        PCA9685_PWM_FULL = 0x1000
        if (in1 == 1):
            self._pwm_controller.set_pwm(_pins0, PCA9685_PWM_FULL, 0)
        else:
            self._pwm_controller.set_pwm(_pins0, 0, 0)
        if (in2 == 1):
            self._pwm_controller.set_pwm(_pins1, PCA9685_PWM_FULL, 0)
        else:
            self._pwm_controller.set_pwm(_pins1, 0, 0)

    def inRange(self, value, min, max):
        return (value >= min) and (value <= max)

class tapHatCinqController():
    def __init__(self):
        if (self.findPCA9685):
            self._error = False
            print("PCA9685 was found")
        else:
            self._error = True
            print("Error: Could not find PCA9685")
            return

        # DRV8871_Valve number, timeout delay, default state
        self.motor1 = DRV8871_Valve(0, 15.0, tapState.open)
        self.motor2 = DRV8871_Valve(1, 15.0, tapState.open)
        self.motor3 = DRV8871_Valve(2, 15.0, tapState.open)
        self.motor4 = DRV8871_Valve(3, 15.0, tapState.open)
        self.motor5 = DRV8871_Valve(4, 15.0, tapState.open)

    def stopMotors(self):
        self.motor1.motorStop()
        self.motor2.motorStop()
        self.motor3.motorStop()
        self.motor4.motorStop()
        self.motor5.motorStop()
        debugPrint("Motor stops issued: SUCCESS.")

    def setValve(self, tap, state):
        debugPrint("setValve: " + str(tap) + " to " + str(state) + ".")
        toState = tapState.closed
        if (state == 1):
            toState = tapState.open
        if (tap == 0):
            self.motor1.setStateTimer(toState)
        if (tap == 1):
            self.motor2.setStateTimer(toState)
        if (tap == 2):
            self.motor3.setStateTimer(toState)
        if (tap == 3):
            self.motor4.setStateTimer(toState)
        if (tap == 4):
            self.motor5.setStateTimer(toState)


    def findPCA9685(self):
        pi = pigpio.pi() # connect to local Pi
        for device in range(128):
              h = pi.i2c_open(1, device)
              try:
                 pi.i2c_read_byte(h)
                 if (inRange(device, 0x60, 0x70)):
                     #print("Possible PCA9685 found at: " + str(hex(device)))
                     deviceAddress = hex(device)
                     return True
                     pi.stop # disconnect from Pi
                 else:
                     #print("Other device found at: " + hex(device))
                     enableDebugPrints("Warning: Found some i2c device outside expected range...")
              except: # exception if i2c_read_byte fails
                 pass
              pi.i2c_close(h)
        pi.stop # disconnect from Pi
        return False

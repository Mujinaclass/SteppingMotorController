import pigpio
import time

#GPIO27: STEP command
#GPIO17: Direction CW:HIGH  CCW:LOW
#GPIO22: Sleep mode
# Microstep Resolution  |   M0   |  M1
#         Full          |  LOW   | HIGH
#         Half          |  HIGH  | LOW
#         1/4           |Floating| LOW
#         1/8           |  LOW   | HIGH
#         1/16          |  HIGH  | HIGH
#         1/32          |Floating| HIGH
# *Leaving selection pins disconnected results "Floating".
#  Motor full step angle: 1.8 deg./step

MOTOR_STEP_PIN = 27
MOTOR_DIR_PIN = 17
MOTOR_SLEEP_PIN = 22
MOTOR_M0_PIN = 24
MOTOR_M1_PIN = 23
MOTOR_STEP_ANGLE = 1.8
MOTOR_PULSEDURATION_LIMIT = 1.9e-6 #[sec]
MOTOR_STEPRESMODES_DICT = {1: (0,0), 2: (1,0), 4: (0,0), 8: (0,1), 16: (1,1), 32: (0,1)} # Resolution: (M0 pin, M1 pin)

SCREW_LEAD = 1.0

AVAIRABLE_PWM_FREQ = { 1: (50,100,200,250,400,500,800,1000,1250,1600,2000,2500,4000,5000,8000,10000,20000,40000), # Sample rate [us]: (Hertz)
                       2: (25, 50,100,125,200,250,400, 500, 625, 800,1000,1250,2000,2500,4000, 5000,10000,20000), # Default is 5[us].
                       4: (13, 25, 50, 63,100,125,200, 250, 313, 400, 500, 625,1000,1250,2000, 2500, 5000,10000),
                       5: (10, 20, 40, 50, 80,100,160, 200, 250, 320, 400, 500, 800,1000,1600, 2000, 4000, 8000),
                       8: ( 6, 13, 25, 31, 50, 63,100, 125, 156, 200, 250, 313, 500, 625,1000, 1250, 2500, 5000),
                      10: ( 5, 10, 20, 25, 40, 50, 80, 100, 125, 160, 200, 250, 400, 500, 800, 1000, 2000, 4000)}
# Stepping Motor limit is 2500Hz???

PWM_dutycycle = (0, 128) # PWM (STOP, 1/2 on)
PWM_sample_rate = 8  # [us]
motor_step_resolution = 2

def motorSettings(stepResolution):
    global pi, motor_step_resolution
    pi = pigpio.pi()
    pi.set_mode(MOTOR_STEP_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_DIR_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_SLEEP_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_M0_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_M1_PIN,pigpio.OUTPUT)

    pi.set_PWM_frequency(MOTOR_STEP_PIN, AVAIRABLE_PWM_FREQ[PWM_sample_rate][16])
    pi.set_PWM_dutycycle(MOTOR_STEP_PIN, PWM_dutycycle[0])
    pi.write(MOTOR_SLEEP_PIN,1)
    time.sleep(1e-3)               #Wake-up time. Need to set over 1msec

    if stepResolution in MOTOR_STEPRESMODES_DICT:
        pi.write(MOTOR_M0_PIN,MOTOR_STEPRESMODES_DICT[stepResolution][0])
        pi.write(MOTOR_M1_PIN,MOTOR_STEPRESMODES_DICT[stepResolution][1])
    else:
        motor_step_resolution = 1        # Set step resolution to Full-step mode
        pi.write(MOTOR_M0_PIN,0)
        pi.write(MOTOR_M1_PIN,0)
        print("Invalid value. Step resolution should be within the following values.")
        print("Full > 1, Half > 2, 1/4 > 4, 1/8 > 8, 1/16 > 16, 1/32 > 32")
        print("Step resolution is now Full-step (default).")

    if stepResolution == 4 or stepResolution == 32:
        print("Please disconnect M0 pin: GPIO" '%d' %MOTOR_M0_PIN)
#end def motorSettings()

def moveMotor(direc,vel,durat):      # direc = 0 (CCW) or 1 (CW), velocity [mm/sec], duration [sec]
    pi.write(MOTOR_DIR_PIN,direc)
    pi.set_PWM_dutycycle(MOTOR_STEP_PIN, PWM_dutycycle[1])  # PWM on
    time.sleep(durat)
    pi.set_PWM_dutycycle(MOTOR_STEP_PIN, PWM_dutycycle[0])  # PWM off   
    

motorSettings(motor_step_resolution)
moveMotor(1,20,1)  #limit vel = 25? 20000Hz 50: 40000Hz

pi.write(MOTOR_SLEEP_PIN,0)

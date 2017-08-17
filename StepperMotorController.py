import pigpio
import time

# Microstep Resolution  |   M0   |  M1
#         Full          |  LOW   | HIGH
#         Half          |  HIGH  | LOW
#         1/4           |Floating| LOW
#         1/8           |  LOW   | HIGH
#         1/16          |  HIGH  | HIGH
#         1/32          |Floating| HIGH
# *Leaving selection pins disconnected results "Floating".

MOTOR_STEP_PIN = 27                # GPIO27: STEP command
MOTOR_DIR_PIN = 17                 # GPIO17: Direction CW:HIGH  CCW:LOW
MOTOR_SLEEP_PIN = 22               # GPIO22: Sleep mode
MOTOR_M0_PIN = 24
MOTOR_M1_PIN = 23
MOTOR_STEP_ANGLE = 1.8             # Motor full step angle: 1.8 deg./step
MOTOR_SPEED_LIMIT = 5              # [rps] Stepping Motor limit is 5 rps.
MOTOR_STEPRESMODES_DICT = {1: (0,0), 2: (1,0), 4: (0,0), 8: (0,1), 16: (1,1), 32: (0,1)} # Resolution: (M0 pin, M1 pin)

SCREW_STANDARD = 'M4'
SCREW_LEAD = 0.7                   # [mm] Lead = pitch

SYRINGE_AREA = 165.13              # [mm^2]

AVAIRABLE_PWM_FREQ_DICT = { 1: (50,100,200,250,400,500,800,1000,1250,1600,2000,2500,4000,5000,8000,10000,20000,40000), # Sample rate [us]: (Hertz)
                            2: (25, 50,100,125,200,250,400, 500, 625, 800,1000,1250,2000,2500,4000, 5000,10000,20000),
                            4: (13, 25, 50, 63,100,125,200, 250, 313, 400, 500, 625,1000,1250,2000, 2500, 5000,10000),
                            5: (10, 20, 40, 50, 80,100,160, 200, 250, 320, 400, 500, 800,1000,1600, 2000, 4000, 8000),
                            8: ( 6, 13, 25, 31, 50, 63,100, 125, 156, 200, 250, 313, 500, 625,1000, 1250, 2500, 5000),
                           10: ( 5, 10, 20, 25, 40, 50, 80, 100, 125, 160, 200, 250, 400, 500, 800, 1000, 2000, 4000)}

PWM_DUTYCYCLE = (0, 128)           # PWM (STOP, 1/2 on)
PWM_SAMPLE_RATE = 5                # Default is 5 us. If you want to change sample rate, type "sudo pigpiod -s <sample rate>" in comand line, when you start the pigpio deamon. 

motor_step_resolution = 1
motor_direction = 1                # direcion = 0 (CCW) or 1 (CW)
motor_moving_dulation = 1          # [sec]

AVAIRABLE_FLOW_RATE_DICT = {}      # {Flow rate [ml/s]: PWM frequency [Hz]}
for freq in range(len(AVAIRABLE_PWM_FREQ_DICT[PWM_SAMPLE_RATE])):
    RPM = (MOTOR_STEP_ANGLE / motor_step_resolution * AVAIRABLE_PWM_FREQ_DICT[PWM_SAMPLE_RATE][freq]) / 360  # [rotation / sec]
    flow_rate = RPM * 0.7 * SYRINGE_AREA * 10**-3 # [ml / sec]
    if RPM <= MOTOR_SPEED_LIMIT:
        AVAIRABLE_FLOW_RATE_DICT[flow_rate] = AVAIRABLE_PWM_FREQ_DICT[PWM_SAMPLE_RATE][freq]
    else:
        thing = None               # do nothing


def motorSettings(stepResolution):
    global pi, motor_step_resolution
    pi = pigpio.pi()
    pi.set_mode(MOTOR_STEP_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_DIR_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_SLEEP_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_M0_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_M1_PIN,pigpio.OUTPUT)

    pi.write(MOTOR_SLEEP_PIN,1)
    time.sleep(1e-3)               # Wake-up time. Need to set over 1msec

    if stepResolution in MOTOR_STEPRESMODES_DICT:
        pi.write(MOTOR_M0_PIN,MOTOR_STEPRESMODES_DICT[stepResolution][0])
        pi.write(MOTOR_M1_PIN,MOTOR_STEPRESMODES_DICT[stepResolution][1])
    else:
        motor_step_resolution = 1  # Set step resolution to Full-step mode
        pi.write(MOTOR_M0_PIN,0)
        pi.write(MOTOR_M1_PIN,0)
        print("Invalid value. Step resolution should be within the following values.")
        print("Full > 1, Half > 2, 1/4 > 4, 1/8 > 8, 1/16 > 16, 1/32 > 32")
        print("Step resolution is now Full-step (default).")

    if stepResolution == 4 or stepResolution == 32:
        print("Please disconnect M0 pin: GPIO" '%d' %MOTOR_M0_PIN)
#end def motorSettings()

def motorFreqSetting():
    pi.set_PWM_frequency(MOTOR_STEP_PIN, AVAIRABLE_PWM_FREQ_DICT[PWM_SAMPLE_RATE][12])
    pi.set_PWM_dutycycle(MOTOR_STEP_PIN, PWM_DUTYCYCLE[0])
#end def motorFreqSetting()

def moveMotor(direc,durat):
    pi.write(MOTOR_DIR_PIN,direc)
    pi.set_PWM_dutycycle(MOTOR_STEP_PIN, PWM_DUTYCYCLE[1])  # PWM on
    time.sleep(durat)
    pi.set_PWM_dutycycle(MOTOR_STEP_PIN, PWM_DUTYCYCLE[0])  # PWM off   
    

motorSettings(motor_step_resolution)
motorFreqSetting()
moveMotor(motor_direction,motor_moving_dulation)

pi.write(MOTOR_SLEEP_PIN,0)

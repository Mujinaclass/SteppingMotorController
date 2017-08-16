import pigpio
import time

MOTOR_STEP_PIN = 27          #GPIO27: STEP command
MOTOR_DIR_PIN = 17           #GPIO17: Direction CW:HIGH  CCW:LOW
MOTOR_SLEEP_PIN = 22         #GPIO22: Sleep mode
MOTOR_M0_PIN = 24            # Microstep Resolution  |   M0   |  M1
MOTOR_M1_PIN = 23            #         Full          |  LOW   | HIGH
step_resolution = 1          #         Half          |  HIGH  | LOW
MOTOR_STEP_ANGLE = 1.8       #         1/4           |Floating| LOW
MOTOR_PULSEDURATION_LIMIT = 1.9e-6 #[sec]#         1/8           |  LOW   | HIGH
                             #         1/16          |  HIGH  | HIGH
                             #         1/32          |Floating| HIGH
                             # *Leaving selection pins disconnected results "Floating".
                             #  Motor full step angle: 1.8 deg./step
SCREW_LEAD = 1.0

def motorSettings(stepResolution):
    global pi
    pi = pigpio.pi()
    pi.set_mode(MOTOR_STEP_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_DIR_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_SLEEP_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_M0_PIN,pigpio.OUTPUT)
    pi.set_mode(MOTOR_M1_PIN,pigpio.OUTPUT)

    pi.write(MOTOR_SLEEP_PIN,1)
    time.sleep(1e-3)               #Wake-up time. Need to set over 1msec

    if stepResolution == 1:
        pi.write(MOTOR_M0_PIN,0)
        pi.write(MOTOR_M1_PIN,0)
    elif stepResolution == 2:
        pi.write(MOTOR_M0_PIN,1)
        pi.write(MOTOR_M1_PIN,0)
    elif stepResolution == 4:
        pi.write(MOTOR_M0_PIN,0)    # Must be disconnected
        pi.write(MOTOR_M1_PIN,0)
        print("Please disconnect M0 pin: GPIO" '%d' %MOTOR_M0_PIN)
    elif stepResolution == 8:
        pi.write(MOTOR_M0_PIN,0)
        pi.write(MOTOR_M1_PIN,1)
    elif stepResolution == 16:
        pi.write(MOTOR_M0_PIN,1)
        pi.write(MOTOR_M1_PIN,1)
    elif stepResolution == 32:
        pi.write(MOTOR_M0_PIN,0)    # Must be disconnected
        pi.write(MOTOR_M1_PIN,1)
        print("Please disconnect M0 pin: GPIO" '%d' %MOTOR_M0_PIN)
    else:
        pi.write(MOTOR_M0_PIN,0)
        pi.write(MOTOR_M1_PIN,0)
        print("Invalid value. Step resolution should be within the following values.")
        print("Full > 1, Half > 2, 1/4 > 4, 1/8 > 8, 1/16 > 16, 1/32 > 32")
        print("Step resolution is now Full-step (default).")
#end def motorSettings()

def moveMotor(direc,vel,durat):      # direc = 0 (CCW) or 1 (CW), velocity [mm/sec], duration [sec]
    pi.write(MOTOR_DIR_PIN,direc)
    steps = int(round((vel * durat)/SCREW_LEAD * (360 * step_resolution)/MOTOR_STEP_ANGLE)) # ([mm/sec] * [sec])/[mm] * ([deg] * [])/[deg] = Required number of steps
    TimeWidth = (float(durat)/steps) / 2.0    # [sec]
    print(steps)
    print(TimeWidth)
    if TimeWidth > MOTOR_PULSEDURATION_LIMIT:
        for step in range(steps):
            pi.write(MOTOR_STEP_PIN,1)
            time.sleep(TimeWidth)
            pi.write(MOTOR_STEP_PIN,0)
            time.sleep(TimeWidth)
    else:
        print("Error!: Over limitation of acceptable motor pulse dulation.")
        print("Motor pulse dulation must be less than " '%f' %MOTOR_PULSEDURATION_LIMIT)
    
    

motorSettings(step_resolution)
moveMotor(1,1,3)

pi.write(MOTOR_SLEEP_PIN,0)

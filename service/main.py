from time import sleep
from kivy.lib import osc
from datetime import datetime

from kivy.logger import Logger
from os.path import exists
from os import makedirs

from plyer import accelerometer, gyroscope

serviceport = 3000
activityport = 3001
filename = "/storage/sdcard1/quantifyMyself/service.txt"

def some_api_callback(message, *args):
    print("got a message! %s" % message)
    answer_message()

def answer_message():
    osc.sendMsg('/some_api', [asctime(localtime()), ], port=activityport)

def get_gyroscope_activity():
    gyroscope.enable()
    i = 0
    asum = 0.0
    lastx = lasty = lastz = 0
    val = gyroscope.orientation[:3]
    if (not val == (None, None, None)):
        lastx = val[0]
        lasty = val[1]
        lastz = val[2]
        Logger.info("gyro-x: " + str(val[0]) + "  y: " + str(val[1]) + "  z: " + str(val[2]))

    while i < 10:
        i += 1
        val = gyroscope.orientation[:3]
        if (not val == (None, None, None)):
            asum += abs(val[0] - lastx) + abs(val[1] - lasty) + abs(val[2] - lastz)
            Logger.info("gyro-yeah! gyro-values:" + str(datetime.now()) + "; asum: " + str(round(asum,2)) + "; x: " + str(round(val[0],2)) + "  y: " + str(round(val[1],2)) + "  z: " + str(round(val[2],2)))
            lastx = val[0]
            lasty = val[1]
            lastz = val[2]
        else:
            Logger.info("gyro-no gyrosc-values at " + str(datetime.now()) + "; " + str(asum))

        sleep(0.1)
    Logger.info("gyrosum: " + str(asum))

    gyroscope.disable()
    return asum, val

def get_accelerometer_activity():
    accelerometer.enable()
    i = 0
    asum = 0.0
    lastx = lasty = lastz = 0
    val = accelerometer.acceleration[:3]
    if (not val == (None, None, None)):
        lastx = val[0]
        lasty = val[1]
        lastz = val[2]
        Logger.info("x: " + str(val[0]) + "  y: " + str(val[1]) + "  z: " + str(val[2]))

    while i < 10:
        i += 1
        val = accelerometer.acceleration[:3]
        if (not val == (None, None, None)):
            asum += abs(val[0] - lastx) + abs(val[1] - lasty) + abs(val[2] - lastz)
            Logger.info("yeah! accelerometer-values:" + str(datetime.now()) + "; asum: " + str(round(asum,2)) + "; x: " + str(round(val[0],2)) + "  y: " + str(round(val[1],2)) + "  z: " + str(round(val[2],2)))
            lastx = val[0]
            lasty = val[1]
            lastz = val[2]
        else:
            Logger.info("no accelerometer-values at " + str(datetime.now()) + "; " + str(asum))

        sleep(0.1)
    Logger.info("asum: " + str(asum))

    accelerometer.disable()
    return asum, val

if __name__ == '__main__':
    #osc.init()
    #oscid = osc.listen(ipAddr='127.0.0.1', port=serviceport)
    #osc.bind(oscid, some_api_callback, '/some_api')
    i=0
    now = datetime.now()
    sensorpath = "/storage/sdcard1/quantifyMyself/sensor/"
    if not exists(sensorpath):
        makedirs(sensorpath)
    gyroFilename = sensorpath + "gyro-" + now.strftime("%y-%m-%d") + ".txt"
    gyroOut = open(gyroFilename,'a+')
    gyroOut.write("\n\ni;time;gyrodata\n")
    gyroOut.write(str(get_gyroscope_activity()))

    accelFilename = sensorpath+ "accel-" + now.strftime("%y-%m-%d") + ".txt"
    accelOut = open(accelFilename, 'a+')
    accelOut.write("\n\nx first line... test...")
    accelOut.write("\nx first measurementx: " + str(get_accelerometer_activity()))
    Logger.info(str(get_accelerometer_activity()))

    gyroOut.flush()
    accelOut.flush()

    while True:
        i += 1
        #osc.readQueue(oscid)
        sleep(60.0)
        now = datetime.now()
        asum, vals = get_accelerometer_activity()
        Logger.info(" accel:  " + str(i) + "; " +  now.strftime("%Y-%m-%d %H:%M:%S") + ";  " + str(round(asum,2)) + ";  " + str(vals))
        accelOut.write("\n " + str(i) + "; " + now.strftime("%Y-%m-%d %H:%M:%S") + " ;  " + str(round(asum,2)) + " ;")
        Logger.info("after output ")
        gyrosum,vals = get_gyroscope_activity()
        Logger.info(" " + str(i) + "; " +  now.strftime("%Y-%m-%d %H:%M:%S") + ";  " + str(round(gyrosum,2)) + ";  " + str(vals))
        gyroOut.write("\n " + str(i) + "; " +  now.strftime("%Y-%m-%d %H:%M:%S") + " ;  " + str(round(gyrosum,2)) + ";  ")
        #output.write("\n-" + str(i) + "; " + str(now))
        if i % 3 == 0:
            accelOut.flush()
            gyroOut.flush()

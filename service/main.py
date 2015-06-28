from time import sleep
from kivy.lib import osc
from datetime import datetime

from kivy.logger import Logger

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
    sleep(0.2)
    i = 0
    asum = 0.0
    lastx = lasty = lastz = 0
    val = gyroscope.orientation[:3]
    if (not val == (None, None, None)):
        lastx = val[0]
        lasty = val[1]
        lastz = val[2]
        Logger.info("gyro-x: " + str(val[0]) + "  y: " + str(val[1]) + "  z: " + str(val[2]))

    while i < 5:
        val = gyroscope.orientation[:3]
        if (not val == (None, None, None)):
            asum += abs(val[0] - lastx) + abs(val[1] - lasty) + abs(val[2] - lastz)
            Logger.info("gyro-yeah! gyro-values:" + str(datetime.now()) + "; asum: " + str(round(asum,2)) + "; x: " + str(round(val[0],2)) + "  y: " + str(round(val[1],2)) + "  z: " + str(round(val[2],2)))
            lastx = val[0]
            lasty = val[1]
            lastz = val[2]
            i += 1
        else:
            Logger.info("gyro-no gyrosc-values at " + str(datetime.now()) + "; " + str(asum))

        sleep(0.1)
    Logger.info("gyrosum: " + str(round(asum,3)))

    gyroscope.disable()
    return asum, val

def get_accelerometer_activity():
    accelerometer.enable()
    i = 0
    asum = 0.0
    lastx = lasty = lastz = 0
    sleep(0.2)
    val = accelerometer.acceleration[:3]
    if (not val == (None, None, None)):
        lastx = val[0]
        lasty = val[1]
        lastz = val[2]
        Logger.info("x: " + str(val[0]) + "  y: " + str(val[1]) + "  z: " + str(val[2]))

    while i < 5:
        val = accelerometer.acceleration[:3]
        if (not val == (None, None, None)):
            asum += abs(val[0] - lastx) + abs(val[1] - lasty) + abs(val[2] - lastz)
            Logger.info("y-ac: " + str(datetime.now()) + "; asum: " + str(round(asum, 2)) + "; x: " + str(round(val[0], 2)) + "  y: " + str(round(val[1], 2)) + "  z: " + str(round(val[2], 2)))
            lastx = val[0]
            lasty = val[1]
            lastz = val[2]
            i += 1
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
    output = open(filename, 'a')
    output.write("\n\nfirst line... test...")
    output.write("\n first measurement: " + str(get_accelerometer_activity()))
    output.close()
    Logger.info(str(get_accelerometer_activity()))
    output2 = open(filename, 'a')

    gyroOut = open("gyro" + str(datetime.now().date) + ".txt")
    gyroOut.write("\n\ngyrotest....\n")
    gyroOut.write(str(get_gyroscope_activity()))

    while True:
        i += 1
        #osc.readQueue(oscid)
        sleep(60.0)
        now = datetime.now()
        asum, vals = get_accelerometer_activity()
        Logger.info("before output..." )
        Logger.info(str(vals))
        Logger.info("  " + str(i) + "; " + str(now) + ";  " + str(asum) + ";  " + str(vals))
        output2.write("\n " + str(i) + "; " + str(now) + ";  " + str(round(asum,2))) # + ";  " + str(vals))
        Logger.info("after output ")
        gyrosum,vals = gyroOut()
        Logger.info(" " + str(i) + "; " + str(now) + ";  " + str(gyrosum) + ";  " + str(vals))
        gyroOut.write("\n " + str(i) + "; " + str(now) + ";  " + str(round(gyrosum,2)) + ";  ") # + str(vals))
        #output.write("\n-" + str(i) + "; " + str(now))
        if i % 3 == 0:
            output2.flush()
            gyroOut.flush()

from time import sleep
from kivy.lib import osc
from datetime import datetime

from kivy.logger import Logger

from plyer import accelerometer

serviceport = 3000
activityport = 3001
filename = "/storage/sdcard1/quantifyMyself/service.txt"

def some_api_callback(message, *args):
    print("got a message! %s" % message)
    answer_message()

def answer_message():
    osc.sendMsg('/some_api', [asctime(localtime()), ], port=activityport)

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

            lastx = val[0]
            lasty = val[1]
            lastz = val[2]
        else:
            Logger.info("no accelerometer-values " + str(asum) + "; x: " + str(val[0]) + "  y: " + str(val[1]) + "  z: " + str(val[2]))
        sleep(0.1)
    Logger.info("asum: " + str(asum))

    accelerometer.disable()
    return asum

if __name__ == '__main__':
    #osc.init()
    #oscid = osc.listen(ipAddr='127.0.0.1', port=serviceport)
    #osc.bind(oscid, some_api_callback, '/some_api')
    i=0
    output = open(filename, 'a')
    output.write("first line... test...")
    output.close()
    Logger.info(str(get_accelerometer_activity()))
    output = open(filename, 'a')

    while True:
        i += 1
        #osc.readQueue(oscid)
        sleep(300.0)
        now = datetime.now()
        asum = get_accelerometer_activity()
        output.write("\n" + str(asum))
        #Logger.info("5s-" + str(now))
        output.write("\n-" + str(i) + "; " + str(now))
        if i % 3 == 0:

            output.close()
            output = open(filename, 'a')

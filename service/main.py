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
    i = 0
    asum = 0.0

    val = accelerometer.acceleration[:3]
    if (not val == (None, None, None)):
        lastx = val[0]
        lasty = val[1]
        lastz = val[2]

    while i < 10:
        i += 1
        val = accelerometer.acceleration[:3]
        if (not val == (None, None, None)):
            asum += abs(val[0] - lastx) + abs(val[1] - lasty) + abs(val[2] - lastz)

            lastx = val[0]
            lasty = val[1]
            lastz = val[2]
        else:
            Logger.info("no accelerometer-values" + str(asum))
        sleep(0.1)
    Logger.info("asum: " + str(asum))
    return asum

if __name__ == '__main__':
    #osc.init()
    #oscid = osc.listen(ipAddr='127.0.0.1', port=serviceport)
    #osc.bind(oscid, some_api_callback, '/some_api')
    i=0
    output = open(filename, 'a')
    output.write("first line... test...")
    output.close()
    output = open(filename, 'a')

    while True:
        i += 1
        #osc.readQueue(oscid)
        sleep(10.0)
        now = datetime.now()
        Logger.info("5s-" + str(now))
        output.write("\n-" + str(i) + "; " + str(now))
        if i % 6 == 0:
            output.close()
            output = open(filename, 'a')
            asum = get_accelerometer_activity()
            output.write("\n" + str(asum))

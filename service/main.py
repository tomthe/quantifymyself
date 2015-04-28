from time import sleep
from kivy.lib import osc
from datetime import datetime

from kivy.logger import Logger

serviceport = 3000
activityport = 3001
filename = "/storage/sdcard1/quantifyMyself/service.txt"

def some_api_callback(message, *args):
    print("got a message! %s" % message)
    answer_message()

def answer_message():
    osc.sendMsg('/some_api', [asctime(localtime()), ], port=activityport)

if __name__ == '__main__':
    osc.init()
    oscid = osc.listen(ipAddr='127.0.0.1', port=serviceport)
    osc.bind(oscid, some_api_callback, '/some_api')
    i=0
    output = open(filename, 'a')
    while True:
        i += 1
        osc.readQueue(oscid)
        sleep(10.0)
        now = datetime.now()
        Logger.info("5s-" + str(now))
        output.write("\n-" + str(i) + "; " + str(now))
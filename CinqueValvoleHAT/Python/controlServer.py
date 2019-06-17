import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
#from TapControl.ControlTap import updateTap
from valveControl import *
import socket
import pigpio

HOST_NAME = 'pumptapunit' # note: change to appropriate hostname
PORT_NUMBER = 8000

'''
    J.A. Korten 2019

'''

enableDebugPrints = False

def debugPrint(message):
    if (enableDebugPrints):
        print(message)

class ValveServerHandler(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        paths = {
            #'/soilsensor': {'status': 200},
            #'/sensordata': {'status': 200},
            '/valves/': {'status': 200}
        }

        if self.path in paths:
            self.respond(paths[self.path])
        else:
            try:
                self.respond({'status': 200})
            except BrokenPipeError:
            	debugPrint("Whoops: broken server pipe...")

    def handle_http(self, status_code, path):
        info = "<b>Tiny Webserver for valve control</b><br><br>/valves/valve=x&state=y where valve x is 0..4 and state y is open=0..close=1<br><br>see: <a href='http://www.jksoftedu.nl' target='_blank'>JKSOFT Edu</a> for more information..."
        content = info
        if (path.find("/valves/") == 0):
            url = urlparse(path)
            content = str(url)

            # parameters:
            try:
                tapIndex   = path.index("valve=") + 6
                stateIndex = path.index("state=") + 6

                tap = int(path[tapIndex])
                state = int(path[stateIndex])
                content = "Cannot set tap " + str(tap) + " to " + str(state) + "!"
                if ((0 <= tap <= 4) and (0 <= state <= 1)):
                    content = "Setting tap " + str(tap) + " to " + str(state) + "!"
                    debugPrint(content)
                    try:
                        global valveController
                        valveController.setValve(tap, state)
                    except:
                        debugPrint("Error: Issue setting valve...")
                    debugPrint("tap: " + str(tap))
                    debugPrint("tap state: " + str(state))
                    content = "Setting tap " + str(tap) + " to " + str(state) + " now..."
                    #updateTap(0, tap, state)

            except:
                content = "Error setting tap state...<br><br>" + info
            # check parameters
        return bytes(content, 'UTF-8')

    def respond(self, opts):
        self.do_HEAD()
        response = self.handle_http(opts['status'], self.path)
        self.wfile.write(response)


valveController = tapHatCinqController()

if __name__ == '__main__':
    server_class = HTTPServer
    HOST_NAME = socket.gethostname() # just to be sure...
    pi = pigpio.pi()
    if not pi.connected:
        print("Warning: pigpio is not running, start pigpio deamon and restart server...")
        exit() # or reporting the issue
    httpd = server_class((HOST_NAME, PORT_NUMBER), ValveServerHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))

# SprinklerSystem: CinqueValvoleHAT
Controller for a CinqueValvoleHAT hat using python.

The controlServer.py will let you start a simple server on your Raspberry Pi.

http://hostname:8000/valves/valve=0&state=1 will set valve 1 to open
http://hostname:8000/valves/valve=0&state=0 will set valve 1 to closed

The tapHatCinqController defines five possible valves you can use.
You could stake more than one CinqueValvoleHAT but then you need a special stacking header of course.

We have not done that for now but it would be easy to change the source code to accommodate for that
(add parameter for your url that you e.g. call 'module', parse that variable and send commands to
the appropriate instance).

All taps have a timeout as defined in that init method:
self.motor1 = DRV8871_Valve(0, 15.0, tapState.open)

This means:
- self.motor1 is defined as motor 0
- has a timeout of 15.0 seconds
- default state is open (change to closed if you want to reverse how your valve reacts)

Johan Korten
June 2019

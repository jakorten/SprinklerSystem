# SprinklerSystem: CinqueValvoleHAT
Repository for valve controllers etc.

## About
Here I publish updates to Python and Arduino scripts to create my / your own irrigation system.

June 2019:
- 5x Tap Controller board (v1.0 / v1.1) (CinqueValvoleHAT)

The CinqueValvoleHAT is used to control up to 5 valves.
- Typical valves have DC motors
- They will switch of when the limit is reached (fully open or fully closed)
- The print was designed to control 12V valves

Other DC motors can also be controlled using this HAT.
We have tested the HAT for 12V and below.

Most parts can handle up to 50V but that is the maximum, of you would
want to control 48V you should change some parts:
- 0.1uF/50V
- 22uF/63V

We use a voltage divider in v1.1 for AOD417, for 12V that would not have been
necessary. The AOD417 protects against wrong polarity.

The input (suggested 5V - 12V) is not connected to the rest of the system only to the
DRV8871 drivers.

Each DRV8871 can handle up to 3.6A (but is limited to about 2A by the 30k resistors) and
has a maximum voltage of 50V (< 45V recommended). In case you want to use the HAT as is
for 48V motors we suggest you make sure your supply only divers 45V or less which should
be more than enough for ball valves. Note: We did not test this so use at your own risk.

We did try to run our 12V ball valves at 7V and although they move slower they will work
just fine.

We used the valves from:
https://nl.aliexpress.com/store/4032047?spm=a2g0o.detail.1000002.2.6d6b58daLNaQAn
(e.g. https://nl.aliexpress.com/item/32896353276.html?spm=a2g0s.9042311.0.0.32b34c4dLBPZam)

## Source
The source lets your Raspberry Pi control the valves via a PCA9685 IC

## Credits

Thanks @Adafruit for not only providing us with the basis idea and HAT layout (https://www.adafruit.com/product/2348).
Their hat works well but we found it got too hot inside the narrow enclosure we used.
Also thanks to @Adafruit for their suggestion to use DRV8871 drivers (they sell separate boards).

Note: we have designed the HAT and software to interoperate with homebridge. We use a second Raspberry Pi that
runs homebridge and will allow to set the valves remotely.

# ToDo: Work in progress
==============================================================================================
- We have created a HMI system for operation without homebridge
- We still need to integrate this functionality with the current source.
- Other parts of the system will be uploaded as we go.
- We hope to make the system available for purchase using Tindie.

Johan Korten<br>
June 2019

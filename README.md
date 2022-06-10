# E-ink Photoframe Weather Display

A Dark Sky weather display for Waveshare's 7.5 inch e-ink display.  Displayed in a nice photoframe.

![E-ink photograme weather display](/docs/weatherframe.png)

☔ **This project requires a Dark Sky developer account.  Dark Sky will be shutting down at some point and they aren't
accepting new sign ups. When that happens, I'll probably port this project to another weather source.**

## Features:
- Shows current and hourly Dark Sky weather on Waveshare's 7.5 inch e-ink display, intended to be refreshed once or twice an hour 
- Graphs that show the chance of rain, cloud cover, and temperature over the next 12 hours 
- The current chance of rain and temperature
- Weather icons from Adam Whitcroft’s excellent Climacons
- Today's date

## Parts
- Raspberry Pi (any model should do as long as it has a GPIO header)
- [7.5inch e-Paper HAT](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT) by Waveshare
- Some way of mounting the eink display (I've put mine in a photo frame)

## Installation
- Follow [Waveshare's installation guide](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT#Users_Guides_of_Raspberry_Pi) for Raspberry Pi
- Create a python3 virtual environment and install the project's requirements
```
$ python3 -m venv eink_display_venv
$ source eink_display_venv/bin/activate
(eink_display_venv) $ pip install -r requirements.txt
```
- Open settings.py and enter your:
  - Latitude
  - Longitude
  - Your Dark Sky API key
  - Preferred units of measurement

Units of measurement options, from https://darksky.net/dev/docs:
``` 
auto: automatically select units based on geographic location
ca: same as si, except that windSpeed is in kilometers per hour
uk2: same as si, except that nearestStormDistance and visibility are in miles and windSpeed is in miles per hour
us: Imperial units (the default)
si: SI units
```

You should now be able to manually run the program and see the weather appear on your eink display.  It'll take a few seconds to update.
```
(eink_display_venv) $ python main.py
```

![E-ink photograme weather display updating](/docs/weather-update.gif)

## Automating it
You can automate the weather updates by running the program in a cronjob.

On your Raspberry Pi:
```
$ crontab -e
```

The following cron will update the weather display once every hour, on the hour.  Remember to put in your actual paths
to this project and your python virtual environment that you created earlier:
```
# m h dom mon dow  command
  0 *  *   *   *   cd /path/to/waveshare-eink-weather-display && /path/to/virtual_environment/bin/python main.py 
```

## Reading the display
The display is split into the following sections:
- Todays date
- An icon summarising the weather
- On the left, the chance of rain as a percentage for the current hour
- On the right, the current temperature
- The left graph shows both chance of rain (solid black line) and cloud cover (dotted line) over the next 12 hours
- The right graph shows the temperature over the next 12 hours

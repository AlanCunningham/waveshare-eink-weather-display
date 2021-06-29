import settings
import epd7in5_V2
import requests
import time
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont


def get_weather():
    """
    Fetches the weather from an API.
    Returns weather information as json
    """
    latitude = settings.latitude
    longitude = settings.longitude
    weather_endpoint = settings.endpoint
    api_key = settings.api_key
    request_url = f"{weather_endpoint}/{api_key}/{latitude},{longitude}"
    payload = {
        "units": settings.units
    }
    weather_data = requests.get(request_url, params=payload)
    return weather_data


def main():
    weather_data = get_weather().json()
    # weather_data = {
    #     "currently": {
    #         "icon": "rain",
    #         "summary": "Overcast",
    #         "apparentTemperature": 18,
    #     }
    # }
    current_weather = weather_data["currently"]
    # Initialise and clear the e-ink screen
    print("Initialising screen")
    epd = epd7in5_V2.EPD()
    epd.init()
    print("Clearing screen")
    epd.Clear()

    normal = ImageFont.truetype("Font.ttc", 40)
    large = ImageFont.truetype("Font.ttc", 64)
    Himage = Image.new("1", (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(Himage)

    # Today's date
    now = datetime.now()
    date_format = now.strftime("%a %d %b")
    draw.text((90, 50), f"{date_format}", font=normal, fill=0)

    # Today's weather
    image_dir = "climacons"
    current_weather_icon = current_weather["icon"]
    weather_icon = Image.open(f"{image_dir}/rain.png")
    Himage.paste(weather_icon, (120, 130))
    # Temperature
    rounded_current_temperature = str(int(round(current_weather["apparentTemperature"])))
    draw.text((125, 230), f"{rounded_current_temperature}°", font=large, fill=0)
    # Weather summary
    draw.text((90, 285), current_weather["summary"], font=normal, fill=0)

    # Daily weather
    daily_weather = weather_data["daily"]["data"]
    tomorrow = daily_weather[1]
    overmorrow = daily_weather[2]

    # Tomorrow's weather
    tomorrow_day_name = datetime.fromtimestamp(tomorrow["time"]).strftime("%a")
    draw.text((400, 50), tomorrow_day_name, font=normal, fill=0)
    tomorrow_weather_icon = tomorrow["icon"]
    weather_icon = Image.open(f"{image_dir}/rain.png")
    Himage.paste(weather_icon, (400, 130))
    # Temperature
    average_temperature = tomorrow["apparentTemperatureHigh"] + tomorrow["apparentTemperatureLow"] / 2
    rounded_tomorrow_temperature = str(int(round(average_temperature)))
    draw.text((420, 230), f"{rounded_tomorrow_temperature}°", font=normal, fill=0)

    # Overmorrow's weather
    overmorrow_day_name = datetime.fromtimestamp(overmorrow["time"]).strftime("%a")
    draw.text((600, 50), overmorrow_day_name, font=normal, fill=0)
    overmorrow_weather_icon = overmorrow["icon"]
    weather_icon = Image.open(f"{image_dir}/rain.png")
    Himage.paste(weather_icon, (600, 130))
    # Temperature
    average_temperature = overmorrow["apparentTemperatureHigh"] + overmorrow["apparentTemperatureLow"] / 2
    rounded_overmorrow_temperature = str(int(round(average_temperature)))
    draw.text((620, 230), f"{rounded_overmorrow_temperature}°", font=normal, fill=0)

    # Display the buffer to the eink screen
    print("Displaying image")
    epd.display(epd.getbuffer(Himage))
    time.sleep(5)
    epd.sleep()
    print("Finished")


if __name__ == "__main__":
    main()
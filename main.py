import settings
import epd7in5_V2
import requests
import time
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import matplotlib.pyplot as plt


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

    # Hourly temperature
    # The graph takes up a lot of space, so we draw this first so other text
    # and images can be drawn on top of it.
    hourly_weather = weather_data["hourly"]["data"]
    number_of_hours = 12
    temperature_list = []
    hour_list = []
    for index, hour in enumerate(hourly_weather):
        if index == number_of_hours:
            break
        temperature_list.append(hour["apparentTemperature"])
        converted_time = datetime.fromtimestamp(hour["time"]).strftime("%H:%M")
        hour_list.append(converted_time)
    # Plot the graph, save it as an image and add to the eink buffer
    plt.figure(figsize=(8, 2))
    plt.plot(hour_list, temperature_list, linewidth=3.0)
    plt.savefig("temperature_graph.png")
    temperature_graph = Image.open(f"temperature_graph.png")
    Himage.paste(temperature_graph, (10, 260))

    # Relative co-ordinates
    day_title_x = 90
    day_title_y = 50
    weather_icon_y = 115
    temperature_y = 210

    # Today's date
    now = datetime.now()
    date_format = now.strftime("%a %d %b")
    draw.text((day_title_x, day_title_y), f"{date_format}", font=normal)
    # Today's weather
    image_dir = "climacons"
    current_weather_icon = current_weather["icon"]
    weather_icon = Image.open(f"{image_dir}/rain.png")
    Himage.paste(weather_icon, (120, weather_icon_y))
    # Temperature
    rounded_current_temperature = str(int(round(current_weather["apparentTemperature"])))
    draw.text((145, temperature_y), f"{rounded_current_temperature}°", font=normal)
    # Weather summary
    # draw.text((90, 275), current_weather["summary"], font=normal)

    # Daily weather
    daily_weather = weather_data["daily"]["data"]
    tomorrow = daily_weather[1]
    overmorrow = daily_weather[2]

    # Tomorrow's weather
    tomorrow_day_name = datetime.fromtimestamp(tomorrow["time"]).strftime("%a")
    draw.text((400, day_title_y), tomorrow_day_name, font=normal)
    tomorrow_weather_icon = tomorrow["icon"]
    weather_icon = Image.open(f"{image_dir}/rain.png")
    Himage.paste(weather_icon, (400, weather_icon_y))
    # Temperature
    average_temperature = tomorrow["apparentTemperatureHigh"] + tomorrow["apparentTemperatureLow"] / 2
    rounded_tomorrow_temperature = str(int(round(average_temperature)))
    draw.text((420, temperature_y), f"{rounded_tomorrow_temperature}°", font=normal)

    # Overmorrow's weather
    overmorrow_day_name = datetime.fromtimestamp(overmorrow["time"]).strftime("%a")
    draw.text((620, day_title_y), overmorrow_day_name, font=normal)
    overmorrow_weather_icon = overmorrow["icon"]
    weather_icon = Image.open(f"{image_dir}/rain.png")
    Himage.paste(weather_icon, (600, weather_icon_y))
    # Temperature
    average_temperature = overmorrow["apparentTemperatureHigh"] + overmorrow["apparentTemperatureLow"] / 2
    rounded_overmorrow_temperature = str(int(round(average_temperature)))
    draw.text((620, temperature_y), f"{rounded_overmorrow_temperature}°", font=normal)

    # Display the buffer to the eink screen
    print("Displaying image")
    epd.display(epd.getbuffer(Himage))
    time.sleep(5)
    epd.sleep()
    print("Finished")


if __name__ == "__main__":
    main()

import settings
import epd7in5_V2
import requests
import time
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


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


def draw_underlined_text(draw, pos, text, font, **options):
    """
    Draw text with a horizontal line underneath.
    See https://stackoverflow.com/questions/3777861/setting-y-axis-limit-in-matplotlib
    """
    twidth, theight = draw.textsize(text, font=font)
    lx, ly = pos[0], pos[1] + theight
    draw.text(pos, text, font=font, **options)
    padding_top = 5
    draw.line((lx, ly + padding_top, lx + twidth, ly + padding_top), **options)


def main():
    weather_data = get_weather().json()
    current_weather = weather_data["currently"]
    # Initialise and clear the e-ink screen
    print("Initialising screen")
    epd = epd7in5_V2.EPD()
    epd.init()

    normal = ImageFont.truetype("Font.ttc", 40)
    large = ImageFont.truetype("Font.ttc", 64)
    Himage = Image.new("1", (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(Himage)

    # Layout
    max_left = 90
    max_right = 700
    left_column_x = 90
    todays_day_name_x = 90
    todays_day_name_y = 50
    todays_date_x = 90
    todays_date_y = 50
    weather_icon_x = int(max_right / 2)
    weather_icon_y = 115
    umbrella_icon_x = max_left + 50
    umbrella_icon_y = 200
    rain_chance_x = umbrella_icon_x + 80
    rain_chance_y = 200
    current_temperature_icon_x = max_right - 180
    current_temperature_icon_y = umbrella_icon_y
    current_temperature_x = current_temperature_icon_x + 65
    current_temperature_y = rain_chance_y
    # Summary
    summary_x = left_column_x
    summary_y = 220
    # Temperature graph
    temperature_graph_x = 420
    temperature_graph_y = 260
    rain_graph_x = 60
    rain_graph_y = 260
    # Height and width of both graphs in inches
    graphs_width = 3.5
    graphs_height = 2

    # The graphs takes up a lot of space, so we draw this first so other text
    # and images can be drawn on top of it.
    # Hourly temperature graph
    hourly_weather = weather_data["hourly"]["data"]
    number_of_hours = 12
    temperature_list = []
    hour_list = []
    rain_chance_list = []
    cloud_cover_list = []
    for index, hour in enumerate(hourly_weather):
        if index == number_of_hours:
            break
        temperature_list.append(hour["apparentTemperature"])
        converted_time = datetime.fromtimestamp(hour["time"]).strftime("%H")
        hour_list.append(converted_time)
        rain_chance_list.append(hour["precipProbability"] * 100)
        cloud_cover_list.append(hour["cloudCover"] * 100)
        print(f"{hour}: {hour['precipProbability']}")
    # Plot the graph, save it as an image and add to the eink buffer
    plt.figure(figsize=(graphs_width, graphs_height))
    plt.grid()
    plt.ylim(0, 100)
    plt.plot(hour_list, rain_chance_list, linewidth=3.0)
    plt.plot(hour_list, cloud_cover_list, linestyle="--", linewidth=2.0)
    plt.savefig("rain_graph.png")

    plt.figure(figsize=(graphs_width, graphs_height))
    plt.grid()
    plt.plot(hour_list, temperature_list, linewidth=3.0)
    plt.savefig("temperature_graph.png")

    temperature_graph = Image.open("temperature_graph.png")
    rain_graph = Image.open("rain_graph.png")
    Himage.paste(temperature_graph, (temperature_graph_x, temperature_graph_y))
    Himage.paste(rain_graph, (rain_graph_x, rain_graph_y))

    # Images
    image_dir = "climacons"
    # If chance of rain is 100%, shift the icon and text over to the left slightly
    rain_chance = int(current_weather["precipProbability"] * 100)
    if rain_chance == 100:
        umbrella_icon_x = max_left + 40
        rain_chance_x = umbrella_icon_x + 70
    umbrella_icon = Image.open(f"{image_dir}/umbrella.png")
    Himage.paste(umbrella_icon, (umbrella_icon_x, umbrella_icon_y))
    temperature_icon = Image.open(f"{image_dir}/temperature-50.png")
    Himage.paste(temperature_icon, (current_temperature_icon_x, current_temperature_icon_y))

    # Today's date
    now = datetime.now()
    todays_day_name = now.strftime("%A")
    todays_date = now.strftime("%A %d %B")
    # draw.text((todays_day_name_x, todays_day_name_y), todays_day_name, font=normal)
    draw_underlined_text(draw, (todays_date_x, todays_date_y), todays_date, font=normal, width=4)
    # draw.text((todays_date_x, todays_date_y), todays_date, font=normal)
    # Chance of rain
    rain_chance = int(round(current_weather["precipProbability"] * 100))
    print(f"Rain chance: {current_weather['precipProbability']}")
    draw.text((rain_chance_x, rain_chance_y), f"{rain_chance}%", font=large)
    # Weather icon
    # Convert 200x200 svg images to png, resized to around 100x100.
    current_weather_icon = current_weather["icon"]
    try:
        weather_icon = Image.open(f"{image_dir}/{current_weather_icon}.png")
        Himage.paste(weather_icon, (weather_icon_x, weather_icon_y))
    except Exception:
        draw.text((weather_icon_x, weather_icon_y), f"Image {current_weather_icon} not found", font=normal)
    # Current Temperature
    current_temperature = str(int(round(current_weather["apparentTemperature"])))
    draw.text((current_temperature_x, current_temperature_y), f"{current_temperature}°", font=large)
    # Weather summary
    # draw.text((summary_x, summary_y),  weather_data["hourly"]["summary"], font=normal)

    print("Clearing screen")
    epd.Clear()
    # Display the buffer to the eink screen
    print("Displaying image")
    epd.display(epd.getbuffer(Himage))
    time.sleep(5)
    epd.sleep()
    print("Finished")


if __name__ == "__main__":
    main()

import os
from sense_hat import SenseHat
from Adafruit_IO import Client, Feed, Data
import time

# --- Environment Variable Loading ---
# Import load_dotenv from the dotenv library to load environment variables from a .env file.
from dotenv import load_dotenv
# Load environment variables from the .env file.
# This allows sensitive information like API keys to be kept out of the source code.
load_dotenv()

# --- Sense HAT Initialization ---
# Create an instance of Sense HAT.
sense = SenseHat()
# Clear the LED display, turning all pixels off.
sense.clear()

# --- Adafruit IO Settings ---
# Retrieve Adafruit IO username and key from environment variables.
# These should be defined in a .env file in the project root.
ADAFRUIT_IO_USERNAME = os.getenv('ADAFRUIT_IO_USERNAME')
ADAFRUIT_IO_KEY = os.getenv('ADAFRUIT_IO_KEY')

# Initialize Adafruit IO client.
# This client object is used to interact with the Adafruit IO platform (e.g., receiving data).
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# --- Adafruit IO Feed Names ---
# Define a dictionary mapping internal sensor names to their corresponding Adafruit IO feed keys.
# These feed keys must match the feeds created on the Adafruit IO dashboard.
feeds = {
    'pressure': 'pressure',
    'temperature': 'temperature',
    'magnetometer': 'magnetometer',
    'humidity': 'humidity'
}

# --- Color Definitions for Sense HAT LED Display ---
# Define RGB color tuples for displaying different sensor data on the Sense HAT LED matrix.
colors = {
    'pressure': [255, 0, 0],    # Red for pressure
    'temperature': [0, 255, 0],  # Green for temperature
    'magnetometer': [0, 0, 255], # Blue for magnetometer
    'humidity': [255, 255, 0]    # Yellow for humidity
}

def display_on_sense_hat(feed_name, value):
    """
    Displays the fetched sensor data on the Sense HAT's LED matrix.
    The message format and text color depend on the type of sensor data.
    :param feed_name: The name of the Adafruit IO feed (e.g., 'pressure', 'temperature').
    :param value: The sensor reading value to display.
    """
    # Display data on Sense HAT based on the feed name.
    if feed_name == feeds['pressure']:
        sense.show_message(f"BP: {value:.2f} hPa", text_colour=colors['pressure'])
    
    elif feed_name == feeds['temperature']:
        sense.show_message(f"Temp: {value:.2f} degree celsius", text_colour=colors['temperature'])
    
    elif feed_name == feeds['magnetometer']:
        sense.show_message(f"Mag: {value:.2f} degrees", text_colour=colors['magnetometer'])
    
    elif feed_name == feeds['humidity']:
        sense.show_message(f"Hum: {value:.2f} %", text_colour=colors['humidity'])

def fetch_and_display_data(feed_name):
    """
    Fetches the latest data from a specified Adafruit IO feed and displays it.
    It handles potential errors during data reception and format conversion.
    :param feed_name: The name of the Adafruit IO feed to fetch data from.
    """
    try:
        # Receive the latest data value from the Adafruit IO feed.
        data = aio.receive(feed_name).value
        # Convert the received data string to a float.
        value = float(data)
        
        # Get current timestamp for console output.
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        # Print the fetched data to the console.
        print(f"{timestamp} - The value of {feed_name.capitalize()} from Adafruit is: {value:.2f}")
        # Display the fetched data on the Sense HAT LED matrix.
        display_on_sense_hat(feed_name, value)
        print("Done!!!\n") # Indicate successful display.
    
    except ValueError:
        # Handle cases where the received data cannot be converted to a float.
        print(f"Invalid data format for {feed_name}: {data}")
    
    except Exception as e:
        # Catch any other exceptions during data reception.
        print(f"Error receiving data from {feed_name}: {e}")

# --- Main Loop for Data Fetching and Display ---
# This loop continuously fetches data from Adafruit IO feeds and displays it.
while True:
    # Fetch and display data for each sensor type.
    fetch_and_display_data(feeds['pressure'])
    fetch_and_display_data(feeds['temperature'])
    fetch_and_display_data(feeds['magnetometer'])
    fetch_and_display_data(feeds['humidity'])
    
    # Wait for 15 seconds before the next data fetch cycle.
    # This interval controls the frequency of data updates from Adafruit IO.
    time.sleep(15)










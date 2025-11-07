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

# --- Adafruit IO Settings ---
# Retrieve Adafruit IO username and key from environment variables.
# These should be defined in a .env file in the project root.
ADAFRUIT_IO_USERNAME = os.getenv('ADAFRUIT_IO_USERNAME')
ADAFRUIT_IO_KEY = os.getenv('ADAFRUIT_IO_KEY')

# Initialize Adafruit IO client.
# This client object is used to interact with the Adafruit IO platform (e.g., sending data).
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# --- Sense HAT Initialization ---
# Create an instance of Sense HAT.
sense = SenseHat()
# Clear the LED display, turning all pixels off.
sense.clear()

# --- Adafruit IO Feed Names ---
# Define a dictionary mapping internal sensor names to their corresponding Adafruit IO feed keys.
# These feed keys must match the feeds created on the Adafruit IO dashboard.
feeds = {
    'pressure': 'pressure',
    'temperature': 'temperature',
    'magnetometer': 'magnetometer',
    'humidity': 'humidity'
}

# --- Sensor Data Retrieval Functions ---
def get_barometric_pressure():
    """
    Reads the barometric pressure from the Sense HAT sensor.
    The reading is rounded to two decimal places.
    :return: Barometric pressure in hPa (hectopascals).
    """
    barometric_pressure = sense.get_pressure()
    barometric_pressure = round(barometric_pressure, 2)
    return barometric_pressure

def get_temperature():
    """
    Reads the temperature from the Sense HAT.
    It averages readings from the humidity and pressure sensors for better accuracy.
    :return: Temperature in degrees Celsius.
    """
    htemp = sense.get_temperature()  # Temperature from humidity sensor
    ptemp = sense.get_temperature_from_pressure() # Temperature from pressure sensor
    temp = round((htemp + ptemp) / 2, 2)  # Average of the two readings
    return temp

def get_compass():
    """
    Reads the magnetometer (compass) data from the Sense HAT.
    The reading represents the direction in degrees (north).
    :return: Magnetometer reading in degrees.
    """
    magnetometer_north = sense.get_compass()
    magnetometer_north = round(magnetometer_north, 2)
    return magnetometer_north

def get_humidity():
    """
    Reads the relative humidity from the Sense HAT sensor.
    The reading is rounded to two decimal places.
    :return: Relative humidity in percentage (%).
    """
    humidity = sense.get_humidity()
    humidity = round(humidity, 2)
    return humidity

# --- Main Loop for Data Publishing ---
# This loop continuously reads sensor data and publishes it to Adafruit IO.
while True:
    # Read current sensor data.
    barometric_pressure = get_barometric_pressure()
    temperature = get_temperature()
    magnetometer = get_compass()
    humidity = get_humidity()

    # Get current timestamp for console output.
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Print all sensor data to the console for monitoring.
    print(f"{timestamp} - barometric pressure: {barometric_pressure:.2f} hPa, temperature: {temperature:.2f} degree Celsius,"
          f"Magnetometer: {magnetometer:.2f} degrees, Humidity: {humidity:.2f} %")

    # Send each sensor data point to its corresponding Adafruit IO feed.
    # The aio.send() method publishes the data to the cloud.
    aio.send(feeds['pressure'], barometric_pressure)
    aio.send(feeds['temperature'], temperature)
    aio.send(feeds['magnetometer'], magnetometer)
    aio.send(feeds['humidity'], humidity)

    # Wait for 15 seconds before the next cycle of reading and publishing.
    # This interval controls the data update frequency on Adafruit IO.
    time.sleep(15)

    



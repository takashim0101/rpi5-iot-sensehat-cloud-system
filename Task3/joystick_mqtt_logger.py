from sense_hat import SenseHat
import paho.mqtt.client as paho
import csv
import os
import time
from datetime import datetime  # Importing datetime module for timestamps

# --- Sense HAT Initialization ---
# Create an instance of Sense HAT.
sense = SenseHat()
# Clear the LED display, turning all pixels off.
sense.clear()

# --- Color Definitions for LED Display ---
# These RGB tuples are used to display letters on the Sense HAT LED matrix
# with different colors based on joystick input.
red = (255, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

# --- CSV File Management ---
# Define the directory where CSV files will be saved.
# This path is specific to the user's desktop environment.
csv_directory = "/home/takashi/Desktop/DANCT702_A2/DANCT702_A2_CSV_files"

# Ensure the CSV directory exists. If not, create it.
if not os.path.exists(csv_directory):
    os.makedirs(csv_directory)
    print(f"Directory created: {csv_directory}")
else:
    print(f"Directory already exists: {csv_directory}")

# --- MQTT Callbacks ---
def on_subscribe(client, userdata, mid, granted_qos):
    """
    Callback function executed when the MQTT client successfully subscribes to a topic.
    Prints information about the subscribed topic.
    :param client: The client instance for this callback.
    :param userdata: The private user data.
    :param mid: The message ID of the subscribe request.
    :param granted_qos: A list of integers indicating the QoS level granted for each topic.
    """
    print("The subscribed topic is: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    """
    Callback function executed when a message is received on a subscribed topic.
    It decodes the message payload and writes it to a corresponding CSV file.
    :param client: The client instance for this callback.
    :param userdata: The private user data.
    :param msg: An MQTTMessage object containing topic, payload, qos, retain, etc.
    """
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    # Determine which CSV file to write to based on the message topic.
    if msg.topic == "TempeTopic":
        write("Temperature.csv", msg.payload)
    elif msg.topic == "PressureTopic":
        write("Barometric pressure.csv", msg.payload)
    elif msg.topic == "HumidityTopic":
        write("Humidity.csv", msg.payload)
    elif msg.topic == "MagnetometerTopic":
        write("Magnetometer.csv", msg.payload)

# --- Data Logging Function ---
def write(title, data):
    """
    Writes sensor data along with a timestamp to a specified CSV file.
    :param title: The filename of the CSV file (e.g., "Temperature.csv").
    :param data: The sensor data payload received from MQTT.
    """
    file_path = os.path.join(csv_directory, title)
    print(f"Writing data to {file_path}")

    # Get the current timestamp in "YYYY-MM-DD HH:MM:SS" format.
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Decode the data payload. If data is empty or None, default to "0".
    decoded_data = data.decode() if data else "0"
    
    # Format the decoded data to two decimal places as a float.
    formatted_data = f"{float(decoded_data):.2f}"

    # Append the timestamp and formatted data to the CSV file.
    # The 'a' mode opens the file for appending.
    with open(file_path, mode="a") as file:
        file.write(f"{current_time}, {formatted_data}\n")

# --- MQTT Client Setup ---
# Create a new MQTT client instance.
client = paho.Client()
# Assign callback functions for message reception and subscription confirmation.
client.on_message = on_message
client.on_subscribe = on_subscribe
# Connect to the MQTT broker (local host in this case) with a keepalive interval of 60 seconds.
client.connect("127.0.0.1", 1883, 60)
# Start a new thread to handle MQTT network traffic (sending/receiving messages).
client.loop_start()

# --- User Instructions ---
# Print instructions to the console for how to use the joystick to control subscriptions.
print("...........................Program Starts................" + "\n")
print("....Use the Joystick to Subscribe a topic......: " + "\n")
print("Joystick control: Up will show you a Temperature Topic")
print("Joystick control: Down will show you a Pressure Topic ")
print("Joystick control: Left will show you a Humidity Topic")
print("Joystick control: Right will show you a Magnetometer Topic" + "\n")

# Variable to track whether data publishing (from this script) should be active.
# This script primarily subscribes, but also publishes sensor data when a topic is selected.
data_publishing = False

# --- Main Program Loop ---
try:
    # Infinite loop to continuously monitor joystick events and publish data if enabled.
    while True:
        # Iterate through all joystick events that have occurred.
        for event in sense.stick.get_events():
            # Check the direction of the joystick event.
            if event.direction == 'up':
                print("Joystick button UP pressed and released. Subscribing to Temperature Topic.")
                sense.show_letter("U", text_colour=yellow) # Display 'U' on LED matrix
                client.subscribe("TempeTopic") # Subscribe to Temperature topic
                # Unsubscribe from other topics to ensure only one is active at a time.
                client.unsubscribe("PressureTopic")
                client.unsubscribe("HumidityTopic")
                client.unsubscribe("MagnetometerTopic")
                data_publishing = True  # Enable data publishing from this script

            elif event.direction == 'down':
                print("Joystick button DOWN pressed and released. Subscribing to Pressure Topic.")
                sense.show_letter("D", text_colour=blue) # Display 'D' on LED matrix
                client.subscribe("PressureTopic") # Subscribe to Pressure topic
                client.unsubscribe("TempeTopic")
                client.unsubscribe("HumidityTopic")
                client.unsubscribe("MagnetometerTopic")
                data_publishing = True  # Enable data publishing

            elif event.direction == 'left':
                print("Joystick button LEFT pressed and released. Subscribing to Humidity Topic.")
                sense.show_letter("L", text_colour=green) # Display 'L' on LED matrix
                client.subscribe("HumidityTopic") # Subscribe to Humidity topic
                client.unsubscribe("TempeTopic")
                client.unsubscribe("PressureTopic")
                client.unsubscribe("MagnetometerTopic")
                data_publishing = True  # Enable data publishing

            elif event.direction == 'right':
                print("Joystick button RIGHT pressed and released. Subscribing to Magnetometer Topic.")
                sense.show_letter("R", text_colour=red) # Display 'R' on LED matrix
                client.subscribe("MagnetometerTopic") # Subscribe to Magnetometer topic
                client.unsubscribe("TempeTopic")
                client.unsubscribe("PressureTopic")
                client.unsubscribe("HumidityTopic")
                data_publishing = True  # Enable data publishing

            elif event.direction == 'middle':
                print("Joystick button MIDDLE pressed and released. Unsubscribing from all topics.")
                sense.show_letter("M", text_colour=red, back_colour=white) # Display 'M' on LED matrix
                # Unsubscribe from all known topics.
                client.unsubscribe("TempeTopic")
                client.unsubscribe("PressureTopic")
                client.unsubscribe("HumidityTopic")
                client.unsubscribe("MagnetometerTopic")
                data_publishing = False  # Disable data publishing

        # If data publishing is enabled (i.e., a sensor topic is selected via joystick).
        if data_publishing:
            # Define local helper functions to get current sensor readings.
            # These are defined within the loop to ensure they use the latest Sense HAT state.
            def get_pressure():
                return round(sense.get_pressure(), 2)

            def get_temperature():
                htemp = sense.get_temperature()
                ptemp = sense.get_temperature_from_pressure()
                return round((htemp + ptemp) / 2, 2)

            def get_compass():
                return round(sense.get_compass(), 2)

            def get_humidity():
                return round(sense.get_humidity(), 2)

            # Read current sensor data.
            temperature = get_temperature()
            humidity = get_humidity()
            pressure = get_pressure()
            magnetometer = get_compass()

            # Publish the current sensor data to their respective topics.
            # Note: This script both subscribes to and publishes to these topics.
            client.publish("TempeTopic", temperature)
            client.publish("HumidityTopic", humidity)
            client.publish("PressureTopic", pressure)
            client.publish("MagnetometerTopic", magnetometer)

            # Display the published data to the console.
            print(f"Published: Temperature={temperature:.2f}, Humidity={humidity:.2f}, Barometric pressure={pressure:.2f}, Magnetometer={magnetometer:.2f}")

            # Wait for 1 second before the next publishing cycle.
            time.sleep(1)

except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to gracefully exit the program.
    print("Exiting...")
finally:
    # Disconnect the MQTT client from the broker.
    client.disconnect()






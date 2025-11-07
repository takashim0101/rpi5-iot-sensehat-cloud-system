import time
import json
import paho.mqtt.client as mqtt # Use your own Alias
from sense_hat import SenseHat

# --- MQTT Settings ---
# The IP address of the MQTT broker.
# For local testing, this is typically "127.0.0.1".
# For cloud brokers, this would be their specific address (e.g., "broker.emqx.io").
MQTT_BROKER = "127.0.0.1"  # Replace with your MQTT broker address
# The port number for MQTT communication. Standard unencrypted port is 1883.
MQTT_PORT = 1883
# Define specific MQTT topics for each sensor data type.
# These topics act as channels for publishing and subscribing to data.
MQTT_TOPIC_PRESSURE = "home/sensors/pressure"
MQTT_TOPIC_TEMPERATURE = "home/sensors/temperature"
MQTT_TOPIC_MAGNETOMETER = "home/sensors/magnetometer"
MQTT_TOPIC_HUMIDITY = "home/sensors/humidity"

# Create an MQTT client instance.
# protocol=mqtt.MQTTv5 specifies the MQTT protocol version to use.
client = mqtt.Client(protocol=mqtt.MQTTv5)

def on_connect(client, userdata, flags, rc, properties=None):
    """
    Callback function that is called when the client successfully connects to the MQTT broker.
    It prints a connection status message based on the return code (rc).
    :param client: The client instance for this callback.
    :param userdata: The private user data as set in Client() or userdata_set().
    :param flags: Response flags sent by the broker.
    :param rc: The connection result code. 0 means success.
    :param properties: MQTTv5 properties.
    """
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Failed to connect, return code {rc}\n")

# Initialize Sense HAT.
# This object provides access to the Sense HAT's sensors and LED display.
sense = SenseHat()
# Clear the LED display, turning all pixels off.
sense.clear()

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
    temp = (htemp + ptemp) / 2  # Average of the two readings
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

# --- Main Program Execution ---
try:
    # Assign the on_connect callback function.
    client.on_connect = on_connect
    # Connect to the MQTT broker.
    # The last argument (60) is the keepalive interval in seconds.
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # Start a new thread to process network traffic (send/receive messages).
    # This allows the main thread to continue with sensor reading and publishing.
    client.loop_start()

    iteration = 0 # Initialize iteration counter for console output.

    # Infinite loop to continuously read sensors and publish data.
    while True:
        try:
            # Read data from all Sense HAT sensors.
            temperature = get_temperature()
            humidity = get_humidity()
            pressure = get_barometric_pressure()
            magnetometer = get_compass()

            # Increment and print the current iteration number.
            iteration += 1
            print(f"Iteration {iteration}")
            # Print all sensor data to the console for real-time monitoring.
            print(f"Temperature: {temperature:.2f} degree celsius")
            print(f"Humidity: {humidity:.2f} %")
            print(f"Pressure: {pressure:.2f} hPa")
            print(f"Magnetometer: {magnetometer:.2f} degrees")
            print("-" * 72)

            # Get current timestamp for data logging.
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Current date & time {timestamp}")

            # Create a JSON object containing all sensor data and timestamp.
            # This is useful for publishing a single, comprehensive message.
            sensor_data = {
                "timestamp": timestamp,
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "magnetometer": magnetometer
            }

            print("-" * 72)

            # Publish each sensor data point to its respective MQTT topic.
            # json.dumps() converts the Python dictionary to a JSON string.
            # qos=0 means "at most once" delivery (no guarantee of delivery).
            # retain=False means the broker will not store the last message.
            client.publish(MQTT_TOPIC_PRESSURE, json.dumps({"pressure": pressure}), qos=0, retain=False)
            print(f"Published to {MQTT_TOPIC_PRESSURE}: {pressure:.2f} (QoS: 0, Retain: False)")

            client.publish(MQTT_TOPIC_TEMPERATURE, json.dumps({"temperature": temperature}), qos=0, retain=False)
            print(f"Published to {MQTT_TOPIC_TEMPERATURE}: {temperature:.2f} degree celsius (QoS: 0, Retain: False)")

            client.publish(MQTT_TOPIC_MAGNETOMETER, json.dumps({"magnetometer": magnetometer}), qos=0, retain=False)
            print(f"Published to {MQTT_TOPIC_MAGNETOMETER}: {magnetometer:.2f} degrees (QoS: 0, Retain: False)")

            client.publish(MQTT_TOPIC_HUMIDITY, json.dumps({"humidity": humidity}), qos=0, retain=False)
            print(f"Published to {MQTT_TOPIC_HUMIDITY}: {humidity:.2f} (QoS: 0, Retain: False)")

            # Wait for 1 second before the next sensor reading and publishing cycle.
            time.sleep(1)

        except Exception as e:
            # Catch any exceptions during sensor reading or data publishing.
            print(f"Error reading sensors or publishing data: {e}")

except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to gracefully exit the program.
    print("Exiting program.")
finally:
    # Stop the MQTT network loop and disconnect from the broker.
    client.loop_stop()
    client.disconnect()


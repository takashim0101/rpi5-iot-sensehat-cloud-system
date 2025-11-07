import time
import paho.mqtt.client as mqtt
from sense_hat import SenseHat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- MQTT Settings ---
# The MQTT broker address and topics for different sensor data are defined.
# Although MQTT client is set up, this script primarily focuses on local data visualization.
MQTT_BROKER = "127.0.0.1"  # Replace with your MQTT broker address
MQTT_PORT = 1883
MQTT_TOPIC_PRESSURE = "home/sensors/pressure"
MQTT_TOPIC_TEMPERATURE = "home/sensors/temperature"
MQTT_TOPIC_MAGNETOMETER = "home/sensors/magnetometer"
MQTT_TOPIC_HUMIDITY = "home/sensors/humidity"

# Create an MQTT client instance using the latest API version (MQTTv5).
client = mqtt.Client(protocol=mqtt.MQTTv5)

def on_connect(client, userdata, flags, rc, properties=None):
    """
    Callback function executed when the MQTT client successfully connects to the broker.
    Prints a status message indicating connection success or failure.
    """
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Failed to connect, return code {rc}\n")

# Assign the connection callback function to the client.
client.on_connect = on_connect

# Initialize Sense HAT.
# This object provides access to the Sense HAT's sensors and LED display.
sense = SenseHat()
# Clear the LED display, turning all pixels off.
sense.clear()

# --- Sensor Data Retrieval Functions ---
def get_pressure():
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

# --- Data Storage for Plotting ---
# Initialize lists to store sensor data over time for plotting.
temperatures = []
humidities = []
pressures = []
magnetometer_data = []
times = [] # Stores Unix timestamps

# --- Matplotlib Plot Initialization ---
# Create a figure and a set of subplots (4 rows, 1 column) for each sensor.
fig, axs = plt.subplots(4, 1, figsize=(8, 6))
# Set the main title for the entire figure.
fig.suptitle('Real-time Sensor Data', fontsize=14)

def update_plot(i):
    """
    This function is called repeatedly by FuncAnimation to update the plots.
    It reads current sensor data, appends it to lists, and redraws the plots.
    :param i: The frame number (unused in this specific implementation but required by FuncAnimation).
    """
    # Read current values from the Sense HAT sensors.
    temperature = get_temperature()
    humidity = get_humidity()
    pressure = get_pressure()
    magnetometer = get_compass()

    # Append the newly read data to their respective lists.
    temperatures.append(temperature)
    humidities.append(humidity)
    pressures.append(pressure)
    magnetometer_data.append(magnetometer)

    # Get the current Unix timestamp (seconds since epoch).
    current_time = int(time.time())
    times.append(current_time)

    # Wait for 1 second before collecting the next timestamp.
    # This sleep also controls the update rate of the plot.
    time.sleep(1)

    # Print the collected timestamps for debugging/monitoring.
    print("Collected timestamps:", times)    

    # Convert absolute Unix timestamps to relative time in seconds
    # from the start of data collection. This makes the x-axis more readable.
    times_in_seconds = [(t - times[0]) for t in times]  

    # Limit the data to the last 100 entries to keep the plots manageable and real-time.
    if len(times_in_seconds) > 100:
        temperatures.pop(0) # Remove the oldest data point
        humidities.pop(0)
        pressures.pop(0)
        magnetometer_data.pop(0)
        times_in_seconds.pop(0)

    # --- Update each subplot ---
    # Clear the previous plot content.
    axs[0].clear()
    # Plot temperature data.
    axs[0].plot(times_in_seconds, temperatures, label='Temperature', color='red')
    axs[0].set_ylabel('Temp (°C)', fontsize=10)
    axs[0].legend(fontsize=8)
    # Display the latest temperature value on the plot.
    axs[0].text(times_in_seconds[-1], temperatures[-1], f'{temperatures[-1]:.2f}', ha='right', fontsize=8)

    axs[1].clear()
    axs[1].plot(times_in_seconds, humidities, label='Humidity', color='blue')
    axs[1].set_ylabel('Humidity (%)', fontsize=10)
    axs[1].legend(fontsize=8)
    axs[1].text(times_in_seconds[-1], humidities[-1], f'{humidities[-1]:.2f}', ha='right', fontsize=8)

    axs[2].clear()
    axs[2].plot(times_in_seconds, pressures, label='Pressure', color='green')
    axs[2].set_ylabel('Pressure (hPa)', fontsize=10)
    axs[2].legend(fontsize=8)
    axs[2].text(times_in_seconds[-1], pressures[-1], f'{pressures[-1]:.2f}', ha='right', fontsize=8)

    axs[3].clear()
    axs[3].plot(times_in_seconds, magnetometer_data, label='Magnetometer', color='purple')
    axs[3].set_ylabel('Magnetometer (°)', fontsize=10)
    axs[3].legend(fontsize=8)
    axs[3].text(times_in_seconds[-1], magnetometer_data[-1], f'{magnetometer_data[-1]:.2f}', ha='right', fontsize=8)

    # Set common x-axis label for all subplots.
    plt.xlabel('Time (seconds)', fontsize=10)
    # Adjust subplot parameters for a tight layout.
    plt.tight_layout()

# --- Main Program Execution ---
try:
    # Connect to the MQTT broker.
    # Although connected, this script does not actively publish or subscribe data in the main loop.
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # Start the MQTT network loop in a separate thread.
    client.loop_start()    
      
       
    # Create the animation.
    # FuncAnimation calls update_plot every 'interval' milliseconds (1000ms = 1 second).
    ani = FuncAnimation(fig, update_plot, interval=1000)

    # Display the Matplotlib plot. This call blocks until the plot window is closed.
    plt.show()

except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to gracefully exit the program.
    print("Exiting program.")
finally:
    # Stop the MQTT network loop and disconnect from the broker.
    client.loop_stop()
    client.disconnect()






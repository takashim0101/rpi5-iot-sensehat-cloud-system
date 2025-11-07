from sense_hat import SenseHat
from time import sleep
import sys

# Print default encoding and filesystem encoding for debugging purposes.
# This helps in understanding how strings are handled in the environment.
print(sys.getdefaultencoding())
print(sys.getfilesystemencoding())

# Create an instance of Sense HAT.
# This object provides access to the Sense HAT's sensors and LED display.
sense = SenseHat()
# Clear the LED display, turning all pixels off.
sense.clear()

# Initialize a counter for the trial number.
# This number will be incremented with each cycle of sensor readings.
trial_number = 1

def display_Barometric_pressure(trial):
    """
    Reads the barometric pressure from the Sense HAT and displays it.
    The reading is shown on the Sense HAT's LED display and printed to the console.
    :param trial: The current trial number to be displayed with the reading.
    """
    # Get barometric pressure in millibars (mb).
    barometric_pressure = sense.get_pressure()
    # Format the pressure reading with the trial number for display.
    barometric_pressure_str = f"Trial {trial}: Barometric Pressure: {barometric_pressure:.2f} mb"
    # Display the message on the Sense HAT LED matrix.
    # The message scrolls horizontally with a green text color.
    sense.show_message(barometric_pressure_str, scroll_speed=0.07, text_colour=[0, 255, 0])  # Green
    # Print the message to the console.
    print(barometric_pressure_str)
    # Pause for 1 second before proceeding.
    sleep(1)

def display_humidity(trial):
    """
    Reads the humidity from the Sense HAT and displays it.
    The reading is shown on the Sense HAT's LED display and printed to the console.
    :param trial: The current trial number to be displayed with the reading.
    """
    # Get humidity as a percentage.
    humidity = sense.get_humidity()
    # Format the humidity reading with the trial number for display.
    humidity_str = f"Trial {trial}: Humidity: {humidity:.2f} %"
    # Display the message on the Sense HAT LED matrix.
    # The message scrolls horizontally with a blue text color.
    sense.show_message(humidity_str, scroll_speed=0.07, text_colour=[0, 0, 255])  # Blue
    # Print the message to the console.
    print(humidity_str)
    # Pause for 1 second before proceeding.
    sleep(1)

def display_temperature(trial):
    """
    Reads the temperature from the Sense HAT and displays it.
    The reading is shown on the Sense HAT's LED display and printed to the console.
    The temperature is an average of readings from humidity and pressure sensors.
    :param trial: The current trial number to be displayed with the reading.
    """
    # Get temperature from the humidity sensor.
    htemp = sense.get_temperature()
    # Get temperature from the pressure sensor.
    ptemp = sense.get_temperature_from_pressure()
    # Calculate the average temperature from both sensors.
    temp = (htemp + ptemp) / 2
    # Format the temperature reading with the trial number for display.
    temp_str = f"Trial {trial}: temperature: {temp:.2f} degree Celsius"

    # Display the message on the Sense HAT LED matrix.
    # The message scrolls horizontally with a red text color.
    sense.show_message(temp_str, scroll_speed=0.07, text_colour=[255, 0, 0])  # Red
    # Print the message to the console.
    print(temp_str)
    # Pause for 1 second before proceeding.
    sleep(1)

def display_magnetometer(trial):
    """
    Reads the magnetometer (compass) data from the Sense HAT and displays it.
    The reading represents the direction in degrees.
    The reading is shown on the Sense HAT's LED display and printed to the console.
    :param trial: The current trial number to be displayed with the reading.
    """
    # Get magnetometer data, which provides the compass heading in degrees.
    magnetometer = sense.get_compass()
    # Format the magnetometer reading with the trial number for display.
    magnetometer_str = f"Trial {trial}: Magnetometer: {magnetometer:.2f} degrees"
    # Display the message on the Sense HAT LED matrix.
    # The message scrolls horizontally with an orange text color.
    sense.show_message(magnetometer_str, scroll_speed=0.07, text_colour=[255, 165, 0])  # Orange
    # Print the message to the console.
    print(magnetometer_str)
    # Pause for 1 second before proceeding.
    sleep(1)

# Main loop to continuously display sensor readings.
# This loop runs indefinitely until the script is manually stopped (e.g., with Ctrl+C).
while True:
    # Call functions to display each sensor reading for the current trial.
    display_Barometric_pressure(trial_number)
    display_humidity(trial_number)
    display_temperature(trial_number)
    display_magnetometer(trial_number)

    # Increment trial number for the next round of readings.
    trial_number += 1

    # Wait for 5 seconds before the next set of readings.
    # This pause controls the frequency of sensor data updates.
    sleep(5) 



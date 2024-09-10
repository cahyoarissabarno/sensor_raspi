import serial
import paho.mqtt.client as mqtt
import mysql.connector
import time
import daemon

# UART configuration
UART_PORT = '/dev/ttyUSB0'  # Update with your UART port
UART_BAUDRATE = 115200        # Update with your baud rate

# MQTT configuration
MQTT_BROKER = "localhost"  # Update with your MQTT broker URL
MQTT_PORT = 1883                 # Update with your MQTT broker port
MQTT_TOPIC = "test/topic"        # Update with your MQTT topic

# MySQL configuration
MYSQL_HOST = "localhost"
MYSQL_USER = "jovial"
MYSQL_PASSWORD = "jovial"  # Update with your MySQL password
MYSQL_DB = "sensor_data"

def uart_read():
    """Read data from UART and return as string."""
    with serial.Serial(UART_PORT, UART_BAUDRATE, timeout=1) as ser:
        # line = ser.readline().decode('utf-8').strip()
        line = ser.readline().decode('utf-8').strip()
        return line

def on_connect(client, userdata, flags, rc):
    """MQTT callback for connection."""
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """MQTT callback for message reception."""
    payload = msg.payload.decode('utf-8')
    print(f"Received `{payload}` from `{msg.topic}` topic")
    store_data_in_db(payload)

def mqtt_setup():
    """Set up MQTT client and return."""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

def store_data_in_db(data):
    """Store sensor data in MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sensor_table (data) VALUES (%s)", (data,))
        conn.commit()
        print(f"Data `{data}` inserted into database")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def run():
    """Main function to read from UART and MQTT, and store data."""
    #client = mqtt_setup()
    #client.loop_start()
    # print(client)
    while True:
         uart_data = uart_read()
         if uart_data:
             print(f"UART Data: {uart_data}")
             store_data_in_db(uart_data)
         time.sleep(1)

def daemonize():
    """Daemonize the process using the python-daemon library."""
    with daemon.DaemonContext():
        run()

if __name__ == "__main__":
    # Uncomment the following line to run as daemon
    # daemonize()
    
    # Comment the following line if using as a daemon
    run()

from flask import Flask, request, jsonify
from flask_cors import CORS
import serial
import mysql.connector
import multiprocessing
import time

app = Flask(__name__)

CORS(app)

# Serial port setup
UART_PORT = '/dev/ttyUSB0'
UART_BAUDRATE = 115200

def send_serial_command(command):
    command2 = command+"\n"
    ser = serial.Serial(UART_PORT, UART_BAUDRATE)
    ser.write(command2.encode())
    print("data terkirim serial")

def read_serial_data():
    with serial.Serial(UART_PORT, UART_BAUDRATE, timeout=3) as ser:
        while True:
            data = ser.readline().decode('utf-8').strip()
            if data:
                print(f"Received data: {data}")
                if data.startswith("{") and data.endswith("}"):
                    # Cek apakah string TIDAK mengandung ":nan"
                    if ":nan" not in data:
                        store_data_in_db(data)
                    else:
                        print("Data Have NaN, Not saved to db")
                else:
                    print("JSON Invalid, Not saved to db")
            time.sleep(1)

def store_data_in_db(data):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="jovial",
            password="jovial",
            database="sensor_data"
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

@app.route('/control', methods=['POST'])
def control():
    data = request.json
    command = data.get('command')
    if command:
        send_serial_command(command)
        print(command)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "No command provided"}), 400

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Start the serial reading in a separate process
    serial_process = multiprocessing.Process(target=read_serial_data)
    serial_process.start()

    # Start Flask app
    run_flask()

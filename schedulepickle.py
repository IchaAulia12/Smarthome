import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
from datetime import datetime
import pickle
import os

# Atur mode pin GPIO
GPIO.setmode(GPIO.BCM)

relay_pins = [20, 21, 16, 12, 13, 6, 26, 19]
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)

schedule_file = "schedule.pkl"

# Fungsi untuk memuat jadwal dari file pickle
def load_schedule():
    if os.path.exists(schedule_file):
        with open(schedule_file, 'rb') as f:
            return pickle.load(f)
    return {}

# Fungsi untuk menyimpan jadwal ke file pickle
def save_schedule(schedule):
    with open(schedule_file, 'wb') as f:
        pickle.dump(schedule, f)

# Muat jadwal saat aplikasi dimulai
schedules = load_schedule()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("Room/jadwal")
    for i in range(8):
        client.subscribe("Room/lamp" + str(i + 1))

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))
    if rc != 0:
        print("Unexpected disconnection, attempting to reconnect")
        reconnect(client)

def reconnect(client):
    while True:
        try:
            client.connect("habibigarden.com", 1883, 60)
            client.loop_start()
            break
        except Exception as e:
            print(f"Reconnection failed: {e}, retrying in 5 seconds")
            time.sleep(5)

def on_message(client, userdata, msg):
    global schedules

    print(msg.topic + " " + str(msg.payload))
    if msg.topic == "Room/jadwal":
        # Parsing pesan jadwal
        schedule_info = str(msg.payload.decode("utf-8"))
        mode = schedule_info[0:2]
        on_time = schedule_info[2:6]
        off_time = schedule_info[6:10]
        relay_states = schedule_info[10:18]
        extra_info = schedule_info[18:]

        # Simpan jadwal ke dalam dictionary
        schedules[msg.topic] = {
            'mode': mode,
            'on_time': on_time,
            'off_time': off_time,
            'relay_states': relay_states,
            'extra_info': extra_info
        }

        # Simpan jadwal ke file pickle
        save_schedule(schedules)
        
        print("Schedule updated and saved.")
    else:
        # Penanganan pesan dari topik "Room/lampX"
        lamp_index = int(msg.topic.split("/")[-1][4:]) - 1
        if msg.payload == b'1':
            GPIO.output(relay_pins[lamp_index], GPIO.HIGH)
            print("Relay " + str(lamp_index + 1) + " ON")
            client.publish("Icha/relay_status", "A")
        elif msg.payload == b'0':
            GPIO.output(relay_pins[lamp_index], GPIO.LOW)
            print("Relay " + str(lamp_index + 1) + " OFF")
            client.publish("Icha/relay_status", "B")

def check_schedule():
    current_time = datetime.now().strftime("%H%M")
    current_day = datetime.now().strftime("%w")
    current_date = datetime.now().strftime("%d%m%Y")
    
    for topic, schedule in schedules.items():
        mode = schedule['mode']
        on_time = schedule['on_time']
        off_time = schedule['off_time']
        relay_states = schedule['relay_states']
        extra_info = schedule['extra_info']

        if mode == "RT":
            daily_schedule = extra_info
            if daily_schedule and daily_schedule[int(current_day) - 1] == current_day:
                if on_time <= current_time < off_time:
                    for i in range(8):
                        if relay_states[i] == "1":
                            GPIO.output(relay_pins[i], GPIO.HIGH)
                        else:
                            GPIO.output(relay_pins[i], GPIO.LOW)
                elif current_time >= off_time:
                    for i in range(8):
                        GPIO.output(relay_pins[i], GPIO.LOW)
        elif mode == "OT":
            schedule_date = extra_info
            if schedule_date == current_date:
                if on_time <= current_time < off_time:
                    for i in range(8):
                        if relay_states[i] == "1":
                            GPIO.output(relay_pins[i], GPIO.HIGH)
                        else:
                            GPIO.output(relay_pins[i], GPIO.LOW)
                elif current_time >= off_time:
                    for i in range(8):
                        GPIO.output(relay_pins[i], GPIO.LOW)

try:
    # Inisialisasi client MQTT
    client = mqtt.Client()

    # Mengatur fungsi callback
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Menghubungkan client ke broker MQTT
    reconnect(client)

    while True:
        check_schedule()
        time.sleep(60)  # Cek jadwal setiap 60 detik

except KeyboardInterrupt:
    print("Program terminated by user.")

finally:
    # Cleanup GPIO ketika program berhenti
    GPIO.cleanup()
    client.loop_stop()

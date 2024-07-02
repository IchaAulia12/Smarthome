import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
from datetime import datetime

# Atur mode pin GPIO
GPIO.setmode(GPIO.BCM)

# Atur pin relay
relay_pins = [20, 21, 16, 12, 13, 6, 26, 19]
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)

# Fungsi callback ketika koneksi ke broker berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe ke topik untuk setiap lampu dan penjadwalan
    client.subscribe("Room/jadwal")

# Fungsi callback ketika pesan diterima dari broker
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "Room/jadwal":
        # Parsing pesan jadwal
        schedule_info = str(msg.payload.decode("utf-8"))
        mode = schedule_info[0:2]
        on_time = schedule_info[2:6]
        off_time = schedule_info[6:10]
        relay_states = schedule_info[10:18]
        daily_schedule = schedule_info[18:]
        current_day = datetime.now().strftime("%w")
        current_time = datetime.now().strftime("%H%M")
        print(mode)
        print(on_time)
        print(off_time)
        print(relay_states)
        print(daily_schedule)
        print(current_day)
        print(current_time)
        print(daily_schedule[int(current_day)-1])
        # Hanya proses jika mode adalah RT
        if mode == "RT" and daily_schedule[int(current_day)-1] == current_day:
            print(int(current_day))
            if on_time <= current_time < off_time:
                for i in range(8):
                    if relay_states[i] == "1":
                        GPIO.output(relay_pins[i], GPIO.HIGH)
                    if relay_states[i] == "0":
                        GPIO.output(relay_pins[i], GPIO.LOW)
            elif current_time >= off_time:
                for i in range(8):
                    if relay_states[i] == "1":
                        GPIO.output(relay_pins[i], GPIO.LOW)
            else:
                GPIO.output(relay_pins[0:], GPIO.LOW)

# Inisialisasi client MQTT
client = mqtt.Client()

# Mengatur fungsi callback
client.on_connect = on_connect
client.on_message = on_message

# Menghubungkan client ke broker MQTT
client.connect("habibigarden.com", 1883, 60)

# Loop utama
client.loop_forever()

# Cleanup GPIO ketika program berhenti
GPIO.cleanup()

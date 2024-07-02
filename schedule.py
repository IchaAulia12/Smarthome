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
        while True:  # Loop utama untuk terus menunggu pesan baru
            # Parsing pesan jadwal
            schedule_info = str(msg.payload.decode("utf-8"))
            mode = schedule_info[0:2]
            on_time = schedule_info[2:6]
            off_time = schedule_info[6:10]
            relay_states = schedule_info[10:18]
            schedule_date = schedule_info[18:]

            print(mode)
            print(on_time)
            print(off_time)
            print(relay_states)
            print(schedule_date)

            # Ambil waktu saat ini
            current_time = datetime.now().strftime("%H%M")
            print(current_time)

            # Periksa apakah penjadwalan aktif dan sesuai dengan tanggal saat ini
            if mode == "OT" and schedule_date == datetime.now().strftime("%d%m%Y"):
                # Periksa apakah saatnya relay harus dihidupkan atau dimatikan
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
            time.sleep(20)  # Tunggu 60 detik sebelum memeriksa lagi

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

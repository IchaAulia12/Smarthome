import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

# Atur mode pin GPIO
GPIO.setmode(GPIO.BCM)

# Atur pin relay (misalnya, pin 21)
relay_pin = 21
GPIO.setup(relay_pin, GPIO.OUT)

# Fungsi callback ketika koneksi ke broker berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe ke topik yang diinginkan
    client.subscribe("Icha/1")

# Fungsi callback ketika pesan diterima dari broker
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # Jika pesan adalah "1", hidupkan relay
    if msg.payload == b'1':
        GPIO.output(relay_pin, GPIO.HIGH)
        print("Relay ON")
    # Jika pesan adalah "0", matikan relay
    elif msg.payload == b'0':
        GPIO.output(relay_pin, GPIO.LOW)
        print("Relay OFF")

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

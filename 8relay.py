import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

# Atur mode pin GPIO
GPIO.setmode(GPIO.BCM)

# Atur pin relay
relay_pins = [20, 21, 16, 12, 13, 6, 26, 19]
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)

# Fungsi callback ketika koneksi ke broker berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe ke topik untuk setiap lampu
    client.subscribe("Room/lamp_schedule")
    for i in range(8):
        client.subscribe("Room/lamp" + str(i + 1))

# Fungsi callback ketika pesan diterima dari broker
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # Pisahkan 'lamp' dari angka yang menyusul
    lamp_index = int(msg.topic.split("/")[-1][4:]) - 1
    # Hidupkan atau matikan relay sesuai dengan pesan yang diterima
    if msg.payload == b'1':
        GPIO.output(relay_pins[lamp_index], GPIO.HIGH)
        print("Relay "+ str(lamp_index + 1) +" ON")
        # Kirim nilai E ke MQTT saat relay hidup
        client.publish("Icha/relay_status", "A")
    elif msg.payload == b'0':
        GPIO.output(relay_pins[lamp_index], GPIO.LOW)
        print("Relay "+ str(lamp_index + 1) +" OFF")
        # Kirim nilai E ke MQTT saat relay mati
        client.publish("Icha/relay_status", "B")

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

import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
from datetime import datetime

# Atur mode pin GPIO
GPIO.setmode(GPIO.BCM)

relay_pins = [20, 21, 16, 12, 13, 6, 26, 19]
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe ke topik untuk setiap lampu dan penjadwalan
    client.subscribe("Room/jadwal")
    for i in range(8):
        client.subscribe("Room/lamp" + str(i + 1))
        
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "Room/jadwal":
        while True:
            # Parsing pesan jadwal
            schedule_info = str(msg.payload.decode("utf-8"))
            mode = schedule_info[0:2]
            on_time = schedule_info[2:6]
            off_time = schedule_info[6:10]
            relay_states = schedule_info[10:18]
            schedule_date = schedule_info[18:]
            current_time = datetime.now().strftime("%H%M")
            current_day = datetime.now().strftime("%w")
            
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
                        if relay_states[i] == "0":
                            GPIO.output(relay_pins[i], GPIO.LOW)
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
                        if relay_states[i] == "0":
                            GPIO.output(relay_pins[i], GPIO.LOW)
                time.sleep(60)  # Tunggu 60 detik sebelum memeriksa lagi
    else:
        while True:
            lamp_index = int(msg.topic.split("/")[-1][4:]) - 1
            
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
            
            time.sleep(60)  # Tunggu 60 detik sebelum memeriksa lagi

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

            
            
            
            
                
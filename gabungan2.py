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
            current_time = datetime.now().strftime("%H%M")
            print(mode)
            print(on_time)
            print(off_time)
            print(relay_states)
            #print(schedule_date)
            
            if mode == "RT":
                daily_schedule = schedule_info[18:]  # Mengatur daily_schedule jika mode adalah "RT"
                current_day = datetime.now().strftime("%w")
                #while True:
                if daily_schedule[int(current_day)-1] == current_day:
                    if on_time <= current_time < off_time:
                        for i in range(8):
                            if relay_states[i] == "1":
                                GPIO.output(relay_pins[i], GPIO.HIGH)
                            else:
                                GPIO.output(relay_pins[i], GPIO.LOW)
                    elif current_time >= off_time:
                        for i in range(8):
                            GPIO.output(relay_pins[i], GPIO.LOW)
                    time.sleep(60)  # Tunggu 60 detik sebelum memeriksa lagi
            elif mode == "OT":
                schedule_date = schedule_info[18:]  # Mengatur schedule_date jika mode adalah "OT"
                #while True:
                if schedule_date == datetime.now().strftime("%d%m%Y"):
                    if on_time <= current_time < off_time:
                        for i in range(8):
                            if relay_states[i] == "1":
                                GPIO.output(relay_pins[i], GPIO.HIGH)
                            else:
                                GPIO.output(relay_pins[i], GPIO.LOW)
                    elif current_time >= off_time:
                        for i in range(8):
                            GPIO.output(relay_pins[i], GPIO.LOW)
                time.sleep(10)  # Tunggu 60 detik sebelum memeriksa lagi
    else:
        # Penanganan pesan dari topik "Room/lampX"
        #while True:
            lamp_index = int(msg.topic.split("/")[-1][4:]) - 1
            if msg.payload == b'1':
                GPIO.output(relay_pins[lamp_index], GPIO.HIGH)
                print("Relay "+ str(lamp_index + 1) +" ON")
                client.publish("Icha/relay_status", "A")
            elif msg.payload == b'0':
                GPIO.output(relay_pins[lamp_index], GPIO.LOW)
                print("Relay "+ str(lamp_index + 1) +" OFF")
                client.publish("Icha/relay_status", "B")
            #time.sleep(60)  # Tunggu 60 detik sebelum memeriksa lagi

try:
    # Inisialisasi client MQTT
    client = mqtt.Client()

    # Mengatur fungsi callback
    client.on_connect = on_connect
    client.on_message = on_message

    # Menghubungkan client ke broker MQTT
    client.connect("habibigarden.com", 1883, 60)

    # Loop utama
    client.loop_forever()

except KeyboardInterrupt:
    print("Program terminated by user.")

finally:
    # Cleanup GPIO ketika program berhenti
    GPIO.cleanup()

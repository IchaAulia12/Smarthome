import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
from datetime import datetime
import pickle
import os

# Atur mode pin GPIO
GPIO.setmode(GPIO.BCM)

# Atur pin relay
relay_pins = [20, 21, 16, 5, 13, 6, 26, 19]
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)

# Nama file pickle untuk menyimpan jadwal mode RT
pickle_file_RT = "schedule_RT.pkl"
# Nama file pickle untuk menyimpan jadwal mode OT
pickle_file_OT = "schedule_OT.pkl"

# Fungsi untuk menyimpan jadwal ke file pickle untuk mode RT
def save_schedule_RT(schedule):
    with open(pickle_file_RT, 'wb') as file:
        pickle.dump(schedule, file)
    print("Jadwal Mode RT disimpan:", schedule)

# Fungsi untuk memuat jadwal dari file pickle untuk mode RT
def load_schedule_RT():
    if os.path.exists(pickle_file_RT):
        with open(pickle_file_RT, 'rb') as file:
            schedule = pickle.load(file)
            print("Jadwal Mode RT dimuat:", schedule)
            return schedule
    return None

# Fungsi untuk menyimpan jadwal ke file pickle untuk mode OT
def save_schedule_OT(schedule):
    with open(pickle_file_OT, 'wb') as file:
        pickle.dump(schedule, file)
    print("Jadwal Mode OT disimpan:", schedule)

# Fungsi untuk memuat jadwal dari file pickle untuk mode OT
def load_schedule_OT():
    if os.path.exists(pickle_file_OT):
        with open(pickle_file_OT, 'rb') as file:
            schedule = pickle.load(file)
            print("Jadwal Mode OT dimuat:", schedule)
            return schedule
    return None

# Fungsi callback ketika koneksi ke broker berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribe ke topik untuk setiap lampu dan penjadwalan
    client.subscribe("Room/jadwal")

# Fungsi callback ketika pesan diterima dari broker
def on_message(client, userdata, msg):
    global schedule_RT, schedule_OT
    print(msg.topic + " " + str(msg.payload))
    if msg.topic == "Room/jadwal":
        # Parsing pesan jadwal
        schedule_info = str(msg.payload.decode("utf-8"))
        mode = schedule_info[0:2]
        on_time = schedule_info[2:6]
        off_time = schedule_info[6:10]
        relay_states = schedule_info[10:18]
        schedule_date = schedule_info[18:]

        print("Pesan diterima:", schedule_info)
        print("Mode:", mode)
        print("Waktu ON:", on_time)
        print("Waktu OFF:", off_time)
        print("Relay States:", relay_states)
        print("Tanggal Jadwal:", schedule_date)

        if mode == "OT":
            schedule_OT = {
                'mode': mode,
                'on_time': on_time,
                'off_time': off_time,
                'relay_states': relay_states,
                'schedule_date': schedule_date
            }
            # Simpan jadwal mode OT ke file pickle
            save_schedule_OT(schedule_OT)
        elif mode == "RT":
            schedule_RT = {
                'mode': mode,
                'on_time': on_time,
                'off_time': off_time,
                'relay_states': relay_states,
                'schedule_date': schedule_date
            }
            # Simpan jadwal mode RT ke file pickle
            save_schedule_RT(schedule_RT)

# Fungsi untuk mengatur relay sesuai dengan jadwal
def apply_schedule(schedule):
    mode = schedule['mode']
    on_time = schedule['on_time']
    off_time = schedule['off_time']
    relay_states = schedule['relay_states']
    schedule_date = schedule['schedule_date']

    # Ambil waktu saat ini
    current_time = datetime.now().strftime("%H%M")
    current_day = datetime.now().strftime("%w")
    print("Waktu Saat Ini:", current_time)

    # Periksa apakah penjadwalan aktif dan sesuai dengan tanggal saat ini
    if mode == "OT" and schedule_date == datetime.now().strftime("%d%m%Y"):
        # Periksa apakah saatnya relay harus dihidupkan atau dimatikan
        if on_time <= current_time < off_time:
            print("Waktu untuk menyalakan relay (Mode OT)")
            for i in range(8):
                if relay_states[i] == "1":
                    GPIO.output(relay_pins[i], GPIO.HIGH)
                if relay_states[i] == "0":
                    GPIO.output(relay_pins[i], GPIO.LOW)
        elif current_time >= off_time:
            print("Waktu untuk mematikan relay (Mode OT)")
            for i in range(8):
                if relay_states[i] == "1":
                    GPIO.output(relay_pins[i], GPIO.LOW)
        else:
            print("Di luar waktu penjadwalan")
            GPIO.output(relay_pins[0:], GPIO.LOW)
    elif mode == "RT" and schedule_date[int(current_day)-1] == current_day:
        # Periksa apakah saatnya relay harus dihidupkan atau dimatikan
        if on_time <= current_time < off_time:
            print("Waktu untuk menyalakan relay (Mode RT)")
            for i in range(8):
                if relay_states[i] == "1":
                    GPIO.output(relay_pins[i], GPIO.HIGH)
                if relay_states[i] == "0":
                    GPIO.output(relay_pins[i], GPIO.LOW)
        elif current_time >= off_time:
            print("Waktu untuk mematikan relay (Mode RT)")
            for i in range(8):
                if relay_states[i] == "1":
                    GPIO.output(relay_pins[i], GPIO.LOW)
        else:
            print("Di luar waktu penjadwalan (Mode RT)")
            GPIO.output(relay_pins[0:], GPIO.LOW)
    else:
        print("Jadwal tidak aktif atau tidak sesuai tanggal")

# Inisialisasi client MQTT
client = mqtt.Client()

# Mengatur fungsi callback
client.on_connect = on_connect
client.on_message = on_message

# Menghubungkan client ke broker MQTT
client.connect("habibigarden.com", 1883, 60)

# Muat jadwal mode RT dari file pickle jika ada
schedule_RT = load_schedule_RT()

# Muat jadwal mode OT dari file pickle jika ada
schedule_OT = load_schedule_OT()

# Loop utama untuk menerapkan jadwal yang ada dan memeriksa pesan baru
while True:
    client.loop(timeout=1.0)  # Menggunakan loop dengan timeout untuk memeriksa pesan MQTT

    # Periksa dan terapkan jadwal mode RT jika tersedia
    if schedule_RT:
        apply_schedule(schedule_RT)

    # Periksa dan terapkan jadwal mode OT jika tersedia
    if schedule_OT:
        apply_schedule(schedule_OT)

    time.sleep(20)
    # Tunggu 20 detik sebelum memeriksa lagi
    
GPIO.cleanup()
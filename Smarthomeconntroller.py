import tkinter as tk
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import pickle
import os
from datetime import datetime
import time

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)
relay_pins = [20, 21, 16, 5, 13, 6, 26, 19]

# Setel semua pin relay sebagai output dan atur ke LOW (matikan relay)
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Fungsi untuk mengubah status relay
def toggle_relay(pin):
    if GPIO.input(pin) == GPIO.LOW:
        GPIO.output(pin, GPIO.HIGH)
        return "ON"
    else:
        GPIO.output(pin, GPIO.LOW)
        return "OFF"

# Fungsi untuk keluar dan membersihkan GPIO
def on_closing():
    GPIO.cleanup()
    root.destroy()

# Fungsi untuk mengendalikan relay dan mengubah warna tombol
def toggle_button(button, pin):
    global manual_override
    manual_override = True
    new_state = toggle_relay(pin)
    button.config(bg="#1E88E5" if new_state == "ON" else "#90CAF9")

# Fungsi untuk memperbarui tombol berdasarkan status relay
def update_button(button, state):
    button.config(bg="#3F51B5" if state == "ON" else "#90CAF9")

# Fungsi callback ketika koneksi ke broker berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("Room/lamp_schedule")
    for i in range(8):
        client.subscribe("Room/lamp" + str(i + 1))

# Fungsi callback ketika pesan diterima dari broker
def on_message(client, userdata, msg):
    global schedule_RT, schedule_OT, manual_override
    print(msg.topic + " " + str(msg.payload))
    if msg.topic == "Room/lamp_schedule":
        # Parsing pesan jadwal
        schedule_info = str(msg.payload.decode("utf-8"))
        mode = schedule_info[0:2]
        on_time = schedule_info[2:6]
        off_time = schedule_info[6:10]
        relay_states = schedule_info[10:18]
        schedule_date = schedule_info[18:]

        if mode == "OT":
            schedule_OT = {
                'mode': mode,
                'on_time': on_time,
                'off_time': off_time,
                'relay_states': relay_states,
                'schedule_date': schedule_date
            }
            save_schedule_OT(schedule_OT)
        elif mode == "RT":
            schedule_RT = {
                'mode': mode,
                'on_time': on_time,
                'off_time': off_time,
                'relay_states': relay_states,
                'schedule_date': schedule_date
            }
            save_schedule_RT(schedule_RT)
    else:
        lamp_index = int(msg.topic.split("/")[-1][4:]) - 1
        if msg.payload == b'1':
            GPIO.output(relay_pins[lamp_index], GPIO.HIGH)
            client.publish("Icha/relay_status", "A")
            update_button(buttons[lamp_index], "ON")
        elif msg.payload == b'0':
            GPIO.output(relay_pins[lamp_index], GPIO.LOW)
            client.publish("Icha/relay_status", "B")
            update_button(buttons[lamp_index], "OFF")

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
        if on_time <= current_time < off_time:
            for i in range(8):
                GPIO.output(relay_pins[i], GPIO.HIGH if relay_states[i] == "1" else GPIO.LOW)
        elif current_time >= off_time:
            for i in range(8):
                GPIO.output(relay_pins[i], GPIO.LOW)
    elif mode == "RT" and schedule_date[int(current_day)-1] == current_day:
        if on_time <= current_time < off_time:
            for i in range(8):
                GPIO.output(relay_pins[i], GPIO.HIGH if relay_states[i] == "1" else GPIO.LOW)
        elif current_time >= off_time:
            for i in range(8):
                GPIO.output(relay_pins[i], GPIO.LOW)

# Membuat GUI dengan Tkinter
root = tk.Tk()
root.title("8 Relay Control")
root.configure(bg="white")
root.geometry("480x320")

frame = tk.Frame(root, bg="white")
frame.pack(pady=20)

# Tambahkan gambar/logo di atas
try:
    logo_image = Image.open("logo.png")
    logo_image = logo_image.resize((50, 60))
    logo_photo = ImageTk.PhotoImage(logo_image)
    label_logo = tk.Label(frame, image=logo_photo, borderwidth=0, bg="white")
    label_logo.image = logo_photo
    label_logo.grid(row=0, column=0, columnspan=1, padx=5, pady=5)
except Exception as e:
    print(f"Error loading logo image: {e}")

# Tambahkan label untuk menampilkan informasi suhu di sebelah kanan atas
label_temp = tk.Label(frame, text="Suhu Ruangan: 25°C", font=("Montserrat", 10), bg="white", fg="#3F51B5")
label_temp.grid(row=0, column=2, columnspan=2, padx=5, pady=15)

# Memuat gambar untuk tombol-tombol
button_images = []
for i in range(8):
    try:
        img = Image.open(f"button_image{i+1}.png")
        img = img.resize((50, 50))
        img = ImageTk.PhotoImage(img)
        button_images.append(img)
    except Exception as e:
        print(f"Error loading image {i+1}: {e}")
        button_images.append(None)

# Membuat tombol untuk setiap relay (dengan gambar)
buttons = []
for i in range(2):
    for j in range(4):
        pin = i * 4 + j
        img = button_images[pin]
        if img:
            btn = tk.Button(frame, image=img, bg="#90CAF9", width=60, height=60, borderwidth=0)
        else:
            btn = tk.Button(frame, text=f"Relay {pin+1}", bg="red", width=8, height=4, borderwidth=0)
        btn.grid(row=i+1, column=j, padx=5, pady=5)
        btn.config(command=lambda b=btn, p=relay_pins[pin]: toggle_button(b, p))
        buttons.append(btn)

# Event handler saat window ditutup
root.protocol("WM_DELETE_WINDOW", on_closing)

# Inisialisasi client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("habibigarden.com", 1883, 60)

# Muat jadwal mode RT dan OT dari file pickle jika ada
pickle_file_RT = "schedule_RT.pkl"
pickle_file_OT = "schedule_OT.pkl"
schedule_RT = load_schedule_RT()
schedule_OT = load_schedule_OT()

# Global flag for manual override
manual_override = False

# Loop utama untuk MQTT dan Tkinter
def mqtt_loop():
    client.loop_start()

def schedule_loop():
    global manual_override
    if not manual_override:
        if schedule_RT:
            apply_schedule(schedule_RT)
        if schedule_OT:
            apply_schedule(schedule_OT)
    else:
        manual_override = False  # Reset manual override after one cycle
    root.after(20000, schedule_loop)  # Periksa jadwal setiap 20 detik

root.after(100, mqtt_loop)
root.after(20000, schedule_loop)
root.mainloop()

# Cleanup GPIO ketika program berhenti
GPIO.cleanup()

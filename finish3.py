import tkinter as tk
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import pickle
import os

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)
relay_pins = [20, 21, 16, 5, 13, 6, 26, 19]

# Setel semua pin relay sebagai output dan atur ke LOW (matikan relay)
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Nama file pickle untuk menyimpan jadwal mode RT
pickle_file_RT = "schedule_RT.pkl"
# Nama file pickle untuk menyimpan jadwal mode OT
pickle_file_OT = "schedule_OT.pkl"

# Fungsi untuk menyimpan jadwal ke file pickle untuk mode RT
def save_schedule_RT(schedule):
    with open(pickle_file_RT, 'wb') as file:
        pickle.dump(schedule, file)
    print("Jadwal Mode RT disimpan:", schedule)
    # Kirim jadwal ke MQTT
    client.publish("Room/saved_schedule_RT", str(schedule))

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
    # Kirim jadwal ke MQTT
    client.publish("Room/saved_schedule_OT", str(schedule))

# Fungsi untuk memuat jadwal dari file pickle untuk mode OT
def load_schedule_OT():
    if os.path.exists(pickle_file_OT):
        with open(pickle_file_OT, 'rb') as file:
            schedule = pickle.load(file)
            print("Jadwal Mode OT dimuat:", schedule)
            return schedule
    return None

# Fungsi untuk mengubah status relay
def toggle_relay(pin, manual=True):
    if not schedule_enabled or not manual:  # Hanya jika penjadwalan dinonaktifkan atau jika dipanggil dari penjadwalan
        if GPIO.input(pin) == GPIO.LOW:
            GPIO.output(pin, GPIO.HIGH)
            client.publish(f"Room/lamp{relay_pins.index(pin) + 1}", '1')  # Kirim status relay ON ke MQTT
            return "ON"
        else:
            GPIO.output(pin, GPIO.LOW)
            client.publish(f"Room/lamp{relay_pins.index(pin) + 1}", '0')  # Kirim status relay OFF ke MQTT
            return "OFF"

# Fungsi untuk keluar dan membersihkan GPIO
def on_closing():
    GPIO.cleanup()
    root.destroy()

# Fungsi untuk mengendalikan relay dan mengubah warna tombol
def toggle_button(button, pin):
    if not schedule_enabled:  # Hanya jika penjadwalan dinonaktifkan
        new_state = toggle_relay(pin)
        button.config(bg="#1E88E5" if new_state == "ON" else "#90CAF9")

# Fungsi untuk memperbarui tombol berdasarkan status relay
def update_button(button, state):
    button.config(bg="#3F51B5" if state == "ON" else "red")

# Fungsi callback ketika koneksi ke broker berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe ke topik untuk setiap lampu dan penjadwalan
    client.subscribe("Room/lamp_schedule")
    for i in range(8):
        client.subscribe("Room/lamp" + str(i + 1))
    client.subscribe("Room/jadwal")
    client.subscribe("Room/schedule_status")

# Fungsi callback ketika pesan diterima dari broker
def on_message(client, userdata, msg):
    global schedule_RT, schedule_OT, schedule_enabled
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
    elif msg.topic == "Room/schedule_status":
        schedule_status = str(msg.payload.decode("utf-8"))
        if schedule_status == "ON":
            schedule_enabled = True
        elif schedule_status == "OFF":
            schedule_enabled = False
        schedule_button.config(text="Schedule ON" if schedule_enabled else "Schedule OFF")
    else:
        if not schedule_enabled:
            lamp_index = int(msg.topic.split("/")[-1][4:]) - 1
            # Hidupkan atau matikan relay sesuai dengan pesan yang diterima
            if msg.payload == b'1':
                GPIO.output(relay_pins[lamp_index], GPIO.HIGH)
                print("Relay " + str(lamp_index + 1) + " ON")
                client.publish("Icha/relay_status", "A")
                update_button(buttons[lamp_index], "ON")
            elif msg.payload == b'0':
                GPIO.output(relay_pins[lamp_index], GPIO.LOW)
                print("Relay " + str(lamp_index + 1) + " OFF")
                client.publish("Icha/relay_status", "B")
                update_button(buttons[lamp_index], "OFF")

# Fungsi untuk menggabungkan jadwal OT dan RT dan menentukan status relay
def apply_combined_schedule(schedule_RT, schedule_OT):
    current_time = datetime.now().strftime("%H%M")
    current_date = datetime.now().strftime("%d%m%Y")
    current_day = datetime.now().strftime("%w")

    relay_status = [GPIO.LOW] * 8

    # Mode OT
    if schedule_OT and schedule_OT['schedule_date'] == current_date:
        on_time_OT = schedule_OT['on_time']
        off_time_OT = schedule_OT['off_time']
        relay_states_OT = schedule_OT['relay_states']
        
        if on_time_OT <= current_time < off_time_OT:
            for i in range(8):
                if relay_states_OT[i] == "1":
                    relay_status[i] = GPIO.HIGH
                else:
                    relay_status[i] = GPIO.LOW

    # Mode RT
    if schedule_RT and schedule_RT['schedule_date'][int(current_day)-1] == current_day:
        on_time_RT = schedule_RT['on_time']
        off_time_RT = schedule_RT['off_time']
        relay_states_RT = schedule_RT['relay_states']
        
        if on_time_RT <= current_time < off_time_RT:
            for i in range(8):
                if relay_states_RT[i] == "1":
                    relay_status[i] = GPIO.HIGH

    for i in range(8):
        GPIO.output(relay_pins[i], relay_status[i])
        update_button(buttons[i], "ON" if relay_status[i] == GPIO.HIGH else "OFF")
        client.publish(f"Room/lamp{i+1}", '1' if relay_status[i] == GPIO.HIGH else '0')

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

# Tombol untuk mengaktifkan dan menonaktifkan mode penjadwalan
schedule_enabled = False

def toggle_schedule():
    global schedule_enabled
    schedule_enabled = not schedule_enabled
    schedule_button.config(text="Schedule ON", bg="#90CAF9" if schedule_enabled else "Schedule OFF", bg="red")
    client.publish("Room/schedule_status", "ON" if schedule_enabled else "OFF")

schedule_button = tk.Button(frame, text="Schedule OFF", bg="#90CAF9", width=15, height=2, borderwidth=0, command=toggle_schedule)
schedule_button.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

# Event handler saat window ditutup
root.protocol("WM_DELETE_WINDOW", on_closing)

# Inisialisasi client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.mqtt.cool", 1883, 60)

# Muat jadwal mode RT dan OT dari file pickle jika ada
schedule_RT = load_schedule_RT()
schedule_OT = load_schedule_OT()

# Loop utama untuk MQTT dan Tkinter
def mqtt_loop():
    client.loop_start()

def schedule_loop():
    if schedule_enabled:
        apply_combined_schedule(schedule_RT, schedule_OT)
    root.after(10000, schedule_loop)  # Periksa setiap 10 detik

root.after(100, mqtt_loop)
root.after(10000, schedule_loop)
root.mainloop()

# Cleanup GPIO ketika program berhenti
GPIO.cleanup()

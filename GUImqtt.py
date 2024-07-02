from PIL import Image, ImageTk
import tkinter as tk
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

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
    new_state = toggle_relay(pin)
    button.config(bg="#1E88E5" if new_state == "ON" else "#90CAF9")

# Fungsi untuk memperbarui tombol berdasarkan status relay
def update_button(button, state):
    button.config(bg="#3F51B5" if state == "ON" else "red")

# Fungsi callback ketika koneksi ke broker berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe ke topik untuk setiap lampu
    client.subscribe("Room/lamp_schedule")
    for i in range(8):
        client.subscribe("Room/lamp" + str(i + 1))

# Fungsi callback ketika pesan diterima dari broker
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
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

# Inisialisasi client MQT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("habibigarden.com", 1883, 60)

# Loop utama untuk MQTT dan Tkinter
def mqtt_loop():
    client.loop_start()

root.after(100, mqtt_loop)
root.mainloop()

# Cleanup GPIO ketika program berhenti
GPIO.cleanup()

import tkinter as tk
from tkinter import messagebox
import RPi.GPIO as GPIO

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)  # Gunakan penomoran BCM
relay_pins = [20, 21, 16, 12, 13, 6, 26, 19]

# Setel semua pin relay sebagai output dan atur ke LOW (matikan relay)
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Fungsi untuk mengubah status relay
def toggle_relay(button, pin):
    if GPIO.input(pin) == GPIO.LOW:
        GPIO.output(pin, GPIO.HIGH)
        button.config(text=f"Relay {pin} ON", bg="green")
        messagebox.showinfo("Status", f"Relay on pin {pin} is ON")
    else:
        GPIO.output(pin, GPIO.LOW)
        button.config(text=f"Relay {pin} OFF", bg="red")
        messagebox.showinfo("Status", f"Relay on pin {pin} is OFF")

# Fungsi untuk keluar dan membersihkan GPIO
def on_closing():
    GPIO.cleanup()
    root.destroy()

# Membuat GUI dengan Tkinter
root = tk.Tk()
root.title("8 Relay Control")

frame = tk.Frame(root)
frame.pack(pady=20)

# Membuat tombol untuk setiap relay
buttons = []
for pin in relay_pins:
    btn = tk.Button(frame, text=f"Relay {pin} OFF", bg="red", width=20)
    btn.config(command=lambda b=btn, p=pin: toggle_relay(b, p))
    btn.pack(pady=5)
    buttons.append(btn)

# Event handler saat window ditutup
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

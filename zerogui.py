import tkinter as tk
from PIL import Image, ImageTk

# Membuat GUI dengan Tkinter
root = tk.Tk()
root.title("8 Button with Images")
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
            btn = tk.Button(frame, text=f"Button {pin+1}", bg="red", width=8, height=4, borderwidth=0)
        btn.grid(row=i+1, column=j, padx=5, pady=5)
        buttons.append(btn)

# Tombol untuk mengaktifkan dan menonaktifkan mode penjadwalan
schedule_enabled = False

def toggle_schedule():
    global schedule_enabled
    schedule_enabled = not schedule_enabled
    schedule_button.config(text="Schedule ON" if schedule_enabled else "Schedule OFF", bg="#90CAF9" if schedule_enabled else "red")

schedule_button = tk.Button(frame, text="Schedule OFF", bg="red", width=15, height=2, borderwidth=0, command=toggle_schedule)
schedule_button.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

root.mainloop()

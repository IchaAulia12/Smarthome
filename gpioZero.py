from PIL import Image, ImageTk
import tkinter as tk

# Fungsi untuk keluar
def on_closing():
    root.destroy()

# Fungsi untuk mengubah status tombol
def toggle_button(button):
    if button["text"] == "ON":
        button.config(text="OFF", bg="#FF5733")
    else:
        button.config(text="ON", bg="#3F51B5")

# Membuat GUI dengan Tkinter
root = tk.Tk()
root.title("8 Relay Control")

# Atur warna latar belakang jendela root menjadi putih
root.configure(bg="white")

# Atur ukuran jendela root
root.geometry("480x320")

frame = tk.Frame(root, bg="white")  # Atur warna latar belakang frame menjadi putih
frame.pack(pady=20)

# Tambahkan gambar/logo di atas
logo_image = Image.open("logo.png")
logo_image = logo_image.resize((50, 60))  # Mengubah ukuran gambar menjadi 100x100 piksel
logo_photo = ImageTk.PhotoImage(logo_image)

# Membuat latar belakang logo menjadi bulat
label_logo = tk.Label(frame, image=logo_photo, borderwidth=0, bg="white")
label_logo.image = logo_photo  # Harus disimpan agar gambar tidak dihapus oleh garbage collector
label_logo.grid(row=0, column=0, columnspan=1, padx=5, pady=5)

# Tambahkan label untuk menampilkan informasi suhu di sebelah kanan atas
label_temp = tk.Label(frame, text="Suhu Ruangan: 25°C", font=("Montserrat", 10), bg="white", fg="#3F51B5")
label_temp.grid(row=0, column=2, columnspan=2, padx=5, pady=15)

# Membuat tombol untuk setiap relay (tanpa koneksi ke GPIO)
buttons = []  # Array untuk menyimpan tombol-tombol
for i in range(2):  # Dua baris tombol
    for j in range(4):  # Empat kolom tombol
        pin = i * 4 + j + 1
        btn = tk.Button(frame, text="OFF", bg="#FF5733", fg="white", width=8, height=4,
                        font=("Arial", 12, "bold"), borderwidth=0)
        btn.grid(row=i+1, column=j, padx=5, pady=5)  # Menyertakan offset baris untuk logo dan suhu
        btn.config(command=lambda b=btn: toggle_button(b))  # Mengatur perintah tombol dengan fungsi lambda
        buttons.append(btn)  # Menambahkan tombol ke array

# Event handler saat window ditutup
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

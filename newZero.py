import requests
from PIL import Image, ImageTk
import tkinter as tk
from io import BytesIO

# Fungsi untuk keluar
def on_closing():
    root.destroy()

# Fungsi untuk mengubah status tombol
def toggle_button(button):
    if button["text"] == "ON":
        button.config(text="OFF", bg="#FF5733")
    else:
        button.config(text="ON", bg="#3F51B5")

# Fungsi untuk mendapatkan data cuaca
def get_weather():
    api_key = "5767733e6c00ae26cb1f93f874be7275"  # Ganti dengan API key Anda yang valid
    city = "Jember"  # Ganti dengan kota Anda
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:  # Periksa status code respons
            main = data["main"]
            temperature = main["temp"]
            weather_description = data["weather"][0]["description"]
            icon_code = data["weather"][0]["icon"]
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
            icon_response = requests.get(icon_url)
            icon_image = Image.open(BytesIO(icon_response.content))
            icon_photo = ImageTk.PhotoImage(icon_image)

            weather_info = {
                "temperature": f"{temperature}°C",
                "description": weather_description.capitalize(),
                "icon": icon_photo
            }
        else:
            weather_info = {"error": data.get("message", "City Not Found")}
    except Exception as e:
        weather_info = {"error": "Error retrieving weather data"}
        print(e)

    return weather_info

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

# Mendapatkan informasi cuaca
weather_info = get_weather()

if "error" in weather_info:
    weather_text = weather_info["error"]
    label_weather = tk.Label(frame, text=f"Cuaca: {weather_text}", font=("Montserrat", 10), bg="white", fg="#3F51B5")
    label_weather.grid(row=0, column=3, columnspan=1, padx=5, pady=15)
else:
    # Tambahkan ikon cuaca di sebelah informasi cuaca
    label_icon = tk.Label(frame, image=weather_info["icon"], borderwidth=0, bg="white")
    label_icon.image = weather_info["icon"]  # Harus disimpan agar gambar tidak dihapus oleh garbage collector
    label_icon.grid(row=0, column=2, padx=2, pady=2)
    
    # Tambahkan keterangan suhu dan kondisi cuaca di bawah ikon
    weather_text = f"{weather_info['temperature']}\n{weather_info['description']}"
    label_weather = tk.Label(frame, text=weather_text, font=("Montserrat", 10), bg="white", fg="#3F51B5")
    label_weather.grid(row=1, column=2, padx=5, pady=2)

# Tambahkan label untuk menampilkan informasi suhu di sebelah kanan atas
label_temp = tk.Label(frame, text="Suhu Ruangan"+"\n"+"25°C", font=("Montserrat", 10), bg="white", fg="#3F51B5")
label_temp.grid(row=0, column=3, columnspan=2, padx=5, pady=5)

# Membuat tombol untuk setiap relay (tanpa koneksi ke GPIO)
buttons = []  # Array untuk menyimpan tombol-tombol
for i in range(2):  # Dua baris tombol
    for j in range(4):  # Empat kolom tombol
        pin = i * 4 + j + 1
        btn = tk.Button(frame, text="OFF", bg="#FF5733", fg="white", width=8, height=4,
                        font=("Arial", 12, "bold"), borderwidth=0)
        btn.grid(row=i+2, column=j, padx=5, pady=5)  # Menyertakan offset baris untuk logo dan suhu
        btn.config(command=lambda b=btn: toggle_button(b))  # Mengatur perintah tombol dengan fungsi lambda
        buttons.append(btn)  # Menambahkan tombol ke array

# Event handler saat window ditutup
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

import paho.mqtt.client as mqtt

# Fungsi callback ketika koneksi ke broker berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe ke topik yang diinginkan
    client.subscribe("Icha/1")

# Fungsi callback ketika pesan diterima dari broker
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

# Inisialisasi client MQTT
client = mqtt.Client()

# Mengatur fungsi callback
client.on_connect = on_connect
client.on_message = on_message

# Menghubungkan client ke broker MQTT
client.connect("habibigarden.com", 1883, 60)

# Loop utama
client.loop_forever()

import RPi.GPIO as GPIO
import time

# Atur mode pin GPIO
GPIO.setmode(GPIO.BCM)

# Atur pin relay (misalnya, pin 11)
relay_pin = 21
GPIO.setup(relay_pin, GPIO.OUT)

try:
    while True:
        # Hidupkan relay
        GPIO.output(relay_pin, GPIO.HIGH)
        print("Relay ON")
        time.sleep(1)  # Tunggu 1 detik

        #Matikan relay
        GPIO.output(relay_pin, GPIO.LOW)
        print("Relay OFF")
        time.sleep(1)  # Tunggu 1 detik

except KeyboardInterrupt:
    # Tangkap jika pengguna menekan Ctrl+C
    GPIO.cleanup()  # Bersihkan pin GPIO

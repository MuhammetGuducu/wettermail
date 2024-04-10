"""
This module provides functionality for sending weather reports via email
based on the current weather conditions at a specified location.
"""

import os
import smtplib
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import tkinter as tk
import requests
from cryptography.fernet import Fernet


def conditions(main):
    """Determine clothing suggestions based on weather conditions."""
    if main in ["Rain", "Drizzle", "Thunderstorm"]:
        return "Kopfbedeckung und "
    if main in ["Snow"]:
        return "Handschuhe, Kopfbedeckung und "
    return ""


def clothing(temperature, cold_threshold, warm_threshold):
    """Determine clothing suggestions based on temperature."""
    if temperature > int(warm_threshold):
        return "luftige Kleidung"
    if temperature < int(cold_threshold):
        return "warme Kleidung"
    return "normale Kleidung"


def get_data(api_key, lat, lon, lang):
    """Retrieve weather data from OpenWeatherMap API."""
    request_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&lang={lang}"
    feedback = requests.get(request_url, timeout=10)
    if (
        feedback.status_code == 200
    ):  # If connection is successful, return the collected data
        return feedback.json()
    return None


def send_email(data, sender, receiver, password, cold_threshold, warm_threshold):
    """Send email with weather report."""
    if data:
        region = data["name"]
        description = data["weather"][0]["description"]
        temp = round(data["main"]["temp"] - 273.15)
        main = data["weather"][0]["main"]
        today = datetime.datetime.now().strftime("%d.%m.%y")

        conditions_txt = conditions(main)
        clothing_txt = clothing(temp, cold_threshold, warm_threshold)

        #
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h2>Wetterbericht {region} für den {today}</h2>
                <table>
                    <tr>
                        <th>Beschreibung</th>
                        <td>{description}</td>
                    </tr>
                    <tr>
                        <th>Aktuelle Temperatur</th>
                        <td>{temp}°C</td>
                    </tr>
                    <tr>
                        <th>Empfohlene Kleidung</th>
                        <td>{conditions_txt + clothing_txt}</td>
                    </tr>
                </table>
            </body>
        </html>
        """

        msg = MIMEMultipart("alternative")  # Both Text + HTML content combined
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = f"Wetterbericht für {region} am {today}"
        msg.attach(MIMEText(html_body, "html"))

        try:  # Server connection test, prints clear description of errors
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
        except smtplib.SMTPException as e:
            print(f"Fehler beim Senden der Mail: {e}")


def create_default_config():
    """Create a default configuration file if none is available."""
    config = configparser.ConfigParser()

    config["WEATHER"] = {
        "latitude": "51.4344",
        "longitude": "6.7623",
        "language": "de",
        "cold_threshold": "5",
        "warm_threshold": "20",
    }

    config["EMAIL"] = {
        "sender_email": "sender@gmail.com",
        "encrypted_password": "",
        "receiver_email": "receiver@gmail.com",
    }

    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


def save_config(
    lat, lon, lang, cold_threshold, warm_threshold, sender, receiver, password, key
):
    """
    Save the current configuration to config.ini if user allows it.
    """
    config = configparser.ConfigParser()
    config.read("config.ini")

    config.set("WEATHER", "latitude", lat)
    config.set("WEATHER", "longitude", lon)
    config.set("WEATHER", "language", lang)
    config.set("WEATHER", "cold_threshold", str(cold_threshold))
    config.set("WEATHER", "warm_threshold", str(warm_threshold))
    config.set("EMAIL", "sender_email", sender)
    config.set("EMAIL", "receiver_email", receiver)

    # Encrypted Binary Key from passwordKey.txt saved in "cipher"
    # Password-String into Bytes, encrypts them and decodes back into string
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode()).decode()
    config.set("EMAIL", "encrypted_password", encrypted_password)

    with open("config.ini", "w", encoding="utf-8") as config_data:
        config.write(config_data)


def load_config():
    """Load configuration from a file."""
    config = configparser.ConfigParser()  # used to write/read ini files
    if not os.path.exists("config.ini"):
        create_default_config()
    config.read("config.ini")

    with open("passwordKey.txt", "rb") as password_key:  # rb = read-binary
        key = password_key.read()

    cipher = Fernet(key)
    encrypted_password = config.get("EMAIL", "encrypted_password")
    decrypted_password = (
        cipher.decrypt(
            encrypted_password.encode()
        ).decode()  # string into bytes, decrypt bytes and back into string
        if encrypted_password
        else ""  # return empty string if there is no password
    )

    return {
        "latitude": config.get("WEATHER", "latitude"),
        "longitude": config.get("WEATHER", "longitude"),
        "language": config.get("WEATHER", "language"),
        "cold_threshold": int(config.get("WEATHER", "cold_threshold")),
        "warm_threshold": int(config.get("WEATHER", "warm_threshold")),
        "sender_email": config.get("EMAIL", "sender_email"),
        "receiver_email": config.get("EMAIL", "receiver_email"),
        "decrypted_password": decrypted_password,
    }


def user_input():
    """Capture user input for the application and send the email."""

    def submit_button():
        lat = lat_input.get()
        lon = lon_input.get()
        lang = lang_input.get()
        cold_threshold = cold_threshold_input.get()
        warm_threshold = warm_threshold_input.get()
        sender = sender_input.get()
        receiver = receiver_input.get()
        password = password_input.get()

        if save_config_var.get():
            save_config(
                lat,
                lon,
                lang,
                cold_threshold,
                warm_threshold,
                sender,
                receiver,
                password,
                password_key,
            )

        data = get_data(API_KEY, lat, lon, lang)
        send_email(data, sender, receiver, password, cold_threshold, warm_threshold)
        window.destroy()

    config_values = load_config()

    window = tk.Tk()
    window.title("WetterMail")
    window.geometry("360x230")
    input_width = 35

    # GUI setup code for the user input
    tk.Label(window, text="Breitengrad:").grid(row=1, column=0)
    lat_input = tk.Entry(window, width=input_width)
    lat_input.insert(0, config_values["latitude"])
    lat_input.grid(row=1, column=1)

    tk.Label(window, text="Längengrad:").grid(row=2, column=0)
    lon_input = tk.Entry(window, width=input_width)
    lon_input.insert(0, config_values["longitude"])
    lon_input.grid(row=2, column=1)

    tk.Label(window, text="Sprache (de/en):").grid(row=3, column=0)
    lang_input = tk.Entry(window, width=input_width)
    lang_input.insert(0, config_values["language"])
    lang_input.grid(row=3, column=1)

    tk.Label(window, text="Kälteschwelle:").grid(row=4, column=0)
    cold_threshold_input = tk.Entry(window, width=input_width)
    cold_threshold_input.insert(0, config_values["cold_threshold"])
    cold_threshold_input.grid(row=4, column=1)

    tk.Label(window, text="Wärmeschwelle:").grid(row=5, column=0)
    warm_threshold_input = tk.Entry(window, width=input_width)
    warm_threshold_input.insert(0, config_values["warm_threshold"])
    warm_threshold_input.grid(row=5, column=1)

    tk.Label(window, text="Absender E-Mail:").grid(row=6, column=0)
    sender_input = tk.Entry(window, width=input_width)
    sender_input.insert(0, config_values["sender_email"])
    sender_input.grid(row=6, column=1)

    tk.Label(window, text="Absender Passwort:").grid(row=7, column=0)
    password_input = tk.Entry(window, show="*", width=input_width)
    password_input.insert(0, config_values["decrypted_password"])
    password_input.grid(row=7, column=1)

    tk.Label(window, text="Empfänger E-Mail:").grid(row=8, column=0)
    receiver_input = tk.Entry(window, width=input_width)
    receiver_input.insert(0, config_values["receiver_email"])
    receiver_input.grid(row=8, column=1)

    save_config_var = tk.IntVar()
    save_config_checkbutton = tk.Checkbutton(
        window, text="Eingaben speichern", variable=save_config_var
    )
    save_config_checkbutton.grid(row=9, column=0)

    submit_button = tk.Button(window, text="Senden", command=submit_button)
    submit_button.grid(row=10, column=0, columnspan=2)

    window.mainloop()  # GUI Reacts to user interaction like mouse clicks


if __name__ == "__main__":
    API_KEY = "e055a71967956ab0d652f985f92e79a4"
    try:
        with open("passwordKey.txt", "r", encoding="utf-8") as file:
            password_key = file.read()
            Fernet(
                password_key
            )  # Create Fernet-Object to check if PasswordKey is valid
    except (FileNotFoundError, ValueError):
        password_key = Fernet.generate_key().decode()
        create_default_config()
        print("Ungültiger Fernet Key, alle Konfigurationsdaten wurden zurückgesetzt!")
        with open("passwordKey.txt", "w", encoding="utf-8") as file:
            file.write(password_key)  # if not valid, write a valid passwordKey

    user_input()

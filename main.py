"""
This module allows you to send weather reports via email.
It analyzes weather data to suggest clothes based on the weather conditions.

Functions:
    - conditions: Recommend clothing based on weather conditions.
    - clothing: Recommend clothing based on the temperature.
    - get_data: Collect weather data from OpenWeatherMap API.
    - send_email: Sends an email with the weather report.
    - password_key: Generate or retrieve a Fernet key for passwort encryption.
    - create_default_config: Creates a default config.ini file.
    - save_config: Saves the current configuration to config.ini file.
    - load_config: Loads configuration from the config.ini file.
    - user_input: Takes user input to send the email report.

Example:
    >>> get_data(api_key, '1', '1', 'de')
    >>> send_email(weather_data, 'sender@gmail.com', 'receiver@gmail.com', 'password123', '5', '25')
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
from typing import Optional, Dict, Any


def conditions(main: str) -> str:
    """
    Determine clothing suggestions based on weather conditions.

    :param main: The main weather condition (Rain, Snow etc.).
    :return: A string with recommended clothing based on weather conditions.
    """
    if main in ["Rain", "Drizzle", "Thunderstorm"]:
        return "Kopfbedeckung und "
    if main in ["Snow"]:
        return "Handschuhe, Kopfbedeckung und "
    return ""


def clothing(temperature: int, cold_threshold: str, warm_threshold: str) -> str:
    """
    Determine clothing suggestion based on temperature.

    :param temperature: The current temperature.
    :param cold_threshold: Temperature below when it starts to get cold.
    :param warm_threshold: Temperature above when it starts to get warm.
    :return: A string with recommended clothing based on the temperature.
    """
    if temperature > int(warm_threshold):
        return "luftige Kleidung"
    if temperature < int(cold_threshold):
        return "warme Kleidung"
    return "normale Kleidung"


def get_data(api_key: str, lat: str, lon: str, lang: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve weather data from OpenWeatherMap API.

    :param api_key: API key for accessing OpenWeatherMap data.
    :param lat: Latitude of the location.
    :param lon: Longitude of the location.
    :param lang: Language code for the API results.
    :return: A dictionary containing the API results.
    """
    request_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&lang={lang}"
    feedback = requests.get(request_url, timeout=10)
    if feedback.status_code == 200:
        return feedback.json()
    return None


def send_email(
    data: Dict[str, Any],
    sender: str,
    receiver: str,
    password: str,
    cold_threshold: str,
    warm_threshold: str,
) -> None:
    """
    Sends the email weather report via smtp server.

    :param data: Weather data dictionary containing the email content.
    :param sender: Email address of the sender.
    :param receiver: Email address of receiver.
    :param password: Password for the senders email.
    :param cold_threshold: Temperature below when it starts to get cold.
    :param warm_threshold: Temperature above when it starts to get warm.
    """
    if data:
        region = data["name"]
        description = data["weather"][0]["description"]
        temp = round(data["main"]["temp"] - 273.15)
        main = data["weather"][0]["main"]
        today = datetime.now().strftime("%d.%m.%y")

        conditions_txt = conditions(main)
        clothing_txt = clothing(temp, cold_threshold, warm_threshold)

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

        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = f"Wetterbericht für {region} am {today}"
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
        except smtplib.SMTPException as e:
            print(f"Fehler beim Senden der Mail: {e}")


def password_key() -> bytes:
    """
    Generate or retrieve a valid Fernet key for encrypting email password.

    :return: Returns bytes containing the Fernet key.
    """
    try:
        with open("passwordKey.txt", "r", encoding="utf-8") as file:
            password_key = file.read()
            Fernet(password_key)  # This just checks if the key is valid
            return password_key.encode()  # Return the key as bytes
    except (FileNotFoundError, ValueError):
        password_key = Fernet.generate_key().decode()
        create_default_config()
        print("Ungültiger Fernet Key, alle Konfigurationsdaten wurden zurückgesetzt!")
        with open("passwordKey.txt", "w", encoding="utf-8") as file:
            file.write(password_key)
        return password_key.encode()  # Return the new key as bytes


def create_default_config() -> None:
    """
    Creates a default configuration file if none is available.
    """
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
    lat: str,
    lon: str,
    lang: str,
    cold_threshold: str,
    warm_threshold: str,
    sender: str,
    receiver: str,
    password: str,
    key: bytes,
) -> None:
    """
    Save the current configuration to the config.ini file.

    :param lat: Latitude for weather data.
    :param lon: Longitude for weather data.
    :param lang: Language for weather data.
    :param cold_threshold: Cold temperature for clothing.
    :param warm_threshold: Warm temperature for clothing.
    :param sender: Senders email address.
    :param receiver: Receivers email address.
    :param password: Senders email password.
    :param key: Encryption key for securing senders email passwort.
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

    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode()).decode()
    config.set("EMAIL", "encrypted_password", encrypted_password)

    with open("config.ini", "w", encoding="utf-8") as config_data:
        config.write(config_data)


def load_config() -> Dict[str, Any]:
    """
    Load GUI configuration from the config.ini file.

    :return: A dictionary containing all configuration values, including decrypted passwords.
    """
    config = configparser.ConfigParser()
    if not os.path.exists("config.ini"):
        create_default_config()
    config.read("config.ini")

    with open("passwordKey.txt", "rb") as password_key:
        key = password_key.read()

    cipher = Fernet(key)
    encrypted_password = config.get("EMAIL", "encrypted_password")
    decrypted_password = (
        cipher.decrypt(encrypted_password.encode()).decode()
        if encrypted_password
        else ""
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


def user_input() -> None:
    """
    Capture user input and send the email based on the input and current weather data.

    This function initializes a Tkinter GUI for user inputs and parameters
    and uses these inputs to collect weather data and send an email report.
    """

    def on_submit():
        lat = lat_input.get()
        lon = lon_input.get()
        lang = lang_input.get()
        cold_threshold = cold_threshold_input.get()
        warm_threshold = warm_threshold_input.get()
        sender = sender_input.get()
        receiver = receiver_input.get()
        password = password_input.get()

        key = password_key()
        save_config(
            lat,
            lon,
            lang,
            cold_threshold,
            warm_threshold,
            sender,
            receiver,
            password,
            key,
        )

        data = get_data(API_KEY, lat, lon, lang)
        send_email(data, sender, receiver, password, cold_threshold, warm_threshold)
        window.destroy()

    config_values = load_config()

    window = tk.Tk()
    window.title("WetterMail")
    window.geometry("360x230")
    input_width = 35

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

    submit_button = tk.Button(window, text="Senden", command=on_submit)
    submit_button.grid(row=10, column=0, columnspan=2)

    window.mainloop()


if __name__ == "__main__":
    API_KEY = "e055a71967956ab0d652f985f92e79a4"
    password_key()
    user_input()

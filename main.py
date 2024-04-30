"""
Weather Report Emailer
======================

This module allows you to send weather reports via email.
It retrieves weather data to suggest clothes based on the weather conditions at the given location.

Functions
---------

.. function:: conditions(main: str) -> str

.. function:: clothing(temperature: int, cold_threshold: str, warm_threshold: str) -> str

.. function:: get_data(api_key: str, lat: str, lon: str, lang: str) -> Optional[Dict[str, Any]]

.. function:: send_email(data: Dict[str, Any], sender: str, receiver: str, password: str, cold_threshold: str, warm_threshold: str) -> bool

Classes
-------

.. class:: ConfigManager

   .. method:: create_default_config() -> None

   .. method:: save_config(settings: Dict[str, Any], password: str, key: bytes) -> None

   .. method:: load_config() -> Dict[str, Any]

   .. method:: generate_password_key() -> bytes

.. class:: UserGUI

   .. method:: initUI()

   .. method:: setupControls(layout)

   .. method:: addTemperatureSliders(layout, config_values)

   .. method:: updateTemperatureLabels()

   .. method:: on_submit()

Example
-------

.. code-block:: python

   get_data(api_key, '1', '1', 'de')
   send_email(weather_data, 'sender@gmail.com', 'receiver@gmail.com', 'password123', '5', '25')



Detailed Descriptions
-------

"""

import os
import smtplib
import configparser
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QSlider,
    QHBoxLayout,
    QCheckBox,
)
from PyQt5.QtCore import Qt


def conditions(main: str) -> str:
    """
    Determines additional clothing based on weather conditions.

    :param main: The main weather condition.
    :return: Recommendations for additional clothing.
    """
    if main in ["Rain", "Drizzle", "Thunderstorm"]:
        return "Kopfbedeckung und "
    elif main in ["Snow"]:
        return "Handschuhe, Kopfbedeckung und "
    return ""


def clothing(temperature: int, cold_threshold: str, warm_threshold: str) -> str:
    """
    Recommends clothing based on the temperature.

    :param temperature: The current temperature.
    :param cold_threshold: The cold threshold.
    :param warm_threshold: The warm threshold.
    :return: String to suggest clothing type like warm clothing.
    """

    if temperature > int(warm_threshold):
        return "luftige Kleidung"
    elif temperature < int(cold_threshold):
        return "warme Kleidung"
    return "normale Kleidung"


def get_data(api_key: str, lat: str, lon: str, lang: str) -> Optional[Dict[str, Any]]:
    """
    Fetches weather data from OpenWeatherMap API.

    :param api_key: The API key for OpenWeatherMap.
    :param lat: The latitude of the location.
    :param lon: The longitude of the location.
    :param lang: The language for the weather data.
    :return: A dictionary with the weather data.
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
) -> bool:
    """
    Sends an email with the weather report.

    :param data: The stored weather data.
    :param sender: The email address of the sender.
    :param receiver: The email address of the receiver.
    :param password: The password of the sender.
    :param cold_threshold: The cold threshold.
    :param warm_threshold: The warm threshold.
    :return: True if the email was successfully sent, otherwise False.
    """

    if not data:
        return False

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

    msg = MIMEMultipart("alternative")  # Both Text + HTML Content combined
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"Wetterbericht für {region} am {today}"
    msg.attach(MIMEText(html_body, "html"))

    try:  # Server connection test, prints clear description of errors
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        return True
    except smtplib.SMTPException as e:
        print(f"Fehler beim Senden der Mail: {e}")
        return False


class ConfigManager:
    """
    Manages reading and writing to the configuration file and handling encryption.
    """

    def __init__(self, config_path: str):
        """
        Initializes the ConfigManager with the configuration file path.

        :param config_path: The path to the configuration file.
        """
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.config_path):
            self.create_default_config()
        self.key = self.generate_password_key()  # Load or generate the key at the start

    def generate_password_key(self) -> bytes:
        """
        Generate or retrieve a valid Fernet key for encrypting email passwords.

        :return: Returns bytes containing the Fernet key.
        """
        try:
            with open(
                "passwordKey.txt", "rb"
            ) as file:  # Ensure this is 'rb' for binary read
                key = file.read()
                Fernet(key)  # Is the key valid?
                return key  # Return Key as bytes
        except (FileNotFoundError, ValueError):
            # If the key file is missing or the key is invalid, generate new key
            key = Fernet.generate_key()
            with open("passwordKey.txt", "wb") as file:  # wb = write-binary
                file.write(key)
                self.create_default_config()
                print("Invalid Password Key, creating default config")
            return key

    def create_default_config(self) -> None:
        """
        Creates a default configuration file if none is available.
        """
        self.config["WEATHER"] = {
            "latitude": "51.4344",
            "longitude": "6.7623",
            "language": "de",
            "cold_threshold": "5",
            "warm_threshold": "20",
        }
        self.config["EMAIL"] = {
            "sender_email": "sender@gmail.com",
            "encrypted_password": "",
            "receiver_email": "receiver@gmail.com",
        }
        with open(self.config_path, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the config.ini file.

        :return: Returns a dictionary containing the loaded configuration values.
        """
        self.config.read(self.config_path)
        cipher = Fernet(self.key)
        encrypted_password = self.config.get("EMAIL", "encrypted_password")
        try:
            decrypted_password = (  # string into bytes, decrypt bytes back into string
                cipher.decrypt(encrypted_password.encode()).decode()
                if encrypted_password
                else ""
            )
        except Exception as e:
            print(f"Error decrypting password: {e}")
            decrypted_password = ""
        return {
            "latitude": self.config.get("WEATHER", "latitude"),
            "longitude": self.config.get("WEATHER", "longitude"),
            "language": self.config.get("WEATHER", "language"),
            "cold_threshold": int(self.config.get("WEATHER", "cold_threshold")),
            "warm_threshold": int(self.config.get("WEATHER", "warm_threshold")),
            "sender_email": self.config.get("EMAIL", "sender_email"),
            "receiver_email": self.config.get("EMAIL", "receiver_email"),
            "decrypted_password": decrypted_password,
        }

    def save_config(
        self,
        latitude,
        longitude,
        language,
        cold_threshold,
        warm_threshold,
        sender_email,
        receiver_email,
        password,
    ) -> None:
        """
        Save the current configuration to the config.ini file.

        :param latitude: Latitude for weather data.
        :param longitude: Longitude for weather data.
        :param language: Language for weather data.
        :param cold_threshold: Cold temperature threshold.
        :param warm_threshold: Warm temperature threshold.
        :param sender_email: Sender's email address.
        :param receiver_email: Receiver's email address.
        :param password: Sender's email password to be encrypted.
        :return: None

        """
        self.config.read(self.config_path)

        # Set new values in the config
        self.config.set("WEATHER", "latitude", latitude)
        self.config.set("WEATHER", "longitude", longitude)
        self.config.set("WEATHER", "language", language)
        self.config.set("WEATHER", "cold_threshold", cold_threshold)
        self.config.set("WEATHER", "warm_threshold", warm_threshold)
        self.config.set("EMAIL", "sender_email", sender_email)
        self.config.set("EMAIL", "receiver_email", receiver_email)

        # Encrypt and set the password
        cipher = Fernet(self.key)
        encrypted_password = cipher.encrypt(password.encode()).decode()
        self.config.set("EMAIL", "encrypted_password", encrypted_password)

        # Write the updated configuration back to file
        with open(self.config_path, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)


class UserGUI(QMainWindow):
    """
    Main class for the weather GUI.
    """

    def __init__(self, ConfigManager):
        super().__init__()  # Creates object for the UI configuration
        self.config_manager = ConfigManager
        self.initUI()

    def initUI(self):
        """
        Initializes the GUI window design and appearance.

        :return: None
        """
        self.setWindowTitle("WetterMail GUI")
        self.setGeometry(100, 100, 500, 500)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.setupControls(layout)
        self.save_input_checkbox = QCheckBox("Eingaben Speichern", self)
        layout.addWidget(self.save_input_checkbox)

        send_btn = QPushButton("Senden", self)
        send_btn.clicked.connect(self.on_submit)
        layout.addWidget(send_btn)

        self.setStyleSheet(
            """
            QWidget {
                font-family: 'Arial';
                font-size: 14px;
                background-color: #f0f4f8;
            }
            QLabel {
                color: #2e3440;
                padding: 8px;
                font-weight: bold;
            }
            QLineEdit, QSlider {
                border: 2px solid #88c0d0;
                border-radius: 10px;
                padding: 8px;
                background-color: #eceff4;
            }
            QPushButton {
                background-color: #5e81ac;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
            QSlider::groove:horizontal {
                height: 10px;
                background: transparent;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eee, stop:1 #ccc);
                border: 1px solid #777;
                width: 18px;
                margin-top: -2px;
                margin-bottom: -2px;
                border-radius: 8px;
            }
            QSlider#coldSlider::sub-page:horizontal {
                background: #256fff;
            }
            QSlider#coldSlider::add-page:horizontal {
                background: #a3be8c;
            }
            QSlider#warmSlider::sub-page:horizontal {
                background: #a3be8c; 
            }
            QSlider#warmSlider::add-page:horizontal {
                background: #f54029;
            }
            """
        )

    def setupControls(self, layout):
        """
        Sets up the controls for the GUI.

        :param layout: The layout to which the controls will be added.
        :return: None
        """

        # Loads config and puts it into input fields
        config_values = self.config_manager.load_config()
        self.entries = {}
        labels = [
            ("Breitengrad:", "latitude", False),
            ("Längengrad:", "longitude", False),
            ("Sprache (de/en):", "language", False),
            ("Absender E-Mail:", "sender_email", False),
            ("Absender Passwort:", "decrypted_password", True),
            ("Empfänger E-Mail:", "receiver_email", False),
        ]

        # creates input fields dynamicaly for each config.ini entry
        for label_text, key, hide_text in labels:
            label = QLabel(label_text, self)
            layout.addWidget(label)
            entry = QLineEdit(self)
            entry.setText(str(config_values[key]))
            if hide_text:
                entry.setEchoMode(QLineEdit.Password)
            layout.addWidget(entry)
            self.entries[key] = entry

        self.addTemperatureSliders(layout, config_values)

    def addTemperatureSliders(self, layout, config_values):
        """
        Adds two temperature sliders to the GUI.

        :param layout: The layout to which the sliders will be added.
        :param config_values: The configuration values for the sliders.
        :return: None
        """

        self.slider_label = QLabel(
            f"Temperatur Komfortzone: {config_values['cold_threshold']}°C - {config_values['warm_threshold']}°C",
            self,
        )
        layout.addWidget(self.slider_label)

        slider_container = QWidget(self)
        slider_layout = QHBoxLayout(slider_container)
        self.cold_slider = QSlider(Qt.Horizontal, self)
        self.cold_slider.setObjectName("coldSlider")
        self.cold_slider.setMinimum(0)
        self.cold_slider.setMaximum(15)
        self.cold_slider.setValue(int(config_values["cold_threshold"]))
        self.cold_slider.setTickPosition(QSlider.TicksBelow)
        self.cold_slider.setTickInterval(1)
        self.warm_slider = QSlider(Qt.Horizontal, self)
        self.warm_slider.setObjectName("warmSlider")
        self.warm_slider.setMinimum(15)
        self.warm_slider.setMaximum(30)
        self.warm_slider.setValue(int(config_values["warm_threshold"]))
        self.warm_slider.setTickPosition(QSlider.TicksBelow)
        self.warm_slider.setTickInterval(1)

        slider_layout.addWidget(self.cold_slider)
        slider_layout.addWidget(self.warm_slider)
        layout.addWidget(slider_container)

        self.cold_slider.valueChanged.connect(self.updateTemperatureLabels)
        self.warm_slider.valueChanged.connect(self.updateTemperatureLabels)

    def updateTemperatureLabels(self):
        self.slider_label.setText(
            f"Temperatur Komfortzone {self.cold_slider.value()}°C - {self.warm_slider.value()}°C"
        )

    def on_submit(self):
        settings = {
            "latitude": self.entries["latitude"].text(),
            "longitude": self.entries["longitude"].text(),
            "language": self.entries["language"].text(),
            "cold_threshold": str(self.cold_slider.value()),
            "warm_threshold": str(self.warm_slider.value()),
        }

        data = get_data(
            API_KEY, settings["latitude"], settings["longitude"], settings["language"]
        )

        if data:
            email_sent = send_email(
                data,
                self.entries["sender_email"].text(),
                self.entries["receiver_email"].text(),
                self.entries["decrypted_password"].text(),
                settings["cold_threshold"],
                settings["warm_threshold"],
            )
            if email_sent:
                QMessageBox.information(self, "Erfolg", "E-Mail erfolgreich gesendet!")
                self.close()
            else:  # If email was not sent
                QMessageBox.warning(self, "Fehler", "Fehler beim Senden der E-Mail.")

        else:  # If data is None
            QMessageBox.warning(self, "Fehler", "Fehler beim Abrufen der Wetterdaten.")

        # Check the checkbox before saving the configuration
        if self.save_input_checkbox.isChecked():
            self.config_manager.save_config(
                settings["latitude"],
                settings["longitude"],
                settings["language"],
                settings["cold_threshold"],
                settings["warm_threshold"],
                self.entries["sender_email"].text(),
                self.entries["receiver_email"].text(),
                self.entries["decrypted_password"].text(),
            )


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    API_KEY = "e055a71967956ab0d652f985f92e79a4"
    config_manager = ConfigManager("config.ini")
    email_settings = config_manager.load_config()

    # Initialize GUI with the configuration manager and the API key
    gui = UserGUI(config_manager)
    gui.show()
    sys.exit(app.exec_())

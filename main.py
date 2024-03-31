# Alle notwendigen Bibliotheken:
import tkinter as tk
import requests
import smtplib
import configparser
from cryptography.fernet import Fernet
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


#conditions.txt, welche Kleidung empfohlen wird
def conditions(main):
    if main in ["Rain", "Drizzle", "Thunderstorm"]:
        return "Kopfbedeckung und "
    elif main in ["Snow"]:
        return "Handschuhe, Kopfbedeckung und "
    else:
        return ""


# Clothing.txt, welche Kleidung empfohlen wird
def clothing(temperature, cold_threshold, warm_threshold):
    if temperature > int(warm_threshold):
        return "luftige Kleidung"
    elif temperature < int(cold_threshold):
        return "warme Kleidung"
    else:
        return "normale Kleidung"


def getData(api_key, lat, lon, lang):
    request_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&lang={lang}"
    feedback = requests.get(request_url)
    if feedback.status_code == 200: # Wenn Verbindung erfolgreich, dann Wetter Daten in json format zurückgeben
        return feedback.json()
    else:
        return None


def sendEmail(data, sender, receiver, password, cold_threshold, warm_threshold):
    if data:
        region = data["name"] ## Ruhrort
        description = data["weather"][0]["description"] ## Leichter Regen
        temp = round(data["main"]["temp"] - 273.15)
        main = data["weather"][0]["main"]
        today = datetime.now().strftime("%d.%m.%y")

        conditions_txt = conditions(main)
        clothing_txt = clothing(temp, cold_threshold, warm_threshold)


        # Tabelle mit den Daten schön formattiert
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

        msg = MIMEMultipart("alternative") ## E-Mail Darstellung aus mehreren Teilen, da wir Text+HTML haben
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = f"Wetterbericht für {region} am {today}"
        msg.attach(MIMEText(html_body, "html"))

        try: ## Da beim Server Verbindungsaufbau fehler passieren können, zb. passwort falsch oder 2-FA Authentifizierung
            with smtplib.SMTP("smtp.gmail.com", 587) as server: # Verbindung zum Server mit TLS-Verchlüsselung
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
                server.quit()
                print("E-Mail erfolgreich gesendet!")
        except Exception as e:
            print(f"Fehler beim Senden der E-Mail: {e}")


def saveConfig(lat, lon, lang, cold_threshold, warm_threshold, sender, receiver, password, key):
    config = configparser.ConfigParser()
    config.read('config.ini')

    config.set('WEATHER', 'latitude', lat) # Falls bei Submit auf Eingaben speichern geklickt wurde, dann sollen die Eingaben in config geschrieben werden
    config.set('WEATHER', 'longitude', lon)
    config.set('WEATHER', 'language', lang)
    config.set('WEATHER', 'cold_threshold', str(cold_threshold)) # Umwandlung in String, da configparser.set kein value returnt
    config.set('WEATHER', 'warm_threshold', str(warm_threshold))
    config.set('EMAIL', 'sender_email', sender)
    config.set('EMAIL', 'receiver_email', receiver)

    # Der schlüssel aus passwordKey.txt wird verschlüsselt im lokalen Objekt cipher gespeichert. Bei jeder verschlüsselung und entschlüsselung braucht man cipher
    # Kodiert das Passwort in Bytes (encode), dann werden die Bytes verschlüsselt mit encrypt
    # Dekodiert das Passwort zurück um einen String aus Bytes zu erhalten, damit es in der config.ini gespeichert werden kann
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode())
    config.set('EMAIL', 'encrypted_password', encrypted_password.decode())

    with open('config.ini', 'w') as configData: # Write um alle configs die wir vorher gesetzt haben in config.ini reinzuschreiben
        config.write(configData)


def loadConfig():
    config = configparser.ConfigParser() #configparser bibliothek um ini dateien lesen/schreiben
    config.read('config.ini')

    with open('passwordKey.txt', 'rb') as passwordKey: # read-binary
        key = passwordKey.read()

    cipher = Fernet(key)
    encrypted_password = config.get('EMAIL', 'encrypted_password')
    decrypted_password = cipher.decrypt(encrypted_password.encode()).decode() if encrypted_password else "" # Falls kein Passwort vorhanden, nur ein leeren String zurückgeben
    # Verschlüsseltes Password wird entschlüsselt, in Bytes umgewandelt zur Verschlüsselung (da es als string gespeichert war), dann werden die Bytes entschlüsselt.

    return {
        'latitude': config.get('WEATHER', 'latitude'),
        'longitude': config.get('WEATHER', 'longitude'),
        'language': config.get('WEATHER', 'language'),
        'cold_threshold': int(config.get('WEATHER', 'cold_threshold')),
        'warm_threshold': int(config.get('WEATHER', 'warm_threshold')),
        'sender_email': config.get('EMAIL', 'sender_email'),
        'receiver_email': config.get('EMAIL', 'receiver_email'),
        'decrypted_password': decrypted_password
    }


def input():
    def submitButton():
        apiKey = "e055a71967956ab0d652f985f92e79a4"
        with open ("passwordKey.txt", "r") as file:
            passwordKey = file.read()
        lat = latInput.get()
        lon = lonInput.get()
        lang = langInput.get()
        coldThreshold = coldThresholdInput.get()
        warmThreshold = warmThresholdInput.get()
        sender = senderInput.get()
        receiver = receiverInput.get()
        password = passwordInput.get()

        if saveConfigVar.get():
            saveConfig(lat, lon, lang, coldThreshold, warmThreshold, sender, receiver, password, passwordKey)

        data = getData(apiKey, lat, lon, lang)
        sendEmail(data, sender, receiver, password, coldThreshold, warmThreshold)
        window.destroy()

    configValues = loadConfig()


    window = tk.Tk() # Haupt-Fenster für die Eingabe wird gestartet
    window.title("Wetterbericht Parameter")
    window.geometry("320x280")
    inputWidth = 35

    tk.Label(window, text="Breitengrad:").grid(row=1, column=0) # Text "Breitengrad" soll auf Zeile 1, Spalte 0 sein
    latInput = tk.Entry(window, width=inputWidth) #Eingabefeld
    latInput.insert(0, configValues['latitude']) #Eingabefeld erhält vordefinierten Wert aus config.ini
    latInput.grid(row=1, column=1) # Eingabefeld soll auf Zeile 1, Spalte 1 positioniert sein

    tk.Label(window, text="Längengrad:").grid(row=2, column=0)
    lonInput = tk.Entry(window, width=inputWidth)
    lonInput.insert(0, configValues['longitude'])
    lonInput.grid(row=2, column=1)

    tk.Label(window, text="Sprache (de/en):").grid(row=3, column=0)
    langInput = tk.Entry(window, width=inputWidth)
    langInput.insert(0, configValues['language'])
    langInput.grid(row=3, column=1)

    tk.Label(window, text="Kälteschwelle:").grid(row=4, column=0)
    coldThresholdInput = tk.Entry(window, width=inputWidth)
    coldThresholdInput.insert(0, configValues['cold_threshold'])
    coldThresholdInput.grid(row=4, column=1)

    tk.Label(window, text="Wärmeschwelle:").grid(row=5, column=0)
    warmThresholdInput = tk.Entry(window, width=inputWidth)
    warmThresholdInput.insert(0, configValues['warm_threshold'])
    warmThresholdInput.grid(row=5, column=1)

    tk.Label(window, text="Absender E-Mail:").grid(row=6, column=0)
    senderInput = tk.Entry(window, width=inputWidth)
    senderInput.insert(0, configValues['sender_email'])
    senderInput.grid(row=6, column=1)

    tk.Label(window, text="Absender Passwort:").grid(row=7, column=0)
    passwordInput = tk.Entry(window, show="*", width=inputWidth)
    passwordInput.insert(0, configValues['decrypted_password'])
    passwordInput.grid(row=7, column=1)

    tk.Label(window, text="Empfänger E-Mail:").grid(row=8, column=0)
    receiverInput = tk.Entry(window, width=inputWidth)
    receiverInput.insert(0, configValues['receiver_email'])
    receiverInput.grid(row=8, column=1)

    saveConfigVar = tk.IntVar()
    saveConfigCheckbutton = tk.Checkbutton(window, text="Eingaben speichern", variable=saveConfigVar)
    saveConfigCheckbutton.grid(row=9, column=0)

    submitButton = tk.Button(window, text="Senden", command=submitButton)
    submitButton.grid(row=10, column=0, columnspan=2)

    window.mainloop() # Reagiert auf Benutzereingaben, aktualisiert die GUI bis es beendet wird durch destroy


if __name__ == "__main__":
    input()

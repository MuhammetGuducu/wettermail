import tkinter as tk
import requests
import smtplib
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
    if temperature > warm_threshold:
        return "luftige Kleidung"
    elif temperature < cold_threshold:
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
        region = data["name"] # Ruhrort
        description = data["weather"][0]["description"] ## Leichter Regen
        temp = round(data["main"]["temp"] - 273.15)
        main = data["weather"][0]["main"]
        humidity = data["main"]["humidity"]
        windSpeed = data["wind"]["speed"]

        conditions_txt = conditions(main)
        clothing_txt = clothing(temp, cold_threshold, warm_threshold)
        today = datetime.now().strftime("%d.%m.%y")

        # Tabelle mit den Daten formattiert
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

        msg = MIMEMultipart("alternative") ## E-Mail aus mehreren Teilen, die Text+HTML zur Darstellung nutzt
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = f"Wetterbericht für {region} am {today}"
        msg.attach(MIMEText(html_body, "html"))

        try: # Da hier Fehler passieren können
            with smtplib.SMTP("smtp.gmail.com", 587) as server: #Verbindung zum server mit TLS-Verschlüselung
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
                server.quit()
                print("EMail erfolgreich gesendet!")
        except Exception as e:
            print(f"Fehler beim Senden der E-Mail: {e}")

def input():
    def submitButton():
        apiKey = "e055a71967956ab0d652f985f92e79a4"
        lat = latInput.get() ## Nutzereingaben lesen und speichern in "lat"
        lon = lonInput.get()
        lang = langInput.get()
        coldThreshold = int(coldThresholdInput.get())
        warmThreshold = int(warmThresholdInput.get())
        sender = senderInput.get()
        receiver = receiverInput.get()
        password = passwordInput.get()

        data = getData(apiKey, lat, lon, lang)
        sendEmail(data, sender, receiver, password, coldThreshold, warmThreshold)
        root.destroy()

    root = tk.Tk() #Starte tk Fenster für die Inputs
    root.title("Wetterbericht Parameter")
    root.geometry("260x200")
    inputWidth = 25

    tk.Label(root, text="Latitude:").grid(row=1, column=0) # Text "Latitude" soll auf Zeile 1, Spalte 0 sein
    latInput = tk.Entry(root, width=inputWidth) ## Eingabefeld
    latInput.insert(0, "51.4344") ## Eingabefeld hat schon einen Wert gegeben, den der Nutzer aber ändern kann
    latInput.grid(row=1, column=1) # Eingabefeld soll auf der Zeile 1, Spalte 1 sein

    tk.Label(root, text="Longitude:").grid(row=2, column=0)
    lonInput = tk.Entry(root, width=inputWidth)
    lonInput.insert(0, "6.7623")
    lonInput.grid(row=2, column=1)

    tk.Label(root, text="Language:").grid(row=3, column=0)
    langInput = tk.Entry(root, width=inputWidth)
    langInput.insert(0, "de")
    langInput.grid(row=3, column=1)

    tk.Label(root, text="Cold Threshold:").grid(row=4, column=0)
    coldThresholdInput = tk.Entry(root, width=inputWidth)
    coldThresholdInput.insert(0, "5")
    coldThresholdInput.grid(row=4, column=1)

    tk.Label(root, text="Warm Threshold:").grid(row=5, column=0)
    warmThresholdInput = tk.Entry(root, width=inputWidth)
    warmThresholdInput.insert(0, "20")
    warmThresholdInput.grid(row=5, column=1)

    tk.Label(root, text="Sender Email:").grid(row=6, column=0)
    senderInput = tk.Entry(root, width=inputWidth)
    senderInput.insert(0, "sender@example.com")
    senderInput.grid(row=6, column=1)

    tk.Label(root, text="Password:").grid(row=7, column=0)
    passwordInput = tk.Entry(root, show="*", width=inputWidth)
    passwordInput.grid(row=7, column=1)

    tk.Label(root, text="Receiver Email:").grid(row=8, column=0)
    receiverInput = tk.Entry(root, width=inputWidth)
    receiverInput.insert(0, "receiver@example.com")
    receiverInput.grid(row=8, column=1)

    submitButton = tk.Button(root, text="Submit", command=submitButton)
    submitButton.grid(row=9, column=0, columnspan=2)

    root.mainloop() # Warte und Reagiere auf Benutzereingaben, anschließend aktualisiere die GUI bis es beendet wird durch destroy


if __name__ == "__main__":
    input()

# WetterMail

WetterMail ist ein Python-Skript, das Nutzern basierend auf wählbaren Parametern personalisierte Wetterberichte per E-Mail zusendet. Es nutzt die OpenWeatherMap-API, um Echtzeit-Wetterdaten zu sammeln, analysiert diese Daten und sendet dann maßgeschneiderte Empfehlungen wie zb. welche Kleidung empfohlen wird.




## Verwendete Sprachen und Bibliotheken

- **Python**: Einzige Programmiersprache, die verwendet wurde.
- **Tkinter**: Eine Python-Bibliothek für die Erstellung des GUI.
- **Requests**: Für HTTP-Anfragen zur Abfrage der Wetterdaten.
- **smtplib**: Zum Versenden von E-Mails.
- **configparser**: Für das Lesen/Schreiben von Konfigurationsdateien.
- **Cryptography-Fernet**: Für die sichere Speicherung von Passwörtern.




## Zweck des Projekts

Das Hauptziel von WetterMail ist es, eine automatisierte Lösung für den täglichen Bedarf an Wetterinformationen zu bieten. Langfristig könnte es zu einer vollwertigen Anwendung ausgebaut werden, die verschiedene Wetterdienste und erweiterte Personalisierungsfunktionen unterstützt. Aktuell befindet sich das Projekt in einer aktiven Entwicklungsphase. Die Grundfunktionalitäten, wie das Abrufen von Wetterdaten und das Versenden von E-Mails, sind implementiert. Zudem kann der Nutzer eingegebene Werte in der config speichern lassen, diese werden dann beim Klick auf "Senden" in die config geschrieben. Die Werte in der config werden beim nächsten Start automatisch eingelesen.  




## Zukünftige Erweiterungen

- Integration zusätzlicher Wetterdatenquellen für genauere Vorhersagen und Empfehlungen.
- Verbesserung der Benutzerinteraktionen in der GUI.
- Implementierung von Benutzerprofilen für personalisierte Einstellungen wie zb. Outfit-Bezeichnungen.
- Verbesserung der Sicherheit, siehe "Aktuelle Probleme".




## Aktuelle Probleme

- **Sicherheit**: Fernet zur Verschlüsselung ist nicht absolut sicher, da der `passwordKey` in falsche Hände geraten kann.
- **Nur G-Mail-Provider**: Aktuell ist das Programm nur auf GMail ausgerichtet durch die smtplib Library.




> [!TIP]
> - Zunächst müssen die notwendigen Bibliotheken installiert werden, dies kann man über Pycharm machen.
> - Die Dateien `config.ini` und `passwordKey.txt` sind ebenfalls notwendig.
> - Anschließend kann das Programm über `main.py` gestartet werden.



## Screenshots 
![EMAIL](https://github.com/MuhammetGuducu/wettermail/assets/84397069/a2f6554f-f4d9-43ae-ac6f-da113c3b6460)
![CONFIG](https://github.com/MuhammetGuducu/wettermail/assets/84397069/2eb53a12-1594-4a54-8319-30cfe8a18c46)
![GUI](https://github.com/MuhammetGuducu/wettermail/assets/84397069/cb412b6b-c60b-436c-be86-5dcb06cb0adf)

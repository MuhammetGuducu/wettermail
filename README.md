# WetterMail

WetterMail ist ein Python-Skript, das Nutzern basierend auf wählbaren Parametern personalisierte Wetterberichte per E-Mail zusendet. Es nutzt die OpenWeatherMap-API, um Echtzeit-Wetterdaten zu sammeln, analysiert diese Daten und sendet dann maßgeschneiderte Empfehlungen wie zb. welche Kleidung empfohlen wird.



## Verwendete Sprachen und Bibliotheken

- **Python**: Einzige Programmiersprache, die verwendet wurde.
- **PyQt5**: Eine Python-Bibliothek für die Erstellung des GUI.
- **Requests**: Für HTTP-Anfragen zur Abfrage der Wetterdaten.
- **smtplib**: Zum Versenden von E-Mails.
- **configparser**: Für das Lesen/Schreiben von Konfigurationsdateien.
- **Cryptography-Fernet**: Für die sichere Speicherung von Passwörtern.
- **Unittests**: Um die Funktionalität von main.py zu testen
- **Sphinx**: Eine automatisch generierte HTML Dokumentation für Funktionen



## Zweck des Projekts

* Das Hauptziel von WetterMail ist es, eine automatisierte Lösung für den täglichen Bedarf an Wetterinformationen zu bieten. 
* Die Grundfunktionalitäten, wie das Abrufen von Wetterdaten und das Versenden von E-Mails, sind implementiert.
* Der Nutzer kann Eingaben in der config speichern, beim Klick auf "Senden" werden diese in die config geschrieben um beim nächsten Start automatisch eingelesen zu werden. 



## Zukünftige Erweiterungen

- Integration zusätzlicher Wetterdatenquellen für genauere Vorhersagen und Empfehlungen.
- Implementierung von Benutzerprofilen für personalisierte Einstellungen wie zb. Outfit-Bezeichnungen.
- Entwicklung einer Website mit dem Django Framework.
- Weitere E-Mail Provider, da aktuell nur G-Mail unterstützt wird. 



> [!TIP]
> - Zunächst müssen die notwendigen Bibliotheken installiert werden, dies kann man über Pycharm machen.
> - Anschließend kann das Programm über `main.py` gestartet werden.
> - `test_main.py` ist optional, damit lässt sich die Funktionalität testen. 



## Screenshots 
![EMAIL](https://github.com/MuhammetGuducu/wettermail/assets/84397069/a2f6554f-f4d9-43ae-ac6f-da113c3b6460)
![CONFIG](https://github.com/MuhammetGuducu/wettermail/assets/84397069/2eb53a12-1594-4a54-8319-30cfe8a18c46)
![gui](https://github.com/MuhammetGuducu/wettermail/assets/84397069/7b42e256-272c-40f5-bc46-280518a78dfb)
![TEST](https://github.com/MuhammetGuducu/wettermail/assets/84397069/2e13568e-1aa1-4ab1-930b-fccd4fd37747)
![sphinx](https://github.com/MuhammetGuducu/wettermail/assets/84397069/aef3a322-a588-4a18-8e6e-c4bb142a1c66)

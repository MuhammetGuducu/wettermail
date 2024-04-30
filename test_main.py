"""
This module tests the functionality of each main.py component by using unittest
"""

import main
import unittest
from unittest.mock import patch, mock_open
from cryptography.fernet import Fernet


class test_functionality(unittest.TestCase):
    def test_conditions_rain(self):
        """Test conditions function for rainy weather."""
        self.assertEqual(main.conditions("Rain"), "Kopfbedeckung und ") # Does it return "Kopfbedeckung und" when it rains?

    def test_conditions_snow(self):
        """Test conditions function for snowy weather."""
        self.assertEqual(main.conditions("Snow"), "Handschuhe, Kopfbedeckung und ")

    def test_clothing_warm(self):
        """Test clothing function for warm temperatures."""
        self.assertEqual(main.clothing(25, 5, 20), "luftige Kleidung")

    @patch("requests.get")
    def test_get_data_successful(self, mock_get):
        """Test get_data function with a successful API call."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"test": "data"}
        self.assertEqual(
            main.get_data("test_api_key", "lat", "lon", "de"), {"test": "data"}
        )

    @patch("smtplib.SMTP")
    def test_send_email(self, mock_smtp):
        """Test send_email function with a successful email send."""
        data = {
            "name": "Region",
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 298},
        }
        main.send_email(
            data, "sender@example.com", "receiver@example.com", "password", 5, 20
        )
        mock_smtp.assert_called_with("smtp.gmail.com", 587)

    def test_create_default_config(self):
        """Test create_default_config function for creating default config."""
        config_manager = main.ConfigManager("config.ini")
        config_manager.create_default_config()

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_create_default_config_file_creation(self, mock_open):
        """Test whether create_default_config creates a config file."""
        config_manager = main.ConfigManager("config.ini")
        config_manager.create_default_config()
        mock_open.assert_called_with("config.ini", "w", encoding="utf-8")


class test_read(unittest.TestCase):

    @patch("main.open", new_callable=mock_open, read_data="[DEFAULT]\n")
    def test_save_config(self, mock_file):
        """Test whether save_config saves a config file."""
        config_manager = main.ConfigManager("config.ini")
        config_manager.save_config(
            "1", "1", "de", "1", "1", "test@gmail.com", "test@gmail.com", "1"
        )
        mock_file.assert_called_with("config.ini", "w", encoding="utf-8")

    @patch("main.configparser.ConfigParser")
    def test_load_config(self, mock_config_parser):
        # Define a preset configuration
        preset_config = {
            "latitude": "1",
            "longitude": "1",
            "language": "de",
            "cold_threshold": 5,
            "warm_threshold": 20,
            "sender_email": "test@gmail.com",
            "receiver_email": "test@gmail.com",
            "encrypted_password": "",
        }

        # Setup mock to return preset values
        mock_config = mock_config_parser.return_value
        mock_config.get.side_effect = lambda section, option: preset_config.get(option)

        config_manager = main.ConfigManager("config.ini")
        config = config_manager.load_config()

        # check if loaded config match the preset config
        for key, value in preset_config.items():
            self.assertEqual(config.get(key, ""), value)

    @patch(
        "main.open",
        new_callable=mock_open,
        read_data="GJwdfls_ApgtFJnKmMV9dmzrMt_10Y4_Qe2HiBEyI6c=",
    )
    def test_password_key(self, mock_file):
        config_manager = main.ConfigManager("config.ini")
        key = config_manager.generate_password_key()
        self.assertIsInstance(key, str)  # Does it return string as key
        try:
            Fernet(key.encode())
        except ValueError:
            self.fail("function password_key() returns an invalid FernetKey")


if __name__ == "__main__":
    unittest.main()

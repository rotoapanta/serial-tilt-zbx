"""
Unit tests for the data parser.
"""

import unittest
from parsers.data_parser import parse_raw_data
from config.station_mapping import STATION_NAMES

class TestDataParser(unittest.TestCase):

    def test_valid_data_parsing(self):
        """Test that valid raw data is parsed correctly."""
        # This is a sample byte string that mimics the expected format.
        # You should replace this with a real example from your device.
        raw_data = b'~\x00\x01\x02\x03\x04\x05\x01\x01\x00\x01RD+12.34,TD+56.78,T+25.5,V+3.3~~\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09RAIN+1.2,V+3.4~\n'
        parsed_data = parse_raw_data(raw_data)
        self.assertIsNotNone(parsed_data)
        self.assertEqual(parsed_data['station_name'], STATION_NAMES.get(1, "Unknown_1"))
        self.assertEqual(parsed_data['inclinometer']['radial'], 12.34)
        self.assertEqual(parsed_data['pluviometer']['rain_level'], 1.2)

    def test_invalid_data_returns_none(self):
        """Test that invalid or incomplete data returns None."""
        self.assertIsNone(parse_raw_data(b'invalid data'))
        self.assertIsNone(parse_raw_data(b'~missing~~parts~'))
        self.assertIsNone(parse_raw_data(b'~too~~many~~parts~'))

    def test_malformed_frame_returns_none(self):
        """Test that malformed frames return None."""
        # Malformed inclinometer part
        raw_data = b'~\x00\x01\x02\x03\x04\x05\x01\x01\x00\x01RD+12.34,TD+56.78~~\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09RAIN+1.2,V+3.4~\n'
        self.assertIsNone(parse_raw_data(raw_data))

if __name__ == '__main__':
    unittest.main()

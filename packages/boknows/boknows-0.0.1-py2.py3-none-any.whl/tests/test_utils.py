import unittest

from boknows import utils

class TestUtils(unittest.TestCase):
    def test_csv_cleanup(self):
        self.maxDiff = None
        files = {}
        expected = {
            'DivisionIWon-LostPercentage': '"Rank","Name","W","L","Pct"\n"1","Michigan St.","10","0","100.0"\n',
            'DivisionIScoringOffense': '"Rank","Name","GM","W-L","PTS","PPG"\n"1","The Citadel","10","6-4","936","93.6"\n"2","La.-Lafayette","6","3-3","551","91.8"\n'
        }
        
        with open('examples/test.csv', 'r') as f:
            files = utils.csv_cleanup(f.read())
        
        self.assertEqual(files, expected)

import unittest
from main import checkUsernameValidity

class testUsernamValidity(unittest.TestCase):
    def test_username(self):
        self.assertTrue(checkUsernameValidity("10test_1"))
        self.assertTrue(checkUsernameValidity("_tESt_20"))
        self.assertTrue(checkUsernameValidity("te@st"), "The username consists of only alphabets, numbers and underscores.")
        

if __name__ == "__main__":
    unittest.main()
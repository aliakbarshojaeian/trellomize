import unittest
from main import checkEmailValidity

class testEmailValidity(unittest.TestCase):
    def test_email(self):
        self.assertTrue(checkEmailValidity("test@gmail.com"))
        self.assertTrue(checkEmailValidity("te~st@gmail.com"), "The characters #, $, ^, &, *, ~ and ` should not be in the email.")
        self.assertTrue(checkEmailValidity("t@g.c"), "Email length is short.")
        self.assertTrue(checkEmailValidity("test@gmail.c"), "There must be at least two letters after the period.")


if __name__ == "__main__":
    unittest.main()
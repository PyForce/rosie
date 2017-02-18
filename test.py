import unittest


if __name__ == '__main__':
    TESTS = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(TESTS)

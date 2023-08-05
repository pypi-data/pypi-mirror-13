import unittest
import sys
import os


ROOT_PATH = os.path.dirname(__file__).split(os.path.sep)[0]

# include alabama dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/alabama/")

if __name__ == '__main__':
    tests = unittest.TestLoader().discover(ROOT_PATH, "*.py")
    result = unittest.TextTestRunner(verbosity=2, failfast=False).run(tests)

    if not result.wasSuccessful():
        sys.exit(1)

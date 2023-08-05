# RUNME as 'python -m picture.tests.__main__'
import unittest
from mdx_picture import tests


def main():
    "Run all of the tests when run as a module with -m."
    suite = tests.get_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    main()

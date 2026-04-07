"""Script with a Python syntax error."""
import ansa
from ansa import base

def main()  # missing colon
    base.Open("test.ansa")

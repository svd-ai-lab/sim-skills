"""ANSA script that uses GUI functions — won't work in -nogui mode."""
import ansa
from ansa import base, constants, guitk


def main():
    entities = base.PickEntities(constants.NASTRAN, "SHELL")
    guitk.UserInput("Select entities to process")

import sys
from elevation.main import main

if ret := main():
    sys.exit(ret)

sys.exit(0)

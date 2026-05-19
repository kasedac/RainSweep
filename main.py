import sys
import os

# Add src to sys.path to allow imports from rainsweep package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rainsweep.main import main

if __name__ == "__main__":
    main()

import sys

# Check user has the correct Python Version
if sys.version_info < (3, 9):
    print("Please upgrade your Python version to 3.9.0 or higher")
    sys.exit()

# Check user packages are installed
import importlib.util

if importlib.util.find_spec("pygame_gui") is None:
    print("pygame_gui is not installed. Please install it using the following command:")
    print("pip install pygame_gui")
    sys.exit()

# Run Program
from src import app

app.run()

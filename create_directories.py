# create_directories.py
import os

directories = [
    'static',
    'static/images',
    'outputs',
    'outputs/plots',
    'saved_models'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")
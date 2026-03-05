import os
import sys
import shutil
from pathlib import Path

PROJECT_NAME = "fusionchmingest"

def create_package_structure():
    """Create the package structure."""
    
    # Create directories
    os.makedirs(f"{PROJECT_NAME}", exist_ok=True)
    os.makedirs("Formula", exist_ok=True)
    os.makedirs(".github/workflows", exist_ok=True)
    os.makedirs(f"{PROJECT_NAME}/tests/fixtures", exist_ok=True)
    os.makedirs(f"{PROJECT_NAME}/tests/unit", exist_ok=True)
    os.makedirs(f"{PROJECT_NAME}/tests/integration", exist_ok=True)
    os.makedirs(f"{PROJECT_NAME}/tests/mcp", exist_ok=True)
    
    print("Created directory structure")

if __name__ == "__main__":
    create_package_structure()

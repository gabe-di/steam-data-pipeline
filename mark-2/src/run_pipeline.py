
import subprocess
import sys
from pathlib import Path

# Locate the directory containing this script
SRC_DIR = Path(__file__).resolve().parent

print("Starting Steam Data Pipeline Mark II...", flush=True)

# Step 1: Extract data
print("Running extraction...", flush=True)
subprocess.run(
    [sys.executable, str(SRC_DIR / "extract.py")],
    check=True
)

# Step 2: Load data
print("Running database load...", flush=True)
subprocess.run(
    [sys.executable, str(SRC_DIR / "load.py")],
    check=True
)

# Step 3: Validate database
print("Running validation checks...", flush=True)
subprocess.run(
    [sys.executable, str(SRC_DIR / "validate.py")],
    check=True
)

print("Steam Data Pipeline Mark II completed successfully!")

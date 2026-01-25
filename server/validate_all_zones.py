import os
import sys
import subprocess

ZONES_DIR = os.path.join(os.path.dirname(__file__), "zones")

def main():
    errors = 0
    for fname in sorted(os.listdir(ZONES_DIR)):
        if fname.lower().endswith(".json"):
            path = os.path.join(ZONES_DIR, fname)
            result = subprocess.run([sys.executable, "validate_zone.py", path])
            if result.returncode != 0:
                errors += 1
    if errors:
        print(f"\n{errors} zone file(s) failed validation.")
        sys.exit(2)
    else:
        print("\nAll zone files are valid.")

if __name__ == "__main__":
    main()

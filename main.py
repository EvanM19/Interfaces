import subprocess
import sys

def main():
    process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "Markowitz/markowitz_app.py"])
    process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "Liquidity_management/liquidity_management_app.py"])

if __name__ == "__main__":
    main()
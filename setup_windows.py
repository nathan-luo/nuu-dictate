"""
Windows setup script for nuu-dictate
Run this after installing Python on Windows
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages for Windows"""
    requirements = [
        "pynput>=1.7.6",
        "pyaudio>=0.2.11", 
        "pyautogui>=0.9.54",
        "pyperclip>=1.8.2",
        "openai>=1.0.0"
    ]
    
    print("Installing requirements for Windows...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✓ Installed {req}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {req}: {e}")
            if "pyaudio" in req:
                print("  Try: pip install pipwin && pipwin install pyaudio")

def create_config():
    """Create config file if it doesn't exist"""
    config_content = """[openai]
api_key = YOUR_OPENAI_API_KEY_HERE

[settings]
recordings_folder = Documents/VoiceRecordings"""
    
    if not os.path.exists("config.ini"):
        with open("config.ini", "w") as f:
            f.write(config_content)
        print("✓ Created config.ini - Add your OpenAI API key!")
    else:
        print("✓ config.ini already exists")

def main():
    print("Setting up nuu-dictate for Windows...")
    install_requirements()
    create_config()
    print("\nSetup complete!")
    print("1. Add your OpenAI API key to config.ini")
    print("2. Run: python main.py")
    print("3. Press Win+Shift+V to record!")

if __name__ == "__main__":
    main()
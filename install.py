import os

# Update the package list
os.system('apt-get update')

# Install necessary packages
os.system('apt-get install -y wget unzip')

# Download and install Google Chrome
os.system('wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb')
os.system('dpkg -i google-chrome-stable_current_amd64.deb')
os.system('apt-get -f install -y')

# Download ChromeDriver
chrome_driver_version = os.popen('curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE').read().strip()
os.system(f'wget https://chromedriver.storage.googleapis.com/{chrome_driver_version}/chromedriver_linux64.zip')

# Unzip ChromeDriver
os.system('unzip chromedriver_linux64.zip')

# Move ChromeDriver to /usr/local/bin
os.system('mv chromedriver /usr/local/bin/chromedriver')

# Make ChromeDriver executable
os.system('chmod +x /usr/local/bin/chromedriver')

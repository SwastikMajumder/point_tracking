from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to ChromeDriver
service = Service('/usr/local/bin/chromedriver')

def main():
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the webpage
    driver.get('https://kiwiirc.hybridirc.com/#allindiachat.com')

    try:
        # Wait for the input field to be visible and interactable
        input_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[contains(@class, 'u-input')]"))
        )

        # Use JavaScript to find the input field and type text
        driver.execute_script("""
            let inputField = document.querySelector('input.u-input');
            if (inputField) {
                inputField.value = 'hello_world_1'; // Set the value
                inputField.dispatchEvent(new Event('input', { bubbles: true })); // Trigger input event
            }
        """)
        print("Text typed into input field!")

        # Use JavaScript to find and click the button
        driver.execute_script("""
            let button = document.querySelector('button.u-button-primary');
            if (button) {
                button.click();
            }
        """)
        print("Button clicked!")

        # Wait for 10 seconds before executing the final JavaScript code
        time.sleep(10)
        print("Waiting period is over.")

        # JavaScript to execute after the page loads
        js_code = """
        function simulateKeypress(element, key) {
            var event = new KeyboardEvent('keydown', {
                bubbles: true,
                cancelable: true,
                key: key,
                code: `Key${key.toUpperCase()}`,
                charCode: key.charCodeAt(0),
                keyCode: key.charCodeAt(0),
                which: key.charCodeAt(0)
            });
            element.dispatchEvent(event);
        }
        var element = document.querySelector('div[placeholder="Send a message..."]');
        if (element) {
            console.log('Element found:', element);
            setInterval(() => {
                    var message = "ajgar madarch*d hai " + Math.floor(Math.random() * 1000).toString();
                    element.textContent = message;
                    console.log('Message set:', message);
                    simulateKeypress(element, 'Enter');
                    console.log('Enter keypress simulated');
            }, 5000); // 1000 milliseconds = 1 second
        } else {
            console.log('Element not found');
        }
        """

        # Execute the JavaScript code
        driver.execute_script(js_code)
        print("JavaScript code executed!")

        time.sleep(25)
    finally:
        # Close the driver
        driver.quit()

while True:
    main()

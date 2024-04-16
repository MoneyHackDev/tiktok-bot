import os
import json
import time
from colorama import init, Fore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

init(autoreset=True)


class Bot:
    def __init__(self):
        os.system("cls" if os.name == "nt" else "clear")
        print(Fore.YELLOW + "[~] Loading driver, please wait...")

        try:
            options = Options()
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")
            self.driver = webdriver.Chrome(options=options)
            print(Fore.GREEN + "[+] Driver loaded successfully\n")
        except Exception as e:
            print(Fore.RED + f"[!] Error loading driver: {e}")
            exit()

        self.url = "https://zefoy.com"
        self.config_file = "config.json"
        self.services = {
            "followers": {"title": "Followers", "xpath": "/html/body/div[6]/div/div[2]/div/div/div[2]/div/button"},
            "hearts": {"title": "Hearts", "xpath": "/html/body/div[6]/div/div[2]/div/div/div[3]/div/button"},
            "comment_hearts": {"title": "Comment Hearts", "xpath": "/html/body/div[6]/div/div[2]/div/div/div[4]/div/button"},
            "views": {"title": "Views", "xpath": "/html/body/div[6]/div/div[2]/div/div/div[5]/div/button"},
            "shares": {"title": "Shares", "xpath": "/html/body/div[6]/div/div[2]/div/div/div[6]/div/button"},
            "favorites": {"title": "Favorites", "xpath": "/html/body/div[6]/div/div[2]/div/div/div[7]/div/button"},
        }

    def start(self):
        self.load_config()
        self.driver.get(self.url)
        print(Fore.MAGENTA + "[!] In case of a 502 Bad Gateway error, please refresh the page\n")

        self.wait_for_element(self.services["followers"]["xpath"])
        print(Fore.GREEN + "[+] Captcha completed successfully\n")

        self.driver.minimize_window()
        self.check_services()
        self.print_services()

        while True:
            try:
                choice = int(input(Fore.YELLOW + "[-] Choose an option: "))
                if 1 <= choice <= len(self.services):
                    self.select_service(choice)
                    self.save_config()
                    break
            except ValueError:
                continue

    def select_service(self, choice):
        service_key = list(self.services.keys())[choice - 1]
        self.driver.find_element(By.XPATH, self.services[service_key]["xpath"]).click()

        print()
        video_url = input(Fore.MAGENTA + "[-] Video URL: ").strip()
        self.save_config(video_url=video_url)
        print()

        self.start_service(video_url)

    def start_service(self, video_url):
        while True:
            div_xpath = f"//div[contains(@class, 'service') and contains(@style, 'display: block')]"
            div = self.driver.find_element(By.XPATH, div_xpath)
            
            url_input = div.find_element(By.TAG_NAME, 'input')
            url_input.clear()
            url_input.send_keys(video_url)

            search_btn = div.find_element(By.TAG_NAME, 'button')
            search_btn.click()

            remaining_time = self.check_remaining_time(div)

            if remaining_time:
                print(Fore.YELLOW + f"[~] Sleeping for {remaining_time} seconds")
                time.sleep(remaining_time)

    def check_remaining_time(self, div):
        try:
            remaining_time_elem = div.find_element(By.XPATH, "./div/span[1]")
            remaining_time_text = remaining_time_elem.text

            if "Please wait" in remaining_time_text:
                minutes = int(remaining_time_text.split()[2])
                seconds = int(remaining_time_text.split()[5])
                return (minutes * 60) + seconds + 5
        except NoSuchElementException:
            pass
        return None

    def check_services(self):
        for service in self.services:
            xpath = self.services[service]["xpath"]
            try:
                element = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                self.services[service]["status"] = Fore.GREEN + "[WORKING]"
            except TimeoutException:
                self.services[service]["status"] = Fore.RED + "[OFFLINE]"

    def wait_for_element(self, xpath, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                return
            except TimeoutException:
                retries += 1
                print(Fore.YELLOW + f"[~] Retrying... ({retries}/{max_retries})")
        print(Fore.RED + f"[!] Element not found after {max_retries} retries. Exiting.")
        exit()

    def print_services(self):
        for index, service in enumerate(self.services, start=1):
            title = self.services[service]["title"]
            status = self.services[service]["status"]
            print(Fore.BLUE + f"[{index}] {title.ljust(20)} {status}")

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
                if "video_url" in config:
                    print(Fore.YELLOW + f"[~] Last Video URL: {config['video_url']}")
                # Optionally load and use previous service choice if needed

    def save_config(self, video_url=None):
        config = {}
        if video_url:
            config["video_url"] = video_url

        with open(self.config_file, "w") as f:
            json.dump(config, f)
            print(Fore.GREEN + "[+] Configuration saved successfully")


if __name__ == "__main__":
    bot = Bot()
    bot.start()

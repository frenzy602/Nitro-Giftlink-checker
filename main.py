import requests
from colorama import Fore, init
import os
import time
import random
import threading
from queue import Queue, Empty
from datetime import datetime
import pytz
import json
from keyauth import api  # Correct import for the keyauth package

# Initialize colorama for colored output
init()

# Initialize KeyAuth with API 1.3 (no secret needed, as per your dashboard)
keyauthapp = api(
    name="giftlink checker",
    ownerid="P3SwDvik2n",
    version="1.0"
)

# Initial counts
valid_count = 0
claimed_count = 0
invalid_count = 0
unknown_count = 0

# Lock for thread-safe counter updates
count_lock = threading.Lock()

# Load configuration from config.json
def load_config():
    config_file = "config.json"
    default_config = {"Proxieless": True, "LicenseKey": ""}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
        except json.JSONDecodeError:
            print(Fore.RED + "Error: Invalid config.json file. Using default settings.")
            return default_config
    else:
        return default_config

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

config = load_config()
proxieless = config.get("Proxieless", True)
stored_key = config.get("LicenseKey", "")

def addcount(counter):
    global valid_count, claimed_count, invalid_count, unknown_count
    with count_lock:
        if counter == "valid":
            valid_count += 1
        elif counter == "claimed":
            claimed_count += 1
        elif counter == "invalid":
            invalid_count += 1
        elif counter == "unknown":
            unknown_count += 1
        update_window_title()

def update_window_title(timer=None):
    title = f".gg/Frenzyst Nitro Checker | Valid: {valid_count} | Claimed: {claimed_count} | Invalid: {invalid_count} | Unknown: {unknown_count}"
    if timer is not None:
        title += f" | Countdown: {timer} Seconds"
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except:
        print(title)

class Utils:
    @staticmethod
    def file_has_content(filename):
        if not os.path.exists(filename):
            return False
        if os.path.getsize(filename) > 0:
            return True
        return False
    
    @staticmethod
    def get_formatted_proxy(filename):
        if not Utils.file_has_content(filename):
            raise ValueError("proxies.txt is empty or does not exist.")
        proxy = random.choice(open(filename, encoding="cp437").read().splitlines()).strip()
        if '@' in proxy:
            return proxy
        elif len(proxy.split(':')) == 2:
            return proxy
        else:
            if '.' in proxy.split(':')[0]:
                return ':'.join(proxy.split(':')[2:]) + '@' + ':'.join(proxy.split(':')[:2])
            else:
                return ':'.join(proxy.split(':')[:2]) + '@' + ':'.join(proxy.split(':')[2:])

def time_difference_in_words(date_string):
    try:
        date = datetime.fromisoformat(date_string)
        now = datetime.now(pytz.utc)
        date = date.replace(tzinfo=pytz.utc)
        time_difference = date - now
        seconds = time_difference.total_seconds()
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"In {hours} Hrs"
        elif minutes > 0:
            return f"In {minutes} Mins"
        elif seconds > 0:
            return f"In {seconds} Secs"
        else:
            return "Now"
    except ValueError:
        return "Idk Bro"

def file_has_content(filename):
    return os.path.exists(filename) and os.path.getsize(filename) > 0

def clear_file(filename):
    with open(filename, "w") as file:
        file.truncate(0)

start_time = None

def authenticate():
    global config, stored_key
    
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(Fore.CYAN + """
██████╗░██╗███████╗████████╗  ░█████╗░██╗░░██╗███████╗░█████╗░██╗░░██╗███████╗██████░
██╔════╝░██║██╔════╝╚══██╔══╝  ██╔══██╗██║░░██║██╔════╝██╔══██╗██║░██╔╝██╔════╝██╔══██╗
██║░░██╗░██║█████╗░░░░░██║░░░  ██║░░╚═╝███████║█████╗░░██║░░╚═╝█████═╝░█████╗░░██████╔╝
██║░░╚██╗██║██╔══╝░░░░░██║░░░  ██║░░██╗██╔══██║██╔══╝░░██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗
╚██████╔╝██║██║░░░░░░░░██║░░░  ╚█████╔╝██║░░██║███████╗╚█████╔╝██║░╚██╗███████╗██║░░██║
░╚═════╝░╚═╝╚═╝░░░░░░░░╚═╝░░░  ░╚════╝░╚═╝░░╚═╝╚══════╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
                                                                 By - @Frenzybtp
    """)
    
    # Initialize KeyAuth application (API 1.3)
    try:
        keyauthapp.init()
    except Exception as e:
        print(Fore.RED + f"Failed to initialize KeyAuth: {str(e)}")
        input("Press Enter to exit...")
        exit()

    # Check stored key if it exists and isn't empty
    if stored_key and stored_key.strip():
        print(Fore.CYAN + "Verifying stored license key...")
        try:
            if keyauthapp.check(stored_key):  # Use `check` for API 1.3 license validation
                print(Fore.GREEN + "Authenticated with stored license key!")
                time.sleep(1)
                return True
            else:
                print(Fore.YELLOW + "Stored key invalid, please enter a new one")
        except Exception as e:
            print(Fore.YELLOW + f"Error verifying stored key: {str(e)}")
    
    # Prompt for new key
    print(Fore.CYAN + "[1] Enter Your License Key")
    choice = input(Fore.WHITE + "Enter your choice: ")
    
    if choice == "1":
        key = input(Fore.WHITE + "Enter license key: ")
        try:
            if keyauthapp.check(key):  # Use `check` for API 1.3 license validation
                print(Fore.GREEN + "Authentication successful!")
                config["LicenseKey"] = key
                save_config(config)
                stored_key = key
                time.sleep(1)
                return True
            else:
                print(Fore.RED + "Invalid license key!")
                input("Press Enter to try again...")
                return authenticate()
        except Exception as e:
            print(Fore.RED + f"Authentication failed: {str(e)}")
            input("Press Enter to try again...")
            return authenticate()
    else:
        print(Fore.RED + "Invalid choice!")
        time.sleep(1)
        return authenticate()

def display_main_menu():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(Fore.CYAN + """
██████╗░██╗███████╗████████╗  ░█████╗░██╗░░██╗███████╗░█████╗░██╗░░██╗███████╗██████░
██╔════╝░██║██╔════╝╚══██╔══╝  ██╔══██╗██║░░██║██╔════╝██╔══██╗██║░██╔╝██╔════╝██╔══██╗
██║░░██╗░██║█████╗░░░░░██║░░░  ██║░░╚═╝███████║█████╗░░██║░░╚═╝█████═╝░█████╗░░██████╔╝
██║░░╚██╗██║██╔══╝░░░░░██║░░░  ██║░░██╗██╔══██║██╔══╝░░██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗
╚██████╔╝██║██║░░░░░░░░██║░░░  ╚█████╔╝██║░░██║███████╗╚█████╔╝██║░╚██╗███████╗██║░░██║
░╚═════╝░╚═╝╚═╝░░░░░░░░╚═╝░░░  ░╚════╝░╚═╝░░╚═╝╚══════╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
                                                                 By - @Frenzybtp
    """)
    print(Fore.CYAN + "[1] Start Gift Link Checker")
    choice = input(Fore.WHITE + "Enter your choice: ")
    if choice == "1":
        begin_checking()
    else:
        display_main_menu()

def begin_checking():
    global start_time
    start_time = datetime.now()
    
    url = "https://google.com"
    try:
        if proxieless:
            requests.get(url)
        else:
            proxy = Utils.get_formatted_proxy("proxies.txt")
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            requests.get(url, proxies=proxies)
        time.sleep(0.4)
    except requests.exceptions.ConnectionError:
        input("You are not connected to the internet, check your connection and try again.\nPress enter to exit")
        exit()
    except ValueError as e:
        print(Fore.RED + str(e))
        input("Press Enter to exit...")
        exit()

    if not Utils.file_has_content("input/GiftCodes.txt"):
        input("The input/GiftCodes.txt File Doesn't Exist Or Is Empty.\nPress Enter To Exit...")
        exit()

    if not proxieless and not Utils.file_has_content("proxies.txt"):
        print(Fore.RED + "Error: proxies.txt is empty or does not exist, but Proxieless is False.")
        input("Press Enter to exit...")
        exit()

    output_files = ["output/ValidCodes.txt", "output/UsedGifts.txt", "output/InvalidCodes.txt", "output/UnknownCodes.txt"]
    if any(file_has_content(filename) for filename in output_files):
        print(Fore.CYAN + "[!] Files In Output Have Some Content Wanna Clear Them? (y/n): ", end="")
        clear_response = input(Fore.WHITE)
        if clear_response.lower() == "y":
            print(Fore.WHITE + "Output>")
            for filename in output_files:
                if file_has_content(filename):
                    print(Fore.WHITE + filename)
                    clear_file(filename)
            print(Fore.GREEN + "Files cleared!")
        else:
            print(Fore.WHITE + "Output>")
            for filename in output_files:
                if file_has_content(filename):
                    print(Fore.WHITE + filename)
            print(Fore.GREEN + "Files not cleared!")

    gift_codes = []
    print(Fore.CYAN + "[!] Do You Wanna Delete Duplicated Gift Links? (y/n): ", end="")
    reply = input(Fore.WHITE)
    with open("input/GiftCodes.txt", "r") as file:
        gift_codes = file.read().splitlines()
    if reply.lower() == "y":
        gift_codes = list(set(gift_codes))
        if not gift_codes:
            raise ValueError("Error: GiftCodes.txt is empty after removing duplicates.")
        with open("input/GiftCodes.txt", "w") as file:
            file.write('\n'.join(gift_codes))
        print(Fore.GREEN + "Duplicated links deleted!")

    hidden_valids = False
    print(Fore.CYAN + "[!] Do You Want The Codes Of Valid Gift Links To Be Hidden? (y/n): ", end="")
    respond = input(Fore.WHITE)
    if respond.lower() == "y":
        hidden_valids = True
        print(Fore.GREEN + "Valid codes will be hidden!")

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    process_gift_codes(gift_codes, hidden_valids)

def check_discord_gift_code(code, hidden_valids, queue):
    current_time = datetime.now().strftime("%H:%M:%S")
    url = f"https://discordapp.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true"
    
    try:
        if proxieless:
            response = requests.get(url)
        else:
            proxy = Utils.get_formatted_proxy("proxies.txt")
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            response = requests.get(url, proxies=proxies)
        
        if response.status_code == 200:
            data = response.json()
            uses = data.get("uses", 0)
            expiration = data["expires_at"]
            time_left = time_difference_in_words(expiration)
            plan = data["subscription_plan"]["name"]
            if uses == 0:
                if hidden_valids:
                    masked_code = code[:-4] + "****"
                    print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.GREEN}[+] Valid  [ Nitro -> {plan}  https://discord.gift/{masked_code}  [{Fore.GREEN}{time_left}{Fore.LIGHTBLACK_EX}]")
                else:
                    print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.GREEN}[+] Valid  [ Nitro -> {plan}  https://discord.gift/{code}  [{Fore.GREEN}{time_left}{Fore.LIGHTBLACK_EX}]")
                with open("output/ValidCodes.txt", "a") as valid_file:
                    valid_file.write(f"https://discord.gift/{code}\n")
                addcount("valid")
            else:
                print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.YELLOW}[-] CLAIMED ->  https://discord.gift/{code}")
                with open("output/UsedGifts.txt", "a") as used_file:
                    used_file.write(f"https://discord.gift/{code}\n")
                addcount("claimed")
        elif response.status_code == 429:
            print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.CYAN}[!] Rate Limited | Retrying...")
            rate_limit_reset = response.headers.get('X-RateLimit-Reset')
            if rate_limit_reset:
                time_to_wait = max(1, int(rate_limit_reset) - int(time.time()))
                time.sleep(time_to_wait)
            else:
                time.sleep(1)
            check_discord_gift_code(code, hidden_valids, queue)
        elif response.status_code == 404:
            print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.RED}[-] Invalid ->  https://discord.gift/{code}")
            with open("output/InvalidCodes.txt", "a") as invalid_file:
                invalid_file.write(f"https://discord.gift/{code}\n")
            addcount("invalid")
        else:
            print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.RED}[?] Unknown ->  https://discord.gift/{code}")
            with open("output/UnknownCodes.txt", "a") as unknown_file:
                unknown_file.write(f"https://discord.gift/{code}\n")
            addcount("unknown")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.RED}[!] Error with {code}: {str(e)}")
        addcount("unknown")
    
    queue.task_done()

def worker(queue, hidden_valids):
    while True:
        try:
            code = queue.get_nowait()
            check_discord_gift_code(code, hidden_valids, queue)
        except Empty:
            break

def process_gift_codes(gift_codes, hidden_valids):
    queue = Queue()
    num_threads = min(50, len(gift_codes))

    for code in gift_codes:
        if code.startswith("https://discord.gift/"):
            code = code.replace("https://discord.gift/", "")
        queue.put(code)

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(queue, hidden_valids))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    elapsed_time_str = ""
    if int(hours) > 0:
        elapsed_time_str += f"{int(hours)} hour{'s' if int(hours) > 1 else ''} "
    if int(minutes) > 0:
        elapsed_time_str += f"{int(minutes)} minute{'s' if int(minutes) > 1 else ''} "
    elapsed_time_str += f"{int(seconds)} second{'s' if int(seconds) > 1 else ''}"
    
    current_time = datetime.now().strftime("%H:%M:%S")
    print(Fore.WHITE + "\n")
    print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.CYAN}[~] Successfully Checked {valid_count + claimed_count + invalid_count + unknown_count} Gift Links In {elapsed_time_str}")
    print(f"{Fore.LIGHTBLACK_EX}[{current_time}] {Fore.CYAN}[~] Valid : {valid_count} | Already Claimed : {claimed_count} | Invalid : {invalid_count} | Unknown : {unknown_count}")
    print(Fore.WHITE + "\n")
    input("Press Enter to exit...")
    
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    display_main_menu()

if __name__ == "__main__":
    if authenticate():
        display_main_menu()
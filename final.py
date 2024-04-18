import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import requests
import os
from selenium.webdriver.common.keys import Keys
import urllib.request


# Load credentials
credentials = {}
with open('facebook_credentials.txt') as file:
    for line in file:
        key, value = line.strip().split('=')
        credentials[key] = value
user_ids = []
id = "355575617485053"
access_token = "EAAGfynRZCFqIBO1GErZASVr48Vn7qJm01o4U8YKdWNclHFE52F0fCbos62pAsXU7cvk9JLx6yG0oefdOcWCZA4538W9ZBAjiJPbQ3RlOOcLy8U0TfaSA6Hcvhzaxibp8qo1ZAb7nlPeOKc7epiozMx5nWqJAQkT4ZAbzk9CrIkTeIlcTDQ2ZB81m2mUA3MySfJpxHZCyKwMKRZAogcxp0y0Ai8RJ3HX6wI0aKeDwUHzZBZBRuNpbZCZAvexgy"
# Initialize WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.page_load_strategy = 'normal'
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)


# chrome_options = webdriver.ChromeOptions()
# chrome_options.page_load_strategy = 'normal'
# prefs = {"profile.default_content_setting_values.notifications": 2}
# chrome_options.add_experimental_option("prefs", prefs)
# driver = webdriver.Chrome(options=chrome_options)
# Function definitions (Aboutinfo, contactinfo, extract_image_links, extract_name) go here
def Aboutinfo():
    profile_info = {
        "Workplace": [],
        "Studies": "Not provided",
        "Lives in": "Not provided",
        "From": "Not provided"
    }

    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='x1hq5gj4']//span[@dir='auto']"))
        )
        text_elements = driver.find_elements(By.XPATH, "//div[@class='x1hq5gj4']//span[@dir='auto']")
        
        for element in text_elements:
            text = element.text.strip()
            if " and " in text or "Works at" in text or " at" in text or " works" in text:
                profile_info["Workplace"].append(text)
            # if text.startswith("Works at"):
            #     profile_info["Workplace"] = text.replace("Works at", "").strip()
            elif text.startswith("Studied at") or text.startswith("Studies at"):
                profile_info["Studies"] = text.replace("Studied at", "").replace("Studies at", "").strip()
            elif text.startswith("Lives in"):
                profile_info["Lives in"] = text.replace("Lives in", "").strip()
            elif text.startswith("From"):
                profile_info["From"] = text.replace("From", "").strip()

    except TimeoutException:
        print("Timed out waiting for page to load")

    return [profile_info[key] for key in ["Workplace", "Studies", "Lives in", "From"]]

# contacts
def contactinfo(heading_text):
    try:
        contact_and_basic_info_link = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'about_contact_and_basic_info')]"))
        )
        contact_and_basic_info_link.click()

        heading = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{heading_text}')]"))
        )
        # The section containing the links and text you're interested in is the sibling of the heading
        section = heading.find_element(By.XPATH, "./following-sibling::div | ./following::div")

        # Initialize an empty list to hold the text and links
        content = []

        # Extracting text
        texts = section.find_elements(By.XPATH, ".//span[not(a)]")
        for text in texts:
            content.append(text.text)

        # Extracting links
        links = section.find_elements(By.XPATH, ".//a")
        for link in links:
            # Getting the text and href for each link
            link_text = link.text
            link_href = link.get_attribute('href')
            content.append(f"{link_text}: {link_href}")

        return content if content else ["No information to show"]
    except NoSuchElementException:
        return ["Information not found"]
def extract_image_links(name):
    cover_image_link = ''
    profile_image_link = ''

    try:
        # Find the profile cover image element using XPath and get its src attribute
        cover_img_element = driver.find_element(By.XPATH, "//img[@data-imgperflogname='profileCoverPhoto']")
        cover_image_link = cover_img_element.get_attribute("src")
        print("Cover image link extracted:", cover_image_link)
        urllib.request.urlretrieve(cover_image_link, f"C:\\Users\\lenovo\\Desktop\\imgs\\{name}_cover.jpg")
        current = driver.current_url
        # Find the profile image element using XPath and get its src attribute
        element = driver.find_element(By.XPATH,f"//a[@aria-label='{name}']")

# Get the value of the href attribute
        href_value = element.get_attribute("href")
        driver.get(href_value)
        img_element = driver.find_element(By.XPATH, "//img[@data-visualcompletion='media-vc-image']")

# Get the src attribute value
        img_src = img_element.get_attribute("src")
        print("Profile image link extracted:", img_src)
        urllib.request.urlretrieve(img_src, f"C:\\Users\\lenovo\\Desktop\\imgs\\{name}_profile.jpg")

        # After performing the right-click action, you can perform further actions such as clicking on a context menu item.
        # For example, to click on a context menu item with a specific XPath:
        # context_menu_item = driver.find_element_by_xpath("xpath_of_context_menu_item")
        # context_menu_item.click()

    except NoSuchElementException as e:
        print("Image link not found:", e)

    return cover_image_link, profile_image_link
def extract_name():
    try:
        # Assuming the first h1 tag within a span with dir="auto" consistently contains the name.
        name_element_xpath = "//div[contains(@class, 'x1e56ztr')]//span[contains(@class, 'x193iq5w')]/h1"
        name_element = driver.find_element(By.XPATH, name_element_xpath)
        name = name_element.text.strip()
        if name:
            print("Name extracted:", name)
            return name
        else:
            
            print("Found the name element, but it contains no text.")
            return "Name not provided"
    except NoSuchElementException as e:
       
        print("Name element not found:", e)
        return "Name not provided"

def append_data_to_csv(file_path, data):
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:  # Append mode
        writer = csv.writer(file)
        writer.writerow(data)

def login():
    driver.get("http://www.facebook.com")
    driver.maximize_window()
    username = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Email address or phone number']")))
    password = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Password']")))
    username.clear()
    username.send_keys("ireg.member67@gmail.com")
    password.clear()
    password.send_keys("ZXCVB@123")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
    time.sleep(10)
    print(" Log in Successfully!")

def navigate_to_group():
    group_url = "https://www.facebook.com/groups/localbusinessownersusa/"
    driver.get(group_url)
    time.sleep(5)  


def collect_member_urls(driver, max_scrolls=10):
    member_urls = set()
    people = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[text()='People']"))
    )
    ActionChains(driver).move_to_element(people).click().perform()
    time.sleep(5)

    scrolls = 0
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(5)

        member_elements = driver.find_elements(By.XPATH, "//h2[contains(., 'New to the group')]/following::div[contains(@class, 'x1q0g3np')]//a[@role='link']")
        for element in member_elements:
            name = element.text  # Assuming the member's name is the text of the anchor tag
            member_url = element.get_attribute('href')
            member_urls.add((name, member_url))  # Store as tuple

        scrolls += 1
        print(f"Scroll: {scrolls}, Members found: {len(member_urls)}")

    return member_urls
    

def process_member_data(driver, member_data, csv_file_path):
    name, url = member_data 
    try:
        # print(f"Processing member {name} with URL: {url}")
        driver.get(url)
        # user_id = url.split('/')[-2]
        # user_ids.append(user_id)
        # graph = facebook.GraphAPI(access_token)

        # pic = graph.get_object(user_id, fields = "picture")
        # image_url = str(pic['picture']['data']['url'])
        # print(image_url)
        # mydata = requests.get(image_url)
        # with open(f"profile_picture_{user_id}.jpg", 'wb') as file:
        #     file.write(mydata.content)
        #     print("Image saved")
    # View profile
        view_profile_button = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//span[text()='View profile']"))
                )
        driver.execute_script("arguments[0].click();", view_profile_button)
        print("At view")
                 # about
        about_profile_button = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, "//span[text()='About']")))
        driver.execute_script("arguments[0].click();", about_profile_button)
        print("at about")
        time.sleep(4)
                    # Scroll down a bit
        driver.execute_script("window.scrollBy(0, 100);")  
        time.sleep(15)
        name = extract_name()
        about_data = Aboutinfo()
        contact_info_data = contactinfo("Contact info")
        websites_and_links_data = contactinfo("Websites and social links")
        basic_info_data = contactinfo("Basic info")
        cover_image_link, profile_image_link = extract_image_links(name)
        admin_info = [
                        name,
                        about_data[0],
                        about_data[1],
                        about_data[2],
                        about_data[3],
                        websites_and_links_data,
                        contact_info_data,
                        basic_info_data,
                        cover_image_link,
                        profile_image_link
                    ]
        append_data_to_csv(csv_file_path, admin_info)
    except Exception as e:
        print(f"An error occurred while processing ({name}, {url}): {e}")
def download_image(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved as {file_path}")
    else:
        print(f"Failed to download image from {url}")

def download_profile_images(user_id):
    # Fetch user's profile picture
    profile_picture_url = f"https://graph.facebook.com/{user_id}/picture?type=large"
    download_image(profile_picture_url, f"profile_picture_{user_id}.jpg")

    # Fetch user's cover photo
    cover_photo_url = f"https://graph.facebook.com/{user_id}?fields=cover&access_token={access_token}"
    response = requests.get(cover_photo_url)
    if response.status_code == 200:
        cover_photo_data = response.json().get('cover')
        if cover_photo_data:
            cover_photo_url = cover_photo_data['source']
            download_image(cover_photo_url, f"cover_photo_{user_id}.jpg")
        else:
            print(f"User {user_id} does not have a cover photo.")
    else:
        print(f"Failed to fetch cover photo for user {user_id}")


           
if __name__ == "__main__":
    try:
        
        login()
        navigate_to_group()
        # CSV file setup
        csv_file_path = 'final.csv'
        # Prepare CSV header
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Workplace", "Studies", "Lives In", "From", "Websites and Links", "Contact Info", "Basic Info", "Cover Image Link", "Profile Image Link"])

        member_urls = collect_member_urls(driver, max_scrolls=10)
        for member_data in member_urls:
            try:
                process_member_data(driver, member_data, csv_file_path)
            except Exception as e:
                print(f"Error processing {member_data[1]}: {e}")

        #print(user_ids)
    except Exception as e:
        print(f"A general error occurred: {e}")
    finally:
        driver.quit()
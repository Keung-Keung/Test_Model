from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Chrome 옵션 설정
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# WebDriver 서비스 설정
service = Service(ChromeDriverManager().install())

browser = webdriver.Chrome(service=service, options=options)
browser.get("https://www.fragrantica.com/notes/")

df = pd.DataFrame(columns=['Note', 'Image'])
time.sleep(5)

notes = browser.find_elements(By.CLASS_NAME, 'notebox')
images = browser.find_elements(By.CSS_SELECTOR, ".notebox img[src]")

data = []

for note, image in zip(notes, images):
    data.append({'Note': note.text, 'Image': image.get_attribute('src')})

new_df = pd.DataFrame(data)

df = pd.concat([df, new_df], ignore_index=True)

browser.close()

df.to_csv("note_img.csv", index=False)
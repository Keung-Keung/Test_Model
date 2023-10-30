import urllib.request
import time
import os
import csv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
options = Options()

headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
}

browser = webdriver.Chrome("chromedriver",options=options)
browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
# 브랜드별 향수 정보 가져오기
site_url = "https://www.fragrantica.com/parent-company/"
site_name = os.getenv('SITE_NAME')
browser.get(site_url)

company_name = browser.find_elements_by_css_selector("div.countrylist.cell.small-6.large-4 > a")
company_names = ['+'.join(brand.text.split()) for brand in company_name]  # 공백 +처리 - 링크 대로 만든 것
time.sleep(2)
print(company_names)  # 총 481개 회사 있음.
print(len(company_names))
browser.close()

all_brand_names = []
#각 회사별 웹사이트에 접속해서 브랜드 이름 가져오기
for company in company_names[:1]:
    browser = webdriver.Chrome("chromedriver", options=options)
    company_url = f"https://www.fragrantica.com/parent-company/{company}.html"
    browser.get(company_url)
    time.sleep(2)

    #브랜드 이름 추출
    brand_name = browser.find_elements_by_css_selector("div.designerlist.cell.small-6.large-4 > a")
    brand_names = ['-'.join(brand.text.split()) for brand in brand_name]  # 공백 하이픈(-)처리
    all_brand_names.extend(brand_names)
    print(brand_names)
    browser.close()
    print(all_brand_names)

    # csv 파일 생성
    file = open("fragrantica.csv", mode="w", encoding="utf-8", newline="")
    writer = csv.writer(file)
    writer.writerow(["perfume name", "gender", "brand name", "image", "main accord",
                     "description", "top note", "middle note", "base note"])


    # 1. 브랜드별 향수 목록 가져오기
    for brand in all_brand_names:
        browser = webdriver.Chrome("chromedriver", options=options)
        link = f"https://www.fragrantica.com/designers/{brand}.html"
        browser.get(link)

        try:
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR,
                              'body div#main-content div#brands div.cell.text-left.prefumeHbox.px1-box-shadow div.flex-child-auto h3 a'))
            WebDriverWait(browser, 10).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")

        all_perfume_url = []
        for i in browser.find_elements_by_css_selector(
            'body div#main-content div#brands div.cell.text-left.prefumeHbox.px1-box-shadow div.flex-child-auto h3 a'):
            perfume_url = i.get_attribute("href")
            all_perfume_url.append(perfume_url)
        for i in all_perfume_url:
            print(i)
        print(len(all_perfume_url))
        print()
        time.sleep(2)
        browser.close()

    # 2. 특정 향수 정보 가져오기
    for perfume_url in all_perfume_url[:2]:
        browser = webdriver.Chrome("chromedriver", options=options)
        browser.get(perfume_url)
        time.sleep(2)

        perfume_accord_list = []
        top_note = []
        attribute_error_count = 0

        #body 내부 main content 발췌
        main_content = browser.find_elements_by_css_selector(
            'div.grid-x.bg-white.grid-padding-x.grid-padding-y')

        for content in main_content:
            # 향수 이름 + 성별 분리
            perfume_name = content.find_element_by_css_selector('div#toptop > h1').text
            perfume_name, _, gender = perfume_name.partition(' for ')
            print(f'향수 이름 : {perfume_name}, 성별: {gender}')
            time.sleep(2)

            # 향수 이미지
            perfume_img = content.find_element_by_css_selector(
                'div.cell.small-6.text-center div.cell.small-12 img').get_attribute("src")
            urllib.request.urlretrieve(perfume_img, perfume_name + ".jpg")
            print(f'향수 이미지 : {perfume_img}')
            time.sleep(2)

            # main accord 목록
            accord_bars = content.find_elements_by_css_selector('div.accord-bar')
            for accord_bar in accord_bars:
                accord_text = accord_bar.text
                style = accord_bar.get_attribute('style')

                for s in style.split(';'):
                    if ' width' in s:
                        width = s.split(':')[1].strip()
                        break  # width 값을 찾았으면 반복 종료
                perfume_accord_list.append(accord_text + ' ' + width)
            print(f'main accord : {perfume_accord_list}')
            time.sleep(2)

            # 향수 스토리 본문
            perfume_story_raw = content.find_element_by_css_selector('div[itemprop=description]')
            p_tags = perfume_story_raw.find_elements_by_tag_name('p')
            perfume_story = ' '.join([p.text for p in p_tags])
            description = perfume_story.split("Read")[0].strip()
            print('향수 스토리 요약 : {}'.format(description))

            # 향수 노트(top/middle/bottom)
            perfume_notes_raw = content.find_elements_by_css_selector(
                'div#pyramid div.cell div div[style^="display: flex"]')

            top_raw = perfume_notes_raw[1]
            top_note = top_raw.text.split('\n')
            position = 'TOP' if len(perfume_notes_raw) > 1 else 'SINGLE'
            print('향수 top 노트 목록: {}'.format(', '.join(top_note)))

            if len(perfume_notes_raw) > 1:
                middle_raw = perfume_notes_raw[2]
                middle_note = middle_raw.text.split('\n')
                print('향수 middle 노트 목록 : {}'.format(middle_note))

                base_raw = perfume_notes_raw[3]
                base_note = base_raw.text.split('\n')
                print('향수 bottom 노트 목록 : {}'.format(base_note))
        writer.writerow([perfume_name, gender, brand, perfume_img, ', '.join(perfume_accord_list), description, ', '.join(top_note),
             ', '.join(middle_note), ', '.join(base_note)])
        print('--------------------------------------------------------------------')
        browser.close()

file.close()
print("저장을 완료했습니다.")
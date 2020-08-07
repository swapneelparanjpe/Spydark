from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url = "http://127.0.0.1:8000/login"
username = "..."
password = "..."

browser = webdriver.Chrome("chromedriver_win32\chromedriver.exe")
browser.get(url)

input_fields = browser.find_elements_by_xpath("//input")
submit_btn = browser.find_element_by_xpath("//button[@type='submit']")

ids = []
for input_field in input_fields:
    ids.append(input_field.get_attribute("id"))

i=0
entry = [username, password]
for id_ in ids:
    try:
        elem = browser.find_element_by_id(id_)
        elem.send_keys(entry[i])
        i+=1
    except:
        pass
submit_btn.send_keys(Keys.ENTER)  

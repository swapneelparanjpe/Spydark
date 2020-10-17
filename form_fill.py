from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url = "................"
username = "..."
password = "..."
firstname = "..."
lastname = "..."
email = "..."

browser = webdriver.Chrome("chromedriver_win32\\chromedriver.exe")
browser.get(url)

input_fields = browser.find_elements_by_xpath("//input")
#submit_btn = browser.find_element_by_xpath("//button[@type='submit']")

names = []
# for input_field in input_fields:
#     names.append(input_field.get_attribute("type"))
# print(names)
count = 0
for input_field in input_fields:
    name = input_field.get_attribute("name")
    if name == 'username':
        input_field.send_keys("EEEEEEEE")
        count+=1
    elif name == 'password' or name == 'pass':
        input_field.send_keys("PPPPPPP")
        count+=1
    elif name == 'firstname':
        input_field.send_keys("TTTT")
        count+=1
    elif name == 'lastname':
        input_field.send_keys("TTTT")
        count+=1
    elif name == 'email':
        input_field.send_keys("TTTT")
        count+=1
    elif name == 'username':
        input_field.send_keys("TTTT")
        count+=1
print(count)
# i=0
# entry = [username, password]
# for id_ in ids:
#     try:
#         elem = browser.find_element_by_id(id_)
#         elem.send_keys(entry[i])
#         i+=1
#     except:
#         pass
# submit_btn.send_keys(Keys.ENTER)  

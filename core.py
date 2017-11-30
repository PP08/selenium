from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from selenium.webdriver.chrome.options import Options
import threading
import json
import re


url = 'http://soha.vn/video.htm'
domain = re.search(r'(http|https):\/\/(.*?)/', url).group(0)[:-1]
desired = DesiredCapabilities.CHROME
desired['loggingPrefs'] = {'browser': 'ALL'}
chrome_options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
# chrome_options.add_argument("--headless")
# chrome_options.add_argument('no-sandbox')
browser = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities=desired)
browser.implicitly_wait(30)
browser.get(url)
responseURLs = []

browser.execute_script('$( document ).ajaxSend(function(event, jqxhr, settings) { \
                                  console.info(settings.url) \
                                });')

# menu = browser.find_element_by_class_name('video-menu')



# xpath = '//*[@id="video-paging"]/a[2]'
# page = browser.find_element_by_xpath(xpath)
# actions1 = ActionChains(browser)
# actions1.move_to_element_with_offset(page, 0, 0)
# actions1.click(page)
# actions1.perform()


links = browser.find_elements_by_xpath('//*[@id="admWrapsite"]/div[3]/div/div[3]/div[1]/ul/li')
for link in links:
    actions = ActionChains(browser)
    actions.move_to_element_with_offset(link, 0, 0)
    actions.click(link)
    actions.perform()

    time.sleep(3)

    for i in range(3):
        # xpath = '//*[@id="video-paging"]/a[{}]'.format(i)
        # page = browser.find_element_by_xpath(xpath)
        # print(page)
        #
        button = browser.find_element_by_id('btnViewMore')
        actions1 = ActionChains(browser)
        actions1.move_to_element_with_offset(button, 0, 0)
        actions1.click(button)
        actions1.perform()
        time.sleep(3)

time.sleep(5)


logs = browser.get_log('browser')
domain = re.search(r'(http|https):\/\/(.*?)/', url).group(0)[:-1]
test = []
indicators = ["laytinmoitronglist", "trang-", "loadListNews", "page-", "page=", "Page", "loadListByPage",
              "LoadListTinTrongNgay", "pageindex", "GetNewestVideoByZone", "video/latest/"]
for el in logs:
    if any(x in el["message"] for x in indicators):
        # url = domain + el["message"].split("\"")[1]
        test.append(el["message"])
print(list(set(test)))

# for t in ['vmenu_0', 'vmenu_49', 'vmenu_112', 'vmenu_110', 'vmenu_111']:
#     button = browser.find_element_by_id(t)
#     # button.click()
#     # print(button.text)
#     actions = ActionChains(browser)
#     actions.move_to_element_with_offset(button, 3, 0)
#     actions.click(button)
#     actions.perform()
#     time.sleep(5)
browser.quit()
    
    
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging, sys, time

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# Create headless web browser
logging.info("Creating headless Chrome browser")
chrome_options = Options()  
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.implicitly_wait(10)

# Login Page:
logging.info("Loading https://my.pltw.org...")
driver.get("https://my.pltw.org/")
username = driver.find_element_by_name('login_username')
password = driver.find_element_by_name('login_password')
login    = driver.find_element_by_id('login')
print("Login to https://my.pltw.org")
username.send_keys(raw_input("Username: "))
password.send_keys(raw_input("Password: "))
logging.info("Logging in...")
login.click()
driver.find_element_by_link_text("Community")

# CSP Members Page
logging.info("Loading CSP Members page...")
driver.get("https://community.pltw.org/s/relatedlist/0F91J000000Id6lSAC/GroupMembers")
def member_count(driver):
    text = driver.find_element_by_class_name("countSortedByFilteredBy").get_attribute('textContent').strip()
    return text.split(" ")[0]
while member_count(driver) == "":
    time.sleep(.5)

# CSP Members Table
logging.info("Scrolling...")
members_table = driver.find_element_by_class_name("forceRecordLayout")
members_table = members_table.find_element_by_tag_name("tbody")
members_rows = members_table.find_elements_by_tag_name("tr")
logging.info(member_count(driver))
current_count = member_count(driver)
while '+' in current_count:
    if current_count != member_count(driver):
        current_count = member_count(driver)
        logging.info(member_count(driver))
    members_rows = members_table.find_elements_by_tag_name("tr")
    members_rows[-1].location_once_scrolled_into_view
    time.sleep(.5)
logging.info("Loaded "+str(member_count(driver))+" members")

# Parse Members Rows
logging.info("Cataloging rows...")
member_urls = {}
members_rows = members_table.find_elements_by_tag_name("tr")
for row in members_rows:
    link = row.find_element_by_class_name("outputLookupLink")
    name = link.get_attribute("title")
    url  = link.get_attribute("href")
    member_urls[url] = name

# Open Output File
filename = "member-data.csv"
print("Writing to "+filename)
file = open(filename, 'w')
file.write("URL,Location\n")

# Members Profiles
for url in member_urls.keys():
    logging.info("Loading "+url+"...")
    driver.get(url)
    driver.find_element_by_class_name("forceCommunityUserProfileDetail")
    data_divs = driver.find_elements_by_class_name("uiOutputTextArea")
    while len(data_divs) < 2:
        logging.info("Waiting...")
        time.sleep(.5)
        data_divs = driver.find_elements_by_class_name("uiOutputTextArea")
    name = member_urls[url]
    role = data_divs[0].get_attribute('textContent').strip()
    location = data_divs[1].get_attribute('textContent').strip()
    file.write(url+',"'+location+'"\n')

logging.info("Done outputting "+len(member_urls)+" profiles.")

file.close()
driver.quit()

# https://chrome.google.com/webstore/detail/geocode-by-awesome-table/cnhboknahecjdnlkjnlodacdjelippfg?utm_source=permalink
# https://www.google.com/earth/outreach/learn/visualize-your-data-on-a-custom-map-using-google-my-maps/

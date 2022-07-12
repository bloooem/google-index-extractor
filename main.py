import os
import shutil
import urllib.parse
import sys
import requests

sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

from selenium import webdriver

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def uploadtojwplayer(upload_link):
  url = "https://api.jwplayer.com/v2/sites/" + jwsitename + "/media/"
  payload = {"upload": {
          
          "method": "fetch",
          "download_url": upload_link
      }}
  headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": auth
  }
  
  response = requests.post(url, json=payload, headers=headers)
  response.raise_for_status()
  # access JSOn content
  jsonResponse = response.json()
  media_id = jsonResponse["id"]
  media_title = jsonResponse["metadata"]["title"]
  cdn_url = "https://cdn.jwplayer.com/players/" + media_id + ".html"
  if cdn_url != "":
    print("------------------------------------")
    print(media_title)
    print(cdn_url)
  else:
    print("error uploading")
def getLinks(pageUrl, path):
    all_links_text = ""
    dirs = ""
    driver.get(pageUrl)
    try:
      WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, "mdui-progress")))
    except:
      print("Site took too long to load")
      sys.exit()
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

    page_source = BeautifulSoup(html, 'html.parser')
    tags_a_list = page_source.find('ul').find_all_next('a')


    for link in tags_a_list:

        currentLink = domain + str(link.get('href'))
        # checking whether currentLink is a link to folder or file

        # link to folder
        if currentLink[-1] == '/':
            sublink = currentLink[:currentLink.rindex('/')]
            dirname = sublink[sublink.rindex('/') + 1:]

            print(dirname)

            dirs = dirs + dirname + '\n'  # puts the name of currently made dir in dirs
           
           #might need to modify this code (don't know if it works)
            # if os.path.exists(path + dirname):
            #     shutil.rmtree(path + dirname)
            # os.makedirs(path + dirname)

            getLinks(currentLink, path + dirname + "/")

        # Else it is a link to file
        else:
            new_current_link = currentLink.replace("?a=view", "").replace(" ", "%20") + "\n"
            uploadtojwplayer(new_current_link) #uncomment this line if you don't want to upload to jw player
            all_links_text = all_links_text + currentLink.replace("?a=view", "").replace(" ", "%20") + "\n"

    # writing all links to links.txt
    if all_links_text != "":
        all_links_text = all_links_text[:all_links_text.rindex('\n')]
        fileLinks = open("links.txt", 'w')
        fileLinks.write(all_links_text)
        fileLinks.close()

URL = input("Enter the URL: ")
if URL[-1]!="/":
  URL = URL + "/"
password = input("Enter password if any. Else press enter: ")
path = input("Enter the path to empty directory to store files: ") #should work fine without path to store links if not a folder dir is given
jwsitename = input("Enter your jw player id if you want yo upload media to jw player: ")
auth = input("enter your jw player api auth key:")

if path[-1]!='/':
  path = path + "/"

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver',options=options)

if password:
  try:
      print("\n\n::Checking Authentication::")
      driver.get(URL)
      WebDriverWait(driver,5).until(EC.alert_is_present(),'Timed out waiting for alerts to appear')
      obj = driver.switch_to.alert
      obj.send_keys(password)
      obj.accept()
      print("\n::Authentication Successful::")
  except:
      print("\n::Authentication Error::")


domain = URL.split(".dev")[0] + ".dev" #get domain name from URL
getLinks(URL, path)
driver.quit()
from selenium import webdriver
from src.myfunctions import Scrape as mfs

#how I installed Selenium
#https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/


main_url = 'https://www.ultimatetennisstatistics.com'
endpoint = '/rankingsTable'
ranking_url = main_url + endpoint

players_url_path = 'data/scraped_dataset/players_url.json' #path to save json file
players_info_path = 'data/scraped_dataset/players_info.json' #path to save json file with actual players info

scraper = mfs(webdriver.Chrome()) #creates the driver Objetct

scraper.driver.get(ranking_url) #goes to ranking page


scraper.scrape_players_urls(players_url_path) #scrapes links of all players found in ranking between 2020 and 2000


scraper.scrape_players_info(main_url, players_url_path, players_info_path)  #scrapes info and saves them in json file


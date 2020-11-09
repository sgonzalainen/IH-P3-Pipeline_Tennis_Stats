from selenium import webdriver
from src.func.scraping_functions import Scrape as scrape

#how I installed Selenium
#https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/


main_url = 'https://www.ultimatetennisstatistics.com'
endpoint = '/rankingsTable'
ranking_url = main_url + endpoint

scraper = scrape(webdriver.Chrome()) #creates the driver Objetct

scraper.driver.get(ranking_url) #goes to ranking page

players_url_path = 'data/scraped_dataset/players_url.json' #path to save json file

print('Start scraping players urls')

scraper.scrape_players_urls(players_url_path) #scrapes links of all players found in ranking between 2020 and 2000



players_info_path = 'data/scraped_dataset/players_info.json' #path to save json file with actual players info

print('Start scraping players info')

response = scraper.scrape_players_info(main_url, players_url_path, players_info_path)  #scrapes info and saves them in json file

if response == False:
    print('Problem when scraping players info. Most likely reached max requests of website. Retry about an hour later. Progress saved.\n')
else:
    print('Scrape of players stats done.\n')


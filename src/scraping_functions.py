import re
import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import tqdm
import json





class Scrape():
    '''
    Collection of functions used for scraping the website  'https://www.ultimatetennisstatistics.com'
    '''

    def __init__(self, driver):
        self.driver = driver


    def select_year(self, year):
        '''
        From ranking webpage, selects year in dropdown list to display ranking

        Args:
            year(int)
        
        Returns:

        '''

        year = str(year)
        select = Select(self.driver.find_element_by_id('season'))
        select.select_by_value(year)

    
    def extend_table(self):
        '''
        Extends table of players in ranking to all

        Args:

        Returns:


        '''

        self.driver.find_element_by_xpath('//*[@id="rankingsTable-header"]/div/div/div[5]/div[1]/button').click()
        self.driver.find_element_by_xpath('//*[@id="rankingsTable-header"]/div/div/div[5]/div[1]/ul/li[4]/a').click()

    
    
    def select_stats(self):
        '''
        Inside player page, selects stats ribbon
        Args:

        Returns:

        '''
        self.driver.find_element_by_xpath('//*[@id="playerPills"]/li[9]/a').click()
        self.driver.find_element_by_xpath('//*[@id="statisticsPill"]').click()


    def extract_players_url(self, players_urls):
        '''
        From ranking page, goes through html content, extracts all players links and adds to dictionary if new player found
        Args:
            players_urls(dict): dictionary of players in use

        Returns:
            players_urls(dict): dictionary of players updated


        '''
    
        page = self.driver.page_source
        soup = BeautifulSoup(page, features="lxml")

        players_html = soup.find('tbody').find_all('a')
        for player in players_html:

            if player.text in players_urls:
                continue

            else:
                name = player.text
                url_path = player['href']

                players_urls[name] = url_path
        
        return players_urls


    def get_player_profile(self):
        '''
        Inside player page, scrapes all info related to player profile

        Args:

        Returns:
            temp_dict(dict): dictionary with all profile data


        '''

    
        temp_dict = {}
        
        page = self.driver.page_source
        soup = BeautifulSoup(page ,features="lxml")
        
        try:
            
            player_html = soup.find_all('table', class_='table table-condensed text-nowrap')[0] #I keep only the first table
        
        except IndexError:
            print(f'There was a problem and data for this player  {self.driver.current_url} could not be retrieved')
            return 0
        
        else:
            rows = player_html.find_all('tr')

            for row in rows:
                col_name = row.find('th').text
                value = row.find('td').text

                temp_dict[col_name] = value

            return temp_dict

    def get_player_stats(self):
        '''
        Inside a player page, goes to player stats and scrapes all the data.

        Args:

        Returns:
            temp_dict(dict): dictionary with all stats data

        '''
        
        temp_dict = {}
        self.select_stats()
        
        
        time.sleep(1) #needed to get time to refresh and get soup
        
        page = self.driver.page_source
        soup = BeautifulSoup(page, features="lxml")
        
        
        

        player_html = soup.find_all('table', class_='table table-condensed table-hover table-striped')
        
        for table in player_html[0:3]:#I want only first three tables
            
            

            rows = table.find_all('tr')

            for row in rows[1:]: #first row is a header

                col_name = row.find('td').text
                value = row.find('th').text

                temp_dict[col_name] = value
            
        return temp_dict


    def scrape_players_urls(self, filepath, end_year = 2020, first_year = 1999):
        '''
        From ranking page, goes through all years, extracts all unique players urls and saves them as a json file
        Args:
            filepath(str): filepath to save the json file
            end_year(int): by default 2020
            first_year(int): by defaul 1999
        Returns:



        '''
        players_urls = {}
        for year in range(end_year,first_year,-1):
            time.sleep(3)
            self.select_year(year)
            self.extend_table()
            time.sleep(2)
            players_urls = self.extract_players_url(players_urls)

        with open(filepath, 'w') as fp:
            json.dump(players_urls, fp)

        print(f'{filepath} saved')

    def scrape_players_info(self, main_url, filepath_url, filepath_info):

        '''
        Opens json file with info about url links to each player and scrapes all wanted information. Finally, saves all info in json.
        If error 429 for exceeding max number of requests, saves the info until that point. Next time it will continue at same place.

        Args:
            main_url(str): main url
            filepath_url(str): filepath to json file with url info
            filepath_info(str): filepath to save json file with players info

    
        '''

        count = 0
        try:
            df = pd.read_json(filepath_info)
        except ValueError: #first time it does not exist
            scraped_players = []
            data = []
        
        else:
            scraped_players = df.name.to_list()
            data = list(df.to_dict('index').values()) #to get already scraped players
        
        finally:

            with open(filepath_url, "r") as read_file:
                players_urls = json.load(read_file)


            for player, endpoint in tqdm.tqdm(players_urls.items()):
                
                if player in scraped_players:
                    continue
                else:
                
                    
                    player_url = main_url + endpoint
                    self.driver.get(player_url)

                    profile_dict = self.get_player_profile() #scrape profile data

                    if profile_dict == 0: #this when there was an error

                        with open(filepath_info, 'w') as fp:
                            json.dump(data, fp)
                            return False

                    else:    

                        stats_dict = self.get_player_stats() #scrape stats data

                        

                        profile_dict.update(stats_dict)

                        profile_dict.update({'name': player})

                        data.append(profile_dict)
                        

                        count += 1

                        if count % 20 == 0:

                            with open(filepath_info, 'w') as fp:
                                json.dump(data, fp)

                            print(f'A save copy of {filepath_info} saved')

                with open(filepath_info, 'w') as fp:
                        json.dump(data, fp)
                print(f'Done. {filepath_info} saved')
                



import pandas as pd
import re
import json
import numpy as np


'''
Collection of functions used for cleaning datasets
'''


def set_opponent(row, main_player):
    '''
    Determines the opponent of a specific main player from dataset

    Args:
        row(dataframe): row dataframe from apply function
        main_player(str): main player

    Returns:
        opponent(str)

    '''
    if row.Loser != main_player:
        return row.Loser
    else:
        return row.Winner


def is_winner(value, main_player):
    '''
    Determines if main player won or not that game

    Args:
        value(str): value in dataframe
        main_player(str): main player

    Returns:
        boolean

    '''

    if value == main_player:
        return True
    else:
        return False

def filter_games(df, main_player):
    '''
    Filters whole datasets and returns only games in which main player is present

    Args:
        df(DataFrame): the whole dataset
        main_player(str): main player

    Returns:
        df(DataFrame): dataset filtered

    '''

    df = df.loc[(df.Winner == main_player) | (df.Loser == main_player)]

    return df


def match_id_players(df, df_1):
    '''
    Given the two different dataframes, find matches between players names (which are in different format) for later insertion of player stats to dataset

    Args:
        df(Dataframe): Dataset from Kaggle
        df_1(Dataframe): Players stats from scraping

    Returns:
        df['player_id]: new column with player_id unified between two dataframes

    '''
    #First let's finde match by surname if surname is unique among players

    surname_dict_count = df_1.name.apply(lambda x: x.rsplit(' ',1)[-1]).value_counts().to_dict() #dict with value_counts as key to see if are unique or not

    def match_single_surname(name, surname_dict_count):
        '''
        Function to use in pandas apply to find matches by unique surname.
        Args:
            name(str): full name player in Kaggle dataset
            surname_dict_count(dict): Keys: surname, Values: number of appearance of that surname among players
        
        Returns:
            match_name(str): match_id or 'No match'


        '''

        name = name.split(' ',1)[0] #which is the surname

        cond = (name in surname_dict_count) and (surname_dict_count.get(name) == 1)   

        if cond:
            match_name = df_1[df_1["name"].str.find(name) > 0].name.to_list()[0]
            return match_name
        else:
            return 'No match'
        
    df['player_id'] = df.Opponent.apply(lambda x: match_single_surname(x, surname_dict_count))

    #Now let's find matches by converting full name in Surname I. 
    name_surname_dict = df_1.name.apply(lambda x: x.split(' ',1)[1]+' '+x.split(' ',1)[0][0]+'.').value_counts().to_dict() #dict with value counts to see if surname + X. are unique or not
        
    def match_name_surname(row, name_surname_dict):
        '''
        Function to use in pandas apply to find matches by unique surname + initial
        Args:
            row(dataframe): row dataframe from apply function
            name_surname_dict(dict): Keys: 'surname X.' Values: number of appearance of that surname plus initial among players

        Returns:
            match_name(str): match_id or 'No match'

        '''



        name = row['Opponent']
        if (name in name_surname_dict) and (name_surname_dict.get(name) == 1):
            
            surname = name.split(' ',1)[0]
            initial = name.split(' ',1)[1].rsplit('.',1)[0]
            
            for player in df_1['name'].to_list():
                cond =  len(re.findall(r'\b' + re.escape(initial)+'.*'+re.escape(surname), player)) > 0
                
                if cond:
                    
                    return player
                else:
                    pass

        else:
            return 'No match'

    df['player_id'] = df.apply(lambda x: match_name_surname(x, name_surname_dict) if x.player_id == 'No match' else x.player_id, axis = 1)

    #Last let's find out extra matches by replacing '-' in double surnames
    surname_comb_list = df_1.name.apply(lambda x: x.split(' ',1)[-1]).to_list() #This time no dict since chances of having two same surnames is quite low

    def match_surname_union(row, surname_comb_list):
        '''
        Function to use in pandas apply to find matches in double surnames
        Args:
            row(dataframe): row dataframe from apply function
            surname_comb_list(list): list of first two words in player stats dataframe
        
        Returns:
            match_name(str): match_id or 'No match'

        '''
        name = row['Opponent']
        name = name.replace('-',' ')
        surname = name.rsplit(' ',1)[0] #I keep as surname first two words '
        
        if surname in surname_comb_list:
            match_name = df_1[df_1["name"].str.find(surname) > 0].name.to_list()[0]
            
            return match_name
        
        else:
            return 'No match'

    df['player_id'] = df.apply(lambda x: match_surname_union(x, surname_comb_list) if x.player_id == 'No match' else x.player_id, axis = 1)

    #Finally let's fix these two last players by hand
    df['player_id'] = np.where(df['Opponent'] == 'Del Potro J.M.', 'Juan Martin Del Potro', df['player_id'])
    df['player_id'] = np.where(df['Opponent'] == 'Bautista R.', 'Roberto Bautista Agut', df['player_id'])


    return df['player_id']



import pandas as pd
import re
import numpy as np
from src.myfunctions import Clean as mfc

print('Starting to clean datasets')

players_info_path = 'data/scraped_dataset/players_info.json' #path json file with players info
main_player =  'Nadal R.' #player to study
clean_dataset_path = 'data/dataset_clean.pkl'


# Cleaning Kaggle dataset

df = pd.read_csv('data/kaggle_dataset/Data.csv', engine='python')
df = df.iloc[:,0:26] #rest of columns are related to bets. 
df = mfc.filter_games(df, main_player) #filter games with main player in match
df['Opponent'] = df.apply(lambda x: mfc.set_opponent(x,main_player), axis = 1) #to specify opponent
df['Is_winner'] = df.Winner.apply(lambda x: mfc.is_winner(x, main_player)) #to specify if main player won or not


#Cleaning Players stats Dataframe

df_1 = pd.read_json(players_info_path)
df_1.Height = df_1.Height.apply(lambda x: str(x).replace('cm','').strip()) #cleaning height column
df_1.Weight = df_1.Weight.apply(lambda x: str(x).replace('kg','').strip()) #cleaning weigth column
df_1 = df_1.apply(lambda x: [str(elem).replace('%','').strip() if '%' in str(elem) else elem for elem in x ]) #remove % from values
#list of columns to convert string to float
columns_num = ['Ace %', 'Double Fault %', '1st Serve %',
       '1st Serve Won %', '2nd Serve Won %', 'Break Points Saved %',
       'Service Points Won %', 'Service Games Won %', 'Ace Against %',
       'Double Fault Against %', '1st Srv. Return Won %',
       '2nd Srv. Return Won %', 'Break Points Won %', 'Return Points Won %',
       'Return Games Won %', 'Points Dominance', 'Games Dominance',
       'Break Points Ratio', 'Total Points Won %', 'Games Won %', 'Sets Won %',
       'Matches Won %']

df_1[columns_num] = df_1[columns_num].apply(lambda x: [ None if ele =='' else float(ele) if ele != None else None for ele in x])

#find ace% threshold of players categorized as good serve
ace_threshold = df_1['Ace %'].quantile(0.85)

df_1['great_serve'] = df_1['Ace %'].dropna().apply(lambda x: True if float(x) > ace_threshold else False)


#Find match id
df['player_id'] = mfc.match_id_players(df, df_1)


#Merge of two dataframes

print('Starting to merge datasets')

df_games_merge = df.drop(['Winner', 'Loser', 'W1', 'L1', 'W2', 'L2', 'W3', 'L3', 'W4', 'L4', 'W5', 'L5','Comment'], axis = 1) #drop columns not to be used

df_players_merge = df_1[['name','Country','Plays', 'Backhand', 'great_serve']] #drop columns not to be used

players_dataset_clean = 'data/players_stats_clean.pkl' #save a copy of clean datasets of all players 


df_players_merge.to_pickle(players_dataset_clean)
print(f'Clean dataset with players stats successfully saved in {players_dataset_clean} ')



clean_df = pd.merge(df_games_merge, df_players_merge,  how='left', left_on='player_id', right_on = 'name')

clean_df['Opponent'] = np.where(clean_df['player_id'] == 'No match', clean_df['Opponent'], clean_df['name']) #Replace in opponent column name from scraping which is not truncated

clean_df = clean_df.drop(['player_id','name'], axis =1) #delete redundant columns

clean_df.to_pickle(clean_dataset_path)

print(f'Clean and merged games dataset successfully saved in {clean_dataset_path} ')


























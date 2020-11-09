import pandas as pd
from src.func.plotting_functions import Plot as myplot


print('Plotting graphs....')

#Load dataset games
clean_dataset_path = 'data/dataset_clean.pkl'
df = pd.read_pickle(clean_dataset_path)

#Load dataset player stats
clean_players_path = 'data/players_stats_clean.pkl'
df_players = pd.read_pickle(clean_players_path)

#Plots wins/loses based on surface
myplot.plot_surface_win(df)

#Plots loses details
myplot.plot_losses_detail(df)


#plots most defeated nationalities
myplot.plot_top_countries_defeated(df)

#plots top nemesis players
myplot.plot_top_nemesis(df)

#plots stats aces all players
myplot.plot_box_aces(df_players)

print('Plots created!\n')





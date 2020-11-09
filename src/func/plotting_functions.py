import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from iso3166 import countries
import matplotlib.image as mpimg
from matplotlib.transforms import TransformedBbox
from matplotlib.transforms import Bbox
from matplotlib.image import BboxImage
from matplotlib.legend_handler import HandlerBase
import matplotlib.patches as patches




class Plot():
    '''
    Collection of functions used for cleaning datasets
    '''
    
    
    def plot_surface_win(df):

        '''
        Plots wins and loses based on surface
        Args:
            df(Dataframe): clean dataset
        Returns:

        '''

        fig = plt.figure()
        ax = fig.add_subplot(111)
        sns.countplot(x=df.Surface, hue =df.Is_winner, hue_order = [True, False])


        #PLot customization
        ax.legend(labels = ['Win', 'Lost'])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.ylabel('Number of games') 
        plt.xlabel('') 
        plt.title('In %, Win Rate', fontsize = 18, pad = 20)

        #to show percentage of win
        for pos, surface in enumerate(df.Surface.unique()):
            wins = df[(df.Surface == surface)].Is_winner.sum()
            total = df[(df.Surface == surface)].Is_winner.count()
            number = round((wins / total) * 100,1)
            plt.text(pos +0.2, wins + 5, f'{number} %',fontsize = 13, ha = 'right')

            
        filename = 'output/img/wins_surface.png'

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)


    def plot_losses_detail(df):
        '''
        Plots losses percentage based on opponent is great server and leftie
        Args:
            df(Dataframe): clean dataset
        Returns:

        '''
        # new column with boolean values if leftie or not
        df['leftie'] = np.where(df['Plays'] == 'Left-handed', 1, np.where(df['Plays'] == 'Right-handed', 0, np.NaN))

        total_df = df.dropna(subset=['Plays']).groupby(['Surface','leftie','great_serve']).count()[['ATP']] #this is to know total number of games per surface, great server and leftie
        #In b dataframe we count number of wins
        b = df.dropna(subset=['Plays']).groupby(['Surface','leftie','great_serve']).sum()[['Is_winner']].reset_index()

        def get_total_games(row, total_df):
            '''
            Mini function to get in b dataframe total number of games based on surface, great server and leftie
            Args:
                row(dataframe): row dataframe from apply function
                total_df(Dataframe): dataframe with total number of games info
            Returns:
                total(int): number of games

            '''
            surface = row['Surface']
            leftie = row['leftie']
            great_serve = row['great_serve']
            
            total = total_df.loc[surface].loc[leftie].loc[great_serve]
            return total
        
        b['total'] = b.apply(lambda x: get_total_games(x,total_df), axis = 1)

        def get_rate_loss(row):
            '''
            Mini function to get rate loss in b dataframe 
            Args:
                row(dataframe): row dataframe from apply function

            Returns:
                loss_perc(float): rate loss



            '''
            surface = row['Surface']
            leftie = row['leftie']
            great_serve = row['great_serve']
            
            
            
            
            total = row['total']
            
            loss_perc = (total - row['Is_winner']) / total * 100
            
            return loss_perc

        b['loss_perc'] = b.apply(lambda x: get_rate_loss(x), axis = 1)

        #Here comes the actual plotting

        fig = plt.figure()
        ax = fig.add_subplot(111)

        sns.scatterplot(x = b.Surface, y = b.loss_perc, hue = b.great_serve, style = b.leftie, size = b.total, sizes =(60, 60))

        handles, labels = ax.get_legend_handles_labels()

        handles = handles[1:3]+ handles[-2:]
        new_labels = ['Server Specialist', 'Regular Player', 'Right-handed', 'Left-handed']

        ax.legend(handles,new_labels, bbox_to_anchor=(1.4, 0.75), loc='upper right')

        plt.ylabel('Loss %') 
        plt.xlabel('') 

        plt.title('Losses details', fontsize = 18, pad = 20)

        filename = 'output/img/losses_details.png'

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)

    def plot_top_countries_defeated(df):
        '''
        Plots top countries defeated by main player
        Args:
            df(Dataframe): clean dataset
        Returns:

        '''
        a = df.groupby('Country').sum().reset_index().sort_values('Is_winner', ascending =False).head(5).sort_values('Is_winner') #reorder to get top1 at the top in plot 

                        
        def pos_image(x, y, pays, haut):
            '''
            Function from stackoverflow to show countries flat

            Args:
                x(float): position in x axis
                y(float): position in y axis
                pays(str): country to look in iso3166
                haut(float): height of bar
            
            Returns:

            '''

            #https://stackoverflow.com/questions/61971090/how-can-i-add-images-to-bars-in-axes-matplotlib
            
            pays = pays.strip()
            if pays == 'United States':
                pays = 'US'
            else:
                pass
            
        
            
            pays = countries.get(pays).alpha2.lower()
            fichier = "/usr/share/iso-flags-png-320x240"
            fichier += f"/{pays}.png"
            im = mpimg.imread(fichier)
            ratio = 25
            w = ratio * haut
            ax.imshow(im, extent = (x -w, x, y  , y + haut), aspect = 'auto', zorder = 2)


        #Here comes the plotting 

        fig, ax = plt.subplots()

        haut= 0.9

        r = ax.barh(y = a.Country, width = a.Is_winner, height = haut, zorder=1)

        countries_list = list(a.set_index('Country').Is_winner.reset_index().to_records(index=False))

        y_bar = [rectangle.get_y() for rectangle in r]

        ax.set_xlim([0, 130])
        ax.set_ylim([-.7, 4.5])

        for country, y in zip(countries_list, y_bar):

            pos_image(country[1], y, country[0], haut)
            
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)

        plt.xlabel('Number of victories') 

            
        #ax.invert_yaxis() #to get top1 at the top

        plt.title('Top 5 defeated nationalities', fontsize = 18, pad = 20)

        filename = 'output/img/top_countries_defeated.png'

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)

        
        
    ## In order to show images as legends
    ##From this thread with some changes https://stackoverflow.com/questions/26029592/insert-image-in-matplotlib-legend##


    class ImageHandler(HandlerBase):

        def create_artists(self, legend, orig_handle,
                        xdescent, ydescent, width, height, fontsize,
                        trans):

            # enlarge the image by these margins
            sx, sy = self.image_stretch 

            # create a bounding box to house the image
            bb = Bbox.from_bounds(xdescent - sx,
                                ydescent - sy,
                                width + sx,
                                height + sy)

            tbb = TransformedBbox(bb, trans)
            image = BboxImage(tbb)
            image.set_data(self.image_data)

            self.update_prop(image, orig_handle, legend)

            return [image]

        def set_image(self, image_path, image_stretch=(9, 9)):


            self.image_data = plt.imread(image_path)

            self.image_stretch = image_stretch


    def plot_top_nemesis(df):
        '''
        Plots top nemesis of main player
        Args:
            df(Dataframe): clean dataset
        Returns:

        '''
        wins = df.groupby('Opponent').sum().Is_winner
        total = df.groupby('Opponent').count().Is_winner
        losses = total - wins
        losses_df = losses.sort_values(ascending = False).head(5).reset_index() #This is the dataframe from where to plot


        fig = plt.figure(figsize=(11.5, 10))
        ax = fig.add_subplot(111)

        nemesis_list = losses_df.Opponent.unique()

        list_plot = []
        legend_text = []
        handler_map = {}

        for player in nemesis_list:
            surname = player.split()[1]

            plot = plt.scatter([], [])
            list_plot.append(plot)
            custom_handler = Plot.ImageHandler()
            custom_handler.set_image(f"src/img/{surname}.jpg",image_stretch=(120, 120))
            handler_map[plot]=custom_handler

            games_lost = int(losses_df.set_index('Opponent').loc[player,'Is_winner'])

            legend_text.append(f'\n{player}\n{games_lost} matches.')


        plt.legend(list_plot,
        legend_text,
        handler_map=handler_map,
        labelspacing=10,
        columnspacing = 10,
        frameon=False,
        bbox_to_anchor=(0.2, 0.17), loc='lower left',
        ncol = 2,
        fontsize = 15)


        #####################################################################

        plt.title('Top 5 Nemesis', fontsize = 18, pad = 20)

        ax.axis('off')


        filename = 'output/img/top_nemesis.png'

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)

    def plot_box_aces(df_players):
        '''
        Plots boxplot with stats all players Aces% and reports main player stat
        Args:
            df_players(DataFrame): players stats dataframe clean

        Returns:
        
        '''

        main_player = 'Rafael Nadal'

        main_player_aces = round(df_players.set_index('name').loc[main_player,'Ace %'],1)

        

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        sns.boxplot(y = df_players['Ace %'], color='white', width=.4)

        #To turn all in black lines
        # https://stackoverflow.com/questions/43434020/black-and-white-boxplots-in-seaborn
        plt.setp(ax.lines, color='k')
        plt.setp(ax.artists, edgecolor = 'k', facecolor='w')


        for line in ax.lines:
            line.set_color('black')
            line.set_mfc('black')
            line.set_mec('black')

        #main player line

        x_coordinates = [-0.5,0.2]
        y_coordinates = [main_player_aces, main_player_aces]
        plt.plot(x_coordinates, y_coordinates, color ='r', linestyle = 'dashed')


        ###Legend######
        list_plot = []
        legend_text = []
        handler_map = {}

        plot = plt.scatter([], [])
        list_plot.append(plot)
        custom_handler = Plot.ImageHandler()
        handler_map[plot]=custom_handler

        surname = main_player.split()[1]


        custom_handler.set_image(f"src/img/{surname}.jpg",image_stretch=(100, 120))
        legend_text.append(f'\n\n\n{main_player}\n\n{main_player_aces} % Aces.')

        plt.legend(list_plot,
        legend_text,
        handler_map=handler_map,
        labelspacing=10,
        columnspacing = 10,
        frameon=False,
        bbox_to_anchor=(1, 0.5), loc='lower left',
        ncol = 2,
        fontsize = 20)

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        plt.title('Ace % Distribution', fontsize = 18, pad = 20)

        filename = 'output/img/aces_detail.png'

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)
        


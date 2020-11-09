main_player = 'Rafael Nadal'

print(f'Welcome to {main_player} Stats Genertor\n')

while True:

    answer = input('What would you like to do?\n\
                    Press 0 to update players stats by scraping\n\
                    Press 1 to clean datasets\n\
                    Press 2 to generate new report\n\
                    Press other key to escape\n')

    if answer == '0':
        exec(open("./src/scrape.py").read())

    elif answer == '1':
        exec(open("./src/clean.py").read())

        
    elif answer == '2':
        exec(open("./src/plot.py").read())

    else:
        print(f'Closing {main_player} Stats Generator')
        exit()    

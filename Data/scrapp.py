import pandas as pd
import pickle
from string import ascii_uppercase as alphabet

all_tables = pd.read_html('https://en.wikipedia.org/wiki/2022_FIFA_World_Cup')

dict_table = {}
for letter, i in zip(alphabet, range(10,10*6,7)):
    df = all_tables[i] # Acquire Group tables
    df.rename(columns={df.columns[1]:'Team'}) # renaming column from 'Teamvte' to "Team"
    df.pop('Qualification') # remove 'Qualification'
    dict_table[f'Group {letter}'] = df # adding the processed table as a df to the dictionary

print(dict_table.keys())

with open('dict_table', 'wb') as output:
    pickle.dump(dict_table, output)
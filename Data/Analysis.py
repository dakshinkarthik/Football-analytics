import pandas as pd
import pickle
from scipy.stats import poisson
from string import ascii_uppercase as alphabet

# read data
df_fix = pd.read_csv('clean_fifa_worldcup_fixture.csv')
df_past = pd.read_csv('clean_fifa_worldcup_matches.csv')

# split data into home and away
df_home = df_past[['HomeTeam', 'HomeGoals', 'AwayGoals']]
df_away = df_past[['AwayTeam', 'HomeGoals', 'AwayGoals']]

# rename columns
df_away = df_away.rename(columns={'AwayTeam':'Team', 'HomeGoals':'GoalsConceded', 'AwayGoals':'GoalsScored'})
df_home = df_home.rename(columns={'HomeTeam':'Team', 'HomeGoals':'GoalsScored', 'AwayGoals':'GoalsConceded'})

# strength computed based on average of goals scored and goals conceded by each country
df_strength = pd.concat([df_home, df_away], ignore_index=True).groupby('Team').mean()

# print(df_strength.sort_values(by='GoalsConceded', ascending=False))
# print(df_strength.at['Argentina','GoalsScored'])

# Predict points scored in a match between two countries based on number of goals scored and conceded, using a poisson distribution
def predict_points(home,away):
    
    if home in df_strength.index and away in df_strength.index:
        # goals scored * goals conceded as lambda for the game between home and away
        lamb_home = df_strength.at[home,'GoalsScored'] * df_strength.at[away,'GoalsConceded']
        lamb_away = df_strength.at[away,'GoalsScored'] * df_strength.at[home,'GoalsConceded']
        prob_home, prob_away, prob_draw = 0,0,0
        for x in range(0,5): # goals scored by home team
            for y in range(0,5): # goals scored by away team
                # poission distribution is used here to compute the probability of goals scored
                p = poisson.pmf(x, lamb_home) * poisson.pmf(y, lamb_away)
                if x == y:
                    prob_draw += p
                elif x > y:
                    prob_home += p
                else:
                    prob_away += p
        
        # 3 points for every win, 1 point for draw
        points_home = 3*prob_home + prob_draw # possible points for home team
        points_away = 3*prob_away + prob_draw # possible points for away team
        
        return (points_home, points_away)
    
    else:
        return (0,0)
    
df_fix_group = df_fix[:48].copy()
df_fix_KO = df_fix[48:56].copy()
df_fix_qf = df_fix[56:60].copy()
df_fix_sf = df_fix[60:62].copy()
df_fix_f = df_fix[62:].copy()

with open('dict_table', 'rb') as file:
    dict_table = pickle.load(file)
    
    
# Simulating group stages
for group in dict_table.keys():
    teams = dict_table[group]['Team'].values
    df_games_6 = df_fix_group[df_fix_group['home'].isin(teams)]
    for index, row in df_games_6.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away = predict_points(home, away)
        dict_table[group].loc[dict_table[group]['Team'] == home, 'Pts'] += points_home
        dict_table[group].loc[dict_table[group]['Team'] == away, 'Pts'] += points_away
        
    dict_table[group] = dict_table[group].sort_values('Pts', ascending=False).reset_index()
    dict_table[group] = dict_table[group][['Team', 'Pts']]
    dict_table[group] = dict_table[group].round(0)
    
   
# Simulating KO stages

# Modifying KO fixture list based on group winners and runners
for letter, group in zip(alphabet, dict_table.keys()):
    winner = (dict_table[group]['Team'][0])
    runner = (dict_table[group]['Team'][1])
    df_fix_KO.replace({f'Winners Group {letter}':winner, f'Runners-up Group {letter}':runner}, inplace=True)
    # print(f'Winners Group {letter}')

df_fix_KO['Winner'] = '?'    

# Uses predict_points() to predict winners in KO 
def get_winner(df):
    for index, row in df.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away = predict_points(home, away)
        if points_home > points_away:
            winner = home
        elif points_home < points_away:
            winner = away
        df.loc[index, 'Winner'] = winner
    return df

df_fix_KO = get_winner(df_fix_KO)

# Simulating quarter-finals

# Modifying QF list based on KO winners
for index, row in df_fix_KO.iterrows():
    match_df = row['score']
    df_fix_qf.replace({f'Winners {match_df}': row['Winner']}, inplace=True)

# print(df_fix_KO)

df_fix_qf['Winner'] = '?'
df_fix_qf = get_winner(df_fix_qf) # Method used to predict winners in KO stages can be used here

# Simulating semi-finals

# Modifying QF list based on semi-finalists
for index, row in df_fix_qf.iterrows():
    match_df = row['score']
    df_fix_sf.replace({f'Winners {match_df}': row['Winner']}, inplace=True)

# print(df_fix_KO)

def get_result(df):
    for index, row in df.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away = predict_points(home, away)
        if points_home > points_away:
            winner = home
            loser = away
        elif points_home < points_away:
            winner = away
            loser = home
        df.loc[index, 'Winner'] = winner
        df.loc[index, 'Loser'] = loser
    return df

df_fix_sf[['Winner', 'Loser']] = '?'
df_fix_sf = get_result(df_fix_sf)


# Simulating third place, and finals

# Modifying QF list based on semi-finalists
for index, row in df_fix_sf.iterrows():
    match_df = row['score']
    df_fix_f.replace({f'Winners {match_df}': row['Winner']}, inplace=True)
    df_fix_f.replace({f'Losers {match_df}': row['Loser']}, inplace=True)
    
df_fix_f[['Winner', 'Loser']] = '?'
df_fix_f = get_result(df_fix_f) # Method used to predict winners in semi-finals can be used here
    
print(dict_table)
print(df_fix_KO)
print(df_fix_qf)
print(df_fix_sf)
print(df_fix_f)
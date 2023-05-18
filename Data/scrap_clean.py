from bs4 import BeautifulSoup
import requests
import pandas as pd

years = [1930,1934,1938,1950,1954,1958,1962,1966,1970,1974,1978,1982,1986,1990,1994,1998,2002,2006,2010,2014,2018,2022]

# for i in range(1930,2023,4):
#     print(i)
def get_matches(year):
    web = f'https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup'
    response = requests.get(web)
    content = response.text

    soup = BeautifulSoup(content, 'lxml')

    matches = soup.find_all('div', class_='footballbox') # this function has to contain the 'tag' and 'class' name

    home = [match.find('th', class_='fhome').get_text() for match in matches]
    score = [match.find('th', class_='fscore').get_text() for match in matches]
    away = [match.find('th', class_='faway').get_text() for match in matches]

    # for match in matches:
    #     home.append(match.find('th', class_='fhome').get_text())
    #     score.append(match.find('th', class_='fscore').get_text())
    #     away.append(match.find('th', class_='faway').get_text())
        
    dict_football = {'home':home, 'away':away, 'score':score}
    df_football = pd.DataFrame(dict_football)
    df_football['year'] = year
    
    return df_football

# print(get_matches('2022'))

# Data cleaning
# all_wcs = [get_matches(year) for year in years]
all_wcs = get_matches(2022)
# all_wcs = pd.concat(all_wcs, ignore_index=True)
all_wcs['home'] = all_wcs['home'].str.strip()
all_wcs['away'] = all_wcs['away'].str.strip()
all_wcs.dropna(inplace=True)
# print(all_wcs[all_wcs['home'].str.contains('Argentina') & all_wcs['away'].str.contains('France')])
# all_wcs ['score'] = all_wcs['score'].str.replace('[^\d-]', '', regex=True)
# print(all_wcs)
print(all_wcs['score'].str.split('-', expand=True))
# all_wcs.to_csv('fifa_worldcup_historical_data.csv', index=False)



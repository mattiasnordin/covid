from urllib.request import Request, urlopen
import pandas as pd
import os
import numpy as np

path = 'D:\\covid'
os.chdir(path)

url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

req = Request(url_confirmed, headers={'User-Agent': 'Mozilla/5.0'})
source = urlopen(req)


df_pop = pd.read_csv('data/input/pop.csv')

df = pd.read_csv(source)

df.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
df = pd.melt(df, id_vars=['Country/Region'])
df['Country/Region'] = np.where(df['Country/Region'] == 'Cape Verde',
                           'Cabo Verde', df['Country/Region'])
df = df.groupby(['Country/Region', 'variable']).agg(['sum'])
df = df.reset_index()
df.columns = ['country', 'date', 'confirmed']


df_t = df
#df_t = df[~df['country'].isin(country_list)]

df_t = df_t.groupby('date').aggregate('sum')
df_t = df_t.reset_index()
df_t['country'] = 'all'
df = df.append(df_t)

df['date2'] = pd.to_datetime(df['date'])
df.sort_values(by=['country', 'date2'], inplace=True)
df.drop('date2', axis=1, inplace=True)

df_confirmed = df

req = Request(url_deaths, headers={'User-Agent': 'Mozilla/5.0'})
source = urlopen(req)

df = pd.read_csv(source)

df.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
df = pd.melt(df, id_vars=['Country/Region'])
df['Country/Region'] = np.where(df['Country/Region'] == 'Cape Verde',
                           'Cabo Verde', df['Country/Region'])
df = df.groupby(['Country/Region', 'variable']).agg(['sum'])
df = df.reset_index()
df.columns = ['country', 'date', 'deaths']

df_t = df

df_t = df_t.groupby('date').aggregate('sum')
df_t = df_t.reset_index()
df_t['country'] = 'all'
df = df.append(df_t)

df['date2'] = pd.to_datetime(df['date'])
df.sort_values(by=['country', 'date2'], inplace=True)
df.drop('date2', axis=1, inplace=True)

df_deaths = df

df = pd.merge(df_confirmed, df_deaths, on=['date', 'country'])

df_pop = pd.read_excel(
    'data/input/WPP2019_POP_F01_1_TOTAL_POPULATION_BOTH_SEXES.xlsx',
    skiprows=15, header=1)
df_pop = df_pop[df_pop['Type'] == 'Country/Area']

q = df_pop['Parent code'].drop_duplicates().tolist()

df_pop['continent'] = ''

for v in q[0:6]:
    df_pop['continent'] = np.where(
        df_pop['Parent code'] == v, 'Africa', df_pop['continent'])

for v in q[6:10]:
    df_pop['continent'] = np.where(
        df_pop['Parent code'] == v, 'Asia', df_pop['continent'])

for v in q[10:12]:
    df_pop['continent'] = np.where(
        df_pop['Parent code'] == v, 'North America', df_pop['continent'])

for v in [q[12]]:
    df_pop['continent'] = np.where(
        df_pop['Parent code'] == v, 'South America', df_pop['continent'])

for v in q[13:17]:
    df_pop['continent'] = np.where(
        df_pop['Parent code'] == v, 'Oceania', df_pop['continent'])

for v in q[17:21]:
    df_pop['continent'] = np.where(
        df_pop['Parent code'] == v, 'Europe', df_pop['continent'])

for v in [q[21]]:
    df_pop['continent'] = np.where(
        df_pop['Parent code'] == v, 'North America', df_pop['continent'])


df_pop = df_pop[['Region, subregion, country or area *', '2020', 'continent']]

df_pop.columns = ['country', 'pop', 'continent']
df_pop['pop'] = df_pop['pop'] * 1000

country_name_dict = {

    'Congo' :'Congo (Brazzaville)',
    'Viet Nam' :'Vietnam',
    'Bahamas' :'Bahamas, The',
    'United Republic of Tanzania' :'Tanzania',
    'Timor-Leste' :'East Timor',
    'Bolivia (Plurinational State of)' :'Bolivia',
    'China, Taiwan Province of China' :'Taiwan*',
    'Republic of Korea' :'Korea, South',
    "Côte d'Ivoire" :"Cote d'Ivoire",
    'Republic of Moldova' :'Moldova',
    'Iran (Islamic Republic of)' :'Iran',
    'United States of America' :'US',
    'Venezuela (Bolivarian Republic of)' :'Venezuela',
    'Democratic Republic of the Congo' :'Congo (Kinshasa)',
    'Russian Federation' :'Russia',
    'Brunei Darussalam' :'Brunei',
    'Gambia' :'Gambia, The'
    
}

df_pop['country'].replace(country_name_dict, inplace=True)

df_pop = df_pop.append(
    {'country' : 'Kosovo' , 'pop' : 1810463, 'continent': 'Europe'},
    ignore_index=True)
df_pop['pop'] = np.where(df_pop['country'] == 'Serbia', 6963764, df_pop['pop'])

df = pd.merge(df, df_pop, on='country')

df['pop'] = pd.to_numeric(df['pop'])

df_cont = df.groupby(
    ['continent', 'date'])[['confirmed', 'deaths', 'pop']].sum()
df_cont = df_cont.reset_index()
df_cont.rename(columns={'continent': 'country'}, inplace=True)
df_world = df.groupby(['date'])[['confirmed', 'deaths', 'pop']].sum()
df_world['country'] = 'all'
df_world = df_world.reset_index()
df = df.append(df_cont)
df = df.append(df_world)


df['date2'] = pd.to_datetime(df['date'])
nr_days = (df['date2'].max() - df['date2'].min()).days + 1
df_date = pd.DataFrame(pd.period_range(
    df['date2'].min(), freq='D', periods=nr_days)).reset_index()
df_date.rename(columns=({'index': 'rank_date', 0: 'date2'}), inplace=True)
df_date['date2'] = pd.to_datetime(df_date['date2'].astype('str'))
df = pd.merge(df, df_date, on='date2')


df.sort_values(by=['country', 'rank_date'], inplace=True)
df = df.reset_index()
df.drop(columns=['index'], inplace=True)
df_temp = df.groupby('country')['confirmed', 'deaths'].rolling(
    7, win_type='boxcar').mean().reset_index()
df_temp['rank_date'] = df_temp.groupby('country')['level_1'].rank(
    'dense', ascending=True).astype(int) - 1

df_temp.drop(columns=['level_1'], inplace=True)
df_temp.rename(columns=({'confirmed': 'confirmed_rolling',
                         'deaths': 'deaths_rolling'}), inplace=True)

df = pd.merge(df, df_temp, on=['country', 'rank_date'], validate='1:1')

for i in ['confirmed', 'confirmed_rolling', 'deaths', 'deaths_rolling']:
    df[i] /= df['pop'] / 1e6


df.sort_values(by=['country', 'rank_date'], inplace=True)
df['delta_confirmed'] = df['confirmed_rolling'].diff(1)
df['delta_confirmed_rolling'] = df.groupby(
    'country')['confirmed_rolling'].diff(7) / 7
df['delta_deaths'] = df['deaths'].diff(1)
df['delta_deaths_rolling'] = df.groupby(
    'country')['deaths_rolling'].diff(7) / 7

df.drop('date2', axis=1, inplace=True)
df_code = pd.read_csv('data/input/country_code.csv')
df = df[['country', 'delta_confirmed', 'delta_confirmed_rolling',
         'delta_deaths', 'delta_deaths_rolling', 'date']]
df = pd.merge(df, df_code, on='country', how='inner')
df['date'] = pd.to_datetime(df['date'])
df['start_date'] = df['start_date'] =pd.to_datetime('1/22/20')
df['day_nr'] = (df['date'] - df['start_date']).dt.days + 1
df.drop('start_date', axis=1, inplace=True)
df['date'] = df['date'].astype(str)

df.to_csv('data/output/country_data.csv')

import numpy as np
import pandas as pd
import plotly.express as px
import scipy.optimize as opt
import sys, os, glob

def linearRegression(x, a, b):
    return x*a + b

# clean loaded data
def cleanup(df):
    new_df = df.copy(deep=True) #  copy dataframe so original is not changed
    cols = pd.MultiIndex.from_tuples([('Coords', 'Lat'), ('Coords', 'Lon')]+list(zip(['Data']*len(df.columns.values[2:]), df.columns.values[2:]))) # add multilevel for numerical data
    new_df.columns = cols # update columns multilevel
    new_df.index = pd.MultiIndex.from_frame(df.index.to_frame().fillna('Main')) # replace NA in Regions with Main
    return new_df

# load data into data frames
def load_data(directory):
    dataFrames = {}
    values = ['recovered', 'deaths', 'confirmed']
    difference_modifier = '_diff'

    # get data, put into dataframes
    for file in glob.glob(os.path.join(directory, '*.csv')):
        for value in values:
            if value in file:
                df = total_stats(cleanup(pd.read_csv(file, index_col=[1,0], header=[0])))
                for country in df.index.unique(level=0).values:
                    if "Main" not in df.loc[country].index.values:
                        df.loc[(country, "Main"), :] = 0
                df.sort_index(inplace=True)
                dataFrames[value] = df

    # make dataframes with daily rates            
    for value in values:
        df_diff = dataFrames[value]['Data'].diff(periods=1, axis=1)
        dataFrames[value+difference_modifier] = df_diff.drop(df_diff.columns[0], axis=1)

    # create dataframe for active cases from confirmed - recovered
    idx = pd.IndexSlice
    activeDF =  dataFrames['confirmed'].copy()
    activeDF['Data'] -= dataFrames['recovered']['Data']
    mask = activeDF.loc[idx[:, :], idx['Data', :]] < 0      # remove unphysical negative values
    activeDF[mask] = 0
    activeDF['Total'] -= dataFrames['recovered']['Total']
    dataFrames['active'] = activeDF

    # calculate daily difference
    df_diff = dataFrames['active']['Data'].diff(periods=1, axis=1)
    dataFrames['active_diff'] = df_diff.drop(df_diff.columns[0], axis=1)
    return dataFrames

def death_vs_confirmed(deaths:pd.DataFrame, confirmed:pd.DataFrame):
    y = deaths.copy() # remove world and copy
    x = confirmed.copy()

    # drop countries without any deaths for log fitting
    dropmask0 = y[y <= 0].index.values
    y0 = y.drop(dropmask0)
    x0 = x.drop(dropmask0)
    dropmask1 = x0[x0<= 0].index.values
    x0 = x0.drop(dropmask1)
    y0 = y0.drop(dropmask1)

    popt0, pcov0 = opt.curve_fit(linearRegression, np.log(x0), np.log(y0), bounds=([-np.inf, -np.inf], [np.inf, 0]))

    return popt0, pcov0, linearRegression



# calculate total stats
def total_stats(df):
    df['Total', 'tot'] = df['Data'][df['Data'].columns.values[-1]] # total in time for each country/region
    df.loc[('World','Main'),:] = df.sum(axis=0) # total of each day for world
    df.loc[('World', 'Main')]['Coords'] = (np.nan, np.nan) # remove gps coordinates for world
    return df



if __name__ == '__main__':
    dataDir = '.\data\\'
    dFrames = load_data(dataDir)
    #print(dFrames['recovered_diff'].head())
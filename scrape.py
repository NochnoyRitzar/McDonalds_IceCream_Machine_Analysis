import requests
import datetime
import os
import pandas as pd


def scrape_info():
    """
    Scrape data from McBroken website

    :rtype tuple:
    :return: time when website was scraped and dictionary containing data
    """
    time_scraped = datetime.datetime.now().replace(microsecond=0)
    resp_json = requests.get('https://mcbroken2.nyc3.digitaloceanspaces.com/markers.json').json()

    return time_scraped, resp_json


def transform_data(time_scraped, resp_json):
    """
    Clean and transform data into usable format for analysis

    :param time_scraped: time when website was scraped
    :param resp_json: data from scraping
    :return: pandas Dataframe
    """
    # retrieve deep nested dictionary keys as columns
    df = pd.json_normalize(resp_json.get('features'), max_level=1)
    df = df.rename(
        columns={
            'geometry.coordinates': 'coordinates',
            'properties.dot': 'status',
            'properties.state': 'state',
            'properties.city': 'city',
            'properties.street': 'street',
            'properties.country': 'country',
            'properties.last_checked': 'last_checked'
        }
    )

    df['longitude'] = df['coordinates'].apply(lambda array: array[0]).astype('float64')
    df['latitude'] = df['coordinates'].apply(lambda array: array[1]).astype('float64')
    df['scraped_datetime'] = time_scraped

    df = df.drop(columns=['type', 'geometry.type', 'properties.is_broken', 'properties.is_active', 'coordinates'])
    df = df.drop(df.loc[df['country'] != 'USA'].index)
    df = df.drop(columns=['country'])

    # leave only integer part of the cell value
    df['last_checked'] = df['last_checked'].str.extract(r'(\d+)').astype('int32')
    # clean last_checked column by subtracting last_checked minute timedelta from time when dat was scraped
    df['last_checked'] = df['scraped_datetime'] - df['last_checked'].apply(
        lambda value: datetime.timedelta(minutes=value)
    )

    return df


def update_warehouse(df_warehouse, new_df):
    """
    Find rows whose status was updated and concatenate them to the data warehouse dataframe

    :param df_warehouse: dataframe that acts like a data warehouse
    :param new_df: dataframe with new scraped info
    :return: updated dataframe with new changes
    """
    # group by longitude and latitude and find rows that were last checked
    temp_df = df_warehouse.groupby(['longitude', 'latitude']).last()
    # merge on 2 unique columns to find updated values
    temp_df = pd.merge(new_df, temp_df, on=['longitude', 'latitude'], how='inner')
    # find indices of rows whose status was updated
    index_list = temp_df.loc[(temp_df['status_x'] != temp_df['status_y'])].index
    # concatenate rows with changes to data warehouse dataframe
    df_warehouse = pd.concat([df_warehouse, new_df.loc[index_list]], ignore_index=True)

    return df_warehouse


if __name__ == '__main__':
    time_scraped, resp_json = scrape_info()
    df = transform_data(time_scraped, resp_json)

    # check if directory is empty
    if not os.listdir('data/final'):
        # save data from first iteration
        df.to_csv('data/final/data_warehouse.csv', index=False)
        df.to_csv(f'data/processed/{time_scraped.strftime("%Y-%m-%d %H-%M-%S")}.csv', index=False)
    else:
        df.to_csv(f'data/processed/{time_scraped.strftime("%Y-%m-%d %H-%M-%S")}.csv', index=False)
        df_warehouse = pd.read_csv('data/final/data_warehouse.csv')
        df_warehouse = update_warehouse(df_warehouse, df)
        df_warehouse.to_csv('data/final/data_warehouse.csv', index=False)

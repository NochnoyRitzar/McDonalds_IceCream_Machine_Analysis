import pandas as pd
import numpy as np
import click

from constants import AVERAGE_DAILY_US_CUSTOMERS, ICE_CREAM_DESSERT_PRICES, DESSERT_ORDER_RATIO, \
    ICE_CREAM_ORDER_RATIO, NUM_RESTAURANTS_US


def load_data(path) -> pd.DataFrame:
    """
    Load info from data warehouse csv to pandas Dataframe

    :param path: path to folder with data warehouse csv
    :return: data warehouse Dataframe
    """
    df = pd.read_csv(path)
    return df


def calculate_total_broken_duration(df, start_time, end_time):
    """
    Calculate daily total duration when machines were broken

    :param df: data warehouse Dataframe
    :param start_time: analysis start point
    :param end_time: analysis end point
    :return: total duration across all restaurants when machines where broken
    """
    # convert to datetime type
    df['scraped_datetime'] = pd.to_datetime(df['scraped_datetime'])
    df['last_checked'] = pd.to_datetime(df['last_checked'])

    # subset rows between start and end time
    daily_df = df.loc[(df['last_checked'] >= start_time) & (df['last_checked'] <= end_time)].copy()

    # lead values by 1 over 'longitude' and 'latitude' partition
    daily_df['last_checked_lead'] = daily_df.groupby(['longitude', 'latitude'])['last_checked'].shift(-1)

    # set all 'broken' rows without lead value to the end_time date
    daily_df.loc[
        (daily_df['last_checked_lead'].isnull()) & (daily_df['status'] == 'broken'), 'last_checked_lead'
    ] = end_time

    broken_index_list = daily_df.loc[daily_df['status'] == 'broken'].index
    broken_duration_series = daily_df['last_checked_lead'].loc[broken_index_list] - \
                             daily_df['last_checked'].loc[broken_index_list]
    broken_duration_series = broken_duration_series.apply(lambda value: value.total_seconds())

    total_broken_duration = np.sum(broken_duration_series)

    return total_broken_duration


def calculate_lost_revenue(broken_time,
                           average_daily_us_customers,
                           ice_cream_dessert_prices,
                           dessert_order_ratio,
                           ice_cream_order_ratio,
                           num_restaurants_us):
    """
    Calculate lost revenue in ice cream sales due to broken ice cream machines

    :param broken_time: total duration in seconds across all restaurants when machines where broken
    :param average_daily_us_customers: average daily number of customers
    :param ice_cream_dessert_prices: dictionary with prices for ice cream desserts
    :param dessert_order_ratio: ratio of dessert orders to all orders
    :param ice_cream_order_ratio: ratio of ice cream orders to other desserts
    :param num_restaurants_us: number of restaurants in US
    :return:
    """
    # calculate total downtime in hours
    broken_time = broken_time / 3600
    # average number of customers per hour
    average_num_customers_per_hour = average_daily_us_customers / 24
    # calculate average ice cream dessert price
    average_ice_cream_price = np.mean(list(ice_cream_dessert_prices.values()))

    lost_revenue = np.ceil(average_num_customers_per_hour * broken_time / num_restaurants_us * dessert_order_ratio * \
                             ice_cream_order_ratio * average_ice_cream_price)

    return lost_revenue


@click.command()
@click.option('--start_date',
              prompt='Analysis start date (format: YEAR-MONTH-DAY)',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              help='Specify starting date of analysis')
@click.option('--end_date',
              prompt='Analysis end date (format: YEAR-MONTH-DAY)',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              help='Specify end date of analysis')
def run_daily_analysis(start_date, end_date):
    df = load_data('data/final/data_warehouse.csv')
    total_broken_duration = calculate_total_broken_duration(df, start_date, end_date)
    lost_revenue = calculate_lost_revenue(
        total_broken_duration,
        AVERAGE_DAILY_US_CUSTOMERS,
        ICE_CREAM_DESSERT_PRICES,
        DESSERT_ORDER_RATIO,
        ICE_CREAM_ORDER_RATIO,
        NUM_RESTAURANTS_US
    )
    print(f'Total downtime across all restaurants: {np.ceil(total_broken_duration / 3600)} hours in the period from {start_date.date()} to {end_date.date()}.')
    print(f"In the period from {start_date.date()} to {end_date.date()} McDonald's lost approximately {lost_revenue}$ in revenue.")


if __name__ == '__main__':
    run_daily_analysis()

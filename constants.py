# information obtained from https://financesonline.com/number-of-mcdonalds-in-north-america/
# average daily number of customers across all restaurants in USA
AVERAGE_DAILY_US_CUSTOMERS = 25000000
# number of McDonald's restaurants in USA
NUM_RESTAURANTS_US = 13683

# obtained from https://www.fastfoodmenuprices.com/mcdonalds-prices/#Desserts
ICE_CREAM_DESSERT_PRICES = {
    'SMALL_SHAKE': 2.19,
    'MEDIUM_SHAKE': 2.59,
    'LARGE_SHAKE': 2.99,
    'SUNDAE': 1.29,
    'VANILLA_CONE': 1,
    'SNACK_MCFLURRY': 1.79,
    'REGULAR_MCFLURRY': 2.39
}

# guess on how often desserts are ordered
# so in 3 out of 10 orders there is a dessert
DESSERT_ORDER_RATIO = 0.3

# guess on how often ice cream is ordered from desserts
# 9 out of 10 desserts is ice cream
ICE_CREAM_ORDER_RATIO = 0.9

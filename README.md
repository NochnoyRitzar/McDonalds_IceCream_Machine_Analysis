# McDonalds_IceCream_Machine_Analysis
## Summary
Analyze data when McDonald's ice cream machines are broken to determine how much revenue they lose. <br>
Analysis is very inaccurate due to wild guesses on a lot of factors and variables. Even hourly distribution of customers, no necessary 4-hour maintenance period, all-day restaurant schedule, ice cream selling all-day - those are assumed.
## How to run:
### To analyze
```
python analyze.py --start_date=2022-09-22 --end_date=2022-09-23
```
`--start_date` - to specify analysis starting date <br>
`--end_date` - to specify analysis ending date <br>
`python analyze.py -h` for more help
### To scrape data
```
python scrape.py
```
## Project structure
```bash
├─── data # Data folder
│    ├─── final # contains data warehouse csv
│    └─── processed # folder with processed hourly data (after transform)
├─── analyze.py # Perform analysis
├─── scrape.py # ETL data from website
├─── constants.py # Declare constants (contains explanation of variables)
├─── .gitignore
├─── README.md
└─── requirements.txt
```

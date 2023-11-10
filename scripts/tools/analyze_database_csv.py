import pandas as pd
import sys
import os
os.chdir("..")
print(os.getcwd())
sys.path.insert(0,os.getcwd())
from settings_prod import database_content_filename 
# Read CSV into DataFrame
csv_file_path = database_content_filename
df = pd.read_csv(csv_file_path)

# Convert 'harvesting date' column to datetime
df['date_harvested'] = pd.to_datetime(df['date_harvested'])

# Sort by 'harvesting date' in ascending order
df.sort_values(by='date_harvested', ascending=True, inplace=True)

# Additional operations or columns you want to create
# For example, you can create a column with the difference in days from the earliest harvesting date
df['days_since_first_harvest'] = (df['date_harvested'] - df['date_harvested'].min()).dt.days
print(df.columns)
print(df.head(50)["episode_title" ])


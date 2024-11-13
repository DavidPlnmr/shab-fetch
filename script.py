from shab_request_api import SHABRequestAPI
import datetime
import pandas as pd

shab = SHABRequestAPI()

today = datetime.date.today()
last_week_date = today - datetime.timedelta(days=7)

# Returns a list of publications
data = shab.get_new_entries(
    publication_date_end=today, publication_date_start=last_week_date, size=1000)

# Affichage du DataFrame
df = shab.publications_data_to_df(data)

print(df.head())
df.to_csv("shab_data.csv", index=False)

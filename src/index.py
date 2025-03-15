from src.scraper.dm_scraper import DMScraper
import pandas as pd

products = DMScraper().scrape_city("Presidente Venceslau")
df = pd.DataFrame(products)

# sort df values by price
df = df.sort_values(by='price', ascending=True)

df.to_csv('raw_output.tsv', sep="\t", index=False)


df = df[
    (df['price'] >= 6) &
    (df['price'] <= 16) &
    (df['is_closed'] == False)
]

df.to_csv('output.tsv', sep="\t", index=False)

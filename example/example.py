from kagglefetcher import fetch_dataset

path = fetch_dataset("zillow/zecon")
print(f"Dataset available at {path}")
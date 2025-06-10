"""
csv_storage.py

This utility performs a web crawl on 137ventures.com and saves the results
to a CSV file, leveraging the desync_data library for the export.

Use case:
    - Demonstrate a basic crawl and data export workflow.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from desync_data import save_to_csv

# Initialize the DesyncClient
client = DesyncClient()
# client = DesyncClient(user_api_key="your_api_key_here") # Alternative initialization

# Perform a crawl on 137ventures.com/team
crawl_pages = client.crawl(start_url="https://www.137ventures.com/team", max_depth=1)

# Save the crawled pages to a CSV file
output_filepath = "output/137ventures_crawl_results.csv"
save_to_csv(crawl_pages, output_filepath, mode="w")
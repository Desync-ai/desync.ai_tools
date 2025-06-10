"""
sqlite_storage.py

This utility performs a web crawl on 137ventures.com and saves the results
to a SQLite database, leveraging the desync_data library for the export.

Use case:
    - Demonstrate a basic crawl and data export workflow to a structured database.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from desync_data import save_to_sqlite

# Initialize the DesyncClient
client = DesyncClient()
# client = DesyncClient(user_api_key="your_api_key_here") # Alternative initialization

# Perform a crawl on 137ventures.com/team
crawl_pages = client.crawl(start_url="https://www.137ventures.com/team", max_depth=1)

# The `append=True` argument will add new records if the table already exists.
# Set `append=False` to recreate the table each time the script runs.
save_to_sqlite(pages=crawl_pages, db_path="output/137ventures_crawl_results.sqlite", table_name="team_pages", append=True)
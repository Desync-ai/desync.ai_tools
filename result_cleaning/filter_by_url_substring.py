# result_cleaning/filter_by_url_substring.py

"""
Filters a list of PageData objects, keeping only those whose URLs
contain a specified substring, using `desync_data.filter_by_url_substring`.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from desync_data import filter_by_url_substring

# Initialize the DesyncClient
client = DesyncClient()
# client = DesyncClient(user_api_key="your_api_key_here") # Alternative initialization

# Perform a crawl to get some pages
pages = client.crawl(start_url="https://www.137ventures.com", max_depth=2)

# Define the substring to filter by
target_substring = "/team/"

# Apply the URL substring filter
filtered_pages = filter_by_url_substring(pages=pages, substring=target_substring)

print(f"Number of URLs before filtering: {len(pages)}.")
print(f"Number of URLs after filtering for '{target_substring}': {len(filtered_pages)}.")
print("\nFiltered URLs:")
if filtered_pages:
    for page in filtered_pages:
        print(f"- {page.url}")
else:
    print("No URLs matched the filter.")
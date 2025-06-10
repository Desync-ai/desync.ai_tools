# result_cleaning/duplicate_page_remover.py

"""
Removes duplicate pages from a list of PageData objects
using `desync_data.remove_duplicate_pages`.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from desync_data import remove_duplicate_pages

# Initialize the DesyncClient
client = DesyncClient()
# client = DesyncClient(user_api_key="your_api_key_here") # Alternative initialization

# Perform a crawl on 137ventures.com
pages = client.crawl(start_url="https://www.137ventures.com", max_depth=1)

# Apply duplicate page removal
deduplicated_pages = remove_duplicate_pages(pages=pages)

print(f"Number of urls before deduplicating: {len(pages)}.")
print(f"Number of urls after deduplicating: {len(deduplicated_pages)}.")
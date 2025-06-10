# result_cleaning/text_cleaning/remove_boilerplate_prefix.py

"""
Removes boilerplate text from the beginning of PageData objects using
`desync_data.remove_boilerplate_prefix`.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from desync_data import remove_boilerplate_prefix

client = DesyncClient()
# client = DesyncClient(user_api_key="your_api_key_here") # Alternative initialization

# Crawl example pages
pages = client.crawl(start_url="https://www.137ventures.com/team", max_depth=1)

# Define a delimiter found before desired content
prefix_delimiter = "LP LOGIN"

# Apply boilerplate removal
cleaned_pages = remove_boilerplate_prefix(pages=pages, delimiter=prefix_delimiter)

# Display first 50 characters of original vs. cleaned text for the first 3 results
for i in range(3):
    print('----------------------------------------------------------')
    print(f"\nOriginal Text:\n{pages[i].text_content[:50]}")
    print(f"\nCleaned Text:\n{cleaned_pages[i].text_content[:50]}\n")
# result_cleaning/text_cleaning/remove_boilerplate_suffix.py

"""
Removes boilerplate text from the end of PageData objects using
`desync_data.remove_boilerplate_suffix`.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from desync_data import remove_boilerplate_suffix

client = DesyncClient()
# client = DesyncClient(user_api_key="your_api_key_here") # Alternative initialization

# Crawl example pages
pages = client.crawl(start_url="https://www.137ventures.com/team", max_depth=1)

# Define a delimiter found before desired content
suffix_delimiter = "This material presented"

# Apply boilerplate removal
cleaned_pages = remove_boilerplate_suffix(pages=pages, delimiter=suffix_delimiter)

# Display last 50 characters of original vs. cleaned text for the first 3 results
for i in range(3):
    print('----------------------------------------------------------')
    print(f"\nOriginal Text:\n{pages[i].text_content[50:]}")
    print(f"\nCleaned Text:\n{cleaned_pages[i].text_content[50:]}\n")
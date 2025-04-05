# examples/use_bulk_clean_save_to_output.py

"""
Example: Clean boilerplate from a bulk search and save the results.

This script demonstrates how to use:
- `bulk_and_clean` from ../results_cleaning/bulk_search_remove_boilerplate.py
- `save_to_csv` from ../storage/csv/csv_storage.py

Steps:
1. Perform a bulk search using DesyncClient.
2. Remove repeated boilerplate text.
3. Save the cleaned results to /outputs/bulk_cleaned_output.csv.

Author: Jackson-Ballow
"""

import sys
import os

# Add relevant directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "result_cleaning", "text_content_cleaning"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "storage", "csv"))

from remove_boilerplate_text import remove_boilerplate_text
from csv_storage import save_to_csv
from desync_search import DesyncClient

urls = [
    "https://www.137ventures.com/team/koby-aliphios",
    "https://www.137ventures.com/team/sebastian-ferus",
    "https://www.137ventures.com/team/justin-fishner-wolfson",
    "https://www.137ventures.com/team/christian-garrett",
    "https://www.137ventures.com/team/andrew-hansen",
    "https://www.137ventures.com/team/s-alexander-jacobson",
    "https://www.137ventures.com/team/kelsey-knorr",
    "https://www.137ventures.com/team/andrew-laszlo",
    "https://www.137ventures.com/team/neva-lew",
    "https://www.137ventures.com/team/sarah-mitchell",
    "https://www.137ventures.com/team/james-pardee",
    "https://www.137ventures.com/team/sarah-pikover",
    "https://www.137ventures.com/team/nicholas-procaccini",
    "https://www.137ventures.com/team/amanda-santonastaso",
    "https://www.137ventures.com/team/andrew-schreder",
    "https://www.137ventures.com/team/dorothy-sumption",
    "https://www.137ventures.com/team/ada-tam",
    "https://www.137ventures.com/team/michelle-tunley",
    "https://www.137ventures.com/team/mason-windatt"
]


if __name__ == "__main__":
    # Initialize DesyncClient
    client = DesyncClient()

    # Step 1: Perform a bulk search
    bulk_info = client.bulk_search(target_list=urls, extract_html=False)

    pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=0.975,
    )

    # Step 2: Remove the boilerplate text
    remove_boilerplate_text(pages, threshold=0.5, chunk_method="line")

    # Step 3: Save cleaned results to CSV
    output_path = "output/bulk_cleaned_output.csv"
    save_to_csv(pages, output_path, mode="w")

    print(f"✅ Saved cleaned bulk search results to {output_path}")

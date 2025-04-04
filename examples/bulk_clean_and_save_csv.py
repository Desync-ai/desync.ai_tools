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
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "result_cleaning"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "storage", "csv"))

from bulk_search_remove_boilerplate import bulk_and_clean
from csv_storage import save_to_csv

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
    # Step 1 & 2: Run bulk search and remove boilerplate
    cleaned_pages = bulk_and_clean(urls, threshold=0.5, chunk_method="line")

    # Step 3: Save cleaned results to CSV
    output_path = "output/bulk_cleaned_output.csv"
    save_to_csv(cleaned_pages, output_path, mode="w")

    print(f"✅ Saved cleaned bulk search results to {output_path}")

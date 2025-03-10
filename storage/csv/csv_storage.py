import csv
import os
from typing import List, Dict, Optional, Any

# Make sure you have installed desync_search (pip install desync_search)
from desync_search import DesyncClient


class CSVStorage:
    """
    A class to handle saving and managing scraped data in a CSV file,
    with integrated methods to perform Desync searches and automatically
    save the results.
    """

    def __init__(self, file_path: str, desync_client: Optional[DesyncClient] = None):
        """
        Initialize the CSVStorage with the desired file path and, optionally, a DesyncClient.
        
        :param file_path: Path to the output CSV file.
        :param desync_client: An instance of DesyncClient used for performing searches/crawls.
        """
        self.file_path = file_path
        self.desync_client = desync_client

    def save(self, data: List[Dict[str, Any]]):
        """
        Save a list of dictionaries to a CSV file. Overwrites any existing file.

        :param data: List of dictionaries containing the scraped data.
        """
        if not data:
            return

        keys = data[0].keys()
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise e

    def append(self, data: List[Dict[str, Any]]):
        """
        Append a list of dictionaries to an existing CSV file. Creates the file if it doesn't exist.

        :param data: List of dictionaries containing the scraped data.
        """
        if not data:
            return

        file_exists = os.path.isfile(self.file_path)
        keys = data[0].keys()
        try:
            with open(self.file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=keys)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise e

    def load(self) -> List[Dict[str, Any]]:
        """
        Load data from the CSV file into a list of dictionaries.

        :return: List of dictionaries containing the CSV data.
        """
        if not os.path.isfile(self.file_path):
            return []

        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = [row for row in reader]
            return data
        except Exception as e:
            raise e

    def update(self, criteria: Dict[str, Any], new_data: Dict[str, Any]):
        """
        Update records in the CSV file that match the given criteria with new data.

        :param criteria: Dictionary of field-value pairs to match records.
        :param new_data: Dictionary of field-value pairs to update matched records.
        """
        data = self.load()
        if not data:
            return

        updated = False
        for row in data:
            if all(row.get(key) == value for key, value in criteria.items()):
                row.update(new_data)
                updated = True

        if updated:
            self.save(data)

    def delete(self, criteria: Dict[str, Any]):
        """
        Delete records from the CSV file that match the given criteria.

        :param criteria: Dictionary of field-value pairs to match records.
        """
        data = self.load()
        if not data:
            return

        original_length = len(data)
        data = [row for row in data if not all(row.get(key) == value for key, value in criteria.items())]
        deleted_count = original_length - len(data)

        if deleted_count > 0:
            self.save(data)

    def get_headers(self) -> Optional[List[str]]:
        """
        Retrieve the headers/columns of the CSV file.

        :return: List of header names or None if the file doesn't exist.
        """
        if not os.path.isfile(self.file_path):
            return None

        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, None)
            return headers
        except Exception as e:
            raise e

    def exists(self) -> bool:
        """
        Check if the CSV file exists and is not empty.

        :return: True if file exists and is not empty, False otherwise.
        """
        if not os.path.isfile(self.file_path):
            return False
        if os.path.getsize(self.file_path) == 0:
            return False
        return True

    def _page_data_to_dict(self, page_data: Any) -> Dict[str, Any]:
        text_content = getattr(page_data, "text_content", None)
        # Replace newline characters with a space if text_content is not None
        if text_content:
            text_content = text_content.replace("\n", " ").replace("\r", " ")
        
        return {
            "id": getattr(page_data, "id", None),
            "url": getattr(page_data, "url", None),
            "domain": getattr(page_data, "domain", None),
            "timestamp": getattr(page_data, "timestamp", None),
            "bulk_search_id": getattr(page_data, "bulk_search_id", None),
            "search_type": getattr(page_data, "search_type", None),
            "text_content": text_content,
            "html_content": getattr(page_data, "html_content", None),
            "internal_links": ", ".join(getattr(page_data, "internal_links", [])) if getattr(page_data, "internal_links", None) else "",
            "external_links": ", ".join(getattr(page_data, "external_links", [])) if getattr(page_data, "external_links", None) else "",
            "latency_ms": getattr(page_data, "latency_ms", None),
            "complete": getattr(page_data, "complete", None),
            "created_at": getattr(page_data, "created_at", None),
        }


    def search_and_save(self, url: str, save_mode: str = "append", **desync_params):
        """
        Perform a search using the integrated DesyncClient and save the result to CSV.

        :param url: The URL to search.
        :param save_mode: Either "append" to add to an existing CSV or "overwrite" to create a new CSV.
        :param desync_params: Additional keyword arguments passed to DesyncClient.search()
                              (e.g., search_type, scrape_full_html, remove_link_duplicates).
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize CSVStorage with a valid DesyncClient.")

        result = self.desync_client.search(url, **desync_params)
        result_dict = self._page_data_to_dict(result)

        if save_mode == "append":
            self.append([result_dict])
        else:
            self.save([result_dict])

    def crawl_and_save(self, start_url: str, max_depth: int = 2, save_mode: str = "append", **desync_params):
        """
        Perform a crawl using the integrated DesyncClient and save the results to CSV.

        :param start_url: The initial URL to begin crawling.
        :param max_depth: Maximum depth for the crawl.
        :param save_mode: Either "append" to add to an existing CSV or "overwrite" to create a new CSV.
        :param desync_params: Additional keyword arguments passed to DesyncClient.crawl()
                              (e.g., scrape_full_html, remove_link_duplicates, poll_interval).
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize CSVStorage with a valid DesyncClient.")

        results = self.desync_client.crawl(start_url=start_url, max_depth=max_depth, **desync_params)
        data = [self._page_data_to_dict(result) for result in results]

        if save_mode == "append":
            self.append(data)
        else:
            self.save(data)

    def bulk_search_and_save(
        self,
        target_list: List[str],
        save_mode: str = "append",
        bulk_search_params: Optional[Dict[str, Any]] = None,
        collect_results_params: Optional[Dict[str, Any]] = None
    ):
        """
        Perform a bulk search using the integrated DesyncClient and save the results to CSV.

        :param target_list: List of URLs to process.
        :param save_mode: Either "append" to add to an existing CSV or "overwrite" to create a new CSV.
        :param bulk_search_params: Additional parameters for DesyncClient.bulk_search().
        :param collect_results_params: Additional parameters for DesyncClient.collect_results().
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize CSVStorage with a valid DesyncClient.")

        bulk_search_params = bulk_search_params or {}
        collect_results_params = collect_results_params or {}

        bulk_info = self.desync_client.bulk_search(target_list=target_list, **bulk_search_params)
        bulk_search_id = bulk_info.get("bulk_search_id")

        results = self.desync_client.collect_results(
            bulk_search_id=bulk_search_id, target_links=target_list, **collect_results_params
        )
        data = [self._page_data_to_dict(result) for result in results]

        if save_mode == "append":
            self.append(data)
        else:
            self.save(data)

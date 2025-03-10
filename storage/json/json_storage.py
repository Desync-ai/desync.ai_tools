import json
import os
from typing import List, Dict, Optional, Any

# Make sure you have installed desync_search (pip install desync_search)
from desync_search import DesyncClient


class JSONStorage:
    """
    A class to handle saving and managing scraped data in a JSON file,
    with integrated methods to perform Desync searches and automatically
    save the results.
    """

    def __init__(self, file_path: str, desync_client: Optional[DesyncClient] = None):
        """
        Initialize the JSONStorage with the desired file path and, optionally, a DesyncClient.
        
        :param file_path: Path to the output JSON file.
        :param desync_client: An instance of DesyncClient used for performing searches/crawls.
        """
        self.file_path = file_path
        self.desync_client = desync_client

    def save(self, data: List[Dict[str, Any]]):
        """
        Save a list of dictionaries to a JSON file. Overwrites any existing file.
        
        :param data: List of dictionaries containing the scraped data.
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=4)
        except Exception as e:
            raise e

    def append(self, data: List[Dict[str, Any]]):
        """
        Append a list of dictionaries to an existing JSON file.
        Creates the file if it doesn't exist.
        
        :param data: List of dictionaries containing the scraped data.
        """
        existing_data = self.load()
        new_data = existing_data + data
        self.save(new_data)

    def load(self) -> List[Dict[str, Any]]:
        """
        Load data from the JSON file into a list of dictionaries.
        
        :return: List of dictionaries containing the JSON data.
        """
        if not os.path.isfile(self.file_path):
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
            return data
        except Exception as e:
            raise e

    def update(self, criteria: Dict[str, Any], new_data: Dict[str, Any]):
        """
        Update records in the JSON file that match the given criteria with new data.
        
        :param criteria: Dictionary of field-value pairs to match records.
        :param new_data: Dictionary of field-value pairs to update matched records.
        """
        data = self.load()
        if not data:
            return

        updated = False
        for record in data:
            if all(record.get(key) == value for key, value in criteria.items()):
                record.update(new_data)
                updated = True

        if updated:
            self.save(data)

    def delete(self, criteria: Dict[str, Any]):
        """
        Delete records from the JSON file that match the given criteria.
        
        :param criteria: Dictionary of field-value pairs to match records.
        """
        data = self.load()
        if not data:
            return

        original_length = len(data)
        data = [record for record in data if not all(record.get(key) == value for key, value in criteria.items())]

        if len(data) < original_length:
            self.save(data)

    def exists(self) -> bool:
        """
        Check if the JSON file exists and is not empty.
        
        :return: True if file exists and is not empty, False otherwise.
        """
        if not os.path.isfile(self.file_path):
            return False
        if os.path.getsize(self.file_path) == 0:
            return False
        return True

    def _page_data_to_dict(self, page_data: Any) -> Dict[str, Any]:
        """
        Convert a PageData object (returned by DesyncClient methods) to a dictionary for JSON storage.
        
        :param page_data: The PageData object.
        :return: Dictionary representation of the page data.
        """
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
            "internal_links": getattr(page_data, "internal_links", []),
            "external_links": getattr(page_data, "external_links", []),
            "latency_ms": getattr(page_data, "latency_ms", None),
            "complete": getattr(page_data, "complete", None),
            "created_at": getattr(page_data, "created_at", None),
        }

    def search_and_save(self, url: str, save_mode: str = "append", **desync_params):
        """
        Perform a search using the integrated DesyncClient and save the result to JSON.
        
        :param url: The URL to search.
        :param save_mode: Either "append" to add to an existing JSON file or "overwrite" to create a new file.
        :param desync_params: Additional keyword arguments passed to DesyncClient.search()
                              (e.g., search_type, scrape_full_html, remove_link_duplicates).
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize JSONStorage with a valid DesyncClient.")

        result = self.desync_client.search(url, **desync_params)
        result_dict = self._page_data_to_dict(result)

        if save_mode == "append":
            self.append([result_dict])
        else:
            self.save([result_dict])

    def crawl_and_save(self, start_url: str, max_depth: int = 2, save_mode: str = "append", **desync_params):
        """
        Perform a crawl using the integrated DesyncClient and save the results to JSON.
        
        :param start_url: The initial URL to begin crawling.
        :param max_depth: Maximum depth for the crawl.
        :param save_mode: Either "append" to add to an existing JSON file or "overwrite" to create a new file.
        :param desync_params: Additional keyword arguments passed to DesyncClient.crawl()
                              (e.g., scrape_full_html, remove_link_duplicates, poll_interval).
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize JSONStorage with a valid DesyncClient.")

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
        Perform a bulk search using the integrated DesyncClient and save the results to JSON.
        
        :param target_list: List of URLs to process.
        :param save_mode: Either "append" to add to an existing JSON file or "overwrite" to create a new file.
        :param bulk_search_params: Additional parameters for DesyncClient.bulk_search().
        :param collect_results_params: Additional parameters for DesyncClient.collect_results().
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize JSONStorage with a valid DesyncClient.")

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

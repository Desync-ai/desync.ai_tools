import re
from typing import List, Dict, Any

class ContactInfoExtractor:
    """
    A class to extract contact information (emails and phone numbers) from results obtained via
    the desync_search client. It integrates with a DesyncClient to perform searches, bulk searches,
    or crawls, and then extracts contact details from the returned PageData objects.
    """

    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_PATTERN = re.compile(
        r"(?:\+?\d{1,3}[-.\s]?)?"      # Optional country code
        r"(?:\(?\d{3}\)?[-.\s]?)"      # Area code (with or without parentheses)
        r"\d{3}[-.\s]?\d{4}"           # Local number
    )

    def __init__(self, client: Any):
        """
        Initialize the ContactInfoExtractor with a desync_search client.

        :param client: An instance of DesyncClient.
        """
        self.client = client

    def _clean_email(self, email: str) -> str:
        """
        Normalizes an email address by stripping whitespace, removing any trailing period, and converting to lowercase.
        """
        return email.strip().rstrip('.').lower()

    def _clean_phone(self, phone: str) -> str:
        """
        Normalizes a phone number by stripping whitespace.
        """
        return phone.strip()

    def _extract_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts emails and phone numbers from the provided text and cleans them.

        :param text: A string to search for contact details.
        :return: A dictionary with keys 'emails' and 'phone_numbers'.
        """
        raw_emails = self.EMAIL_PATTERN.findall(text)
        raw_phones = self.PHONE_PATTERN.findall(text)
        emails = [self._clean_email(email) for email in raw_emails]
        phone_numbers = [self._clean_phone(phone) for phone in raw_phones]
        return {"emails": emails, "phone_numbers": phone_numbers}

    def extract_from_page(self, page_data: Any) -> Dict[str, Any]:
        """
        Extracts contact information from a single PageData object.

        :param page_data: A PageData object returned by desync_search.
        :return: A dictionary containing the page URL and the extracted contacts.
        """
        text = getattr(page_data, "text_content", "") or ""
        contacts = self._extract_from_text(text)
        return {"url": getattr(page_data, "url", ""), "contacts": contacts}

    def search_and_extract(self, url: str, **desync_params) -> Dict[str, Any]:
        """
        Performs a search using the desync_search client and extracts contact information
        from the resulting PageData.

        :param url: The URL to search.
        :param desync_params: Additional parameters to pass to the client's search() method.
        :return: A dictionary with the URL and extracted contact details.
        """
        page_data = self.client.search(url, **desync_params)
        return self.extract_from_page(page_data)

    def bulk_search_and_extract(self, urls: List[str], **desync_params) -> List[Dict[str, Any]]:
        """
        Performs a bulk search using the desync_search client and extracts contact information
        from all returned PageData objects.

        :param urls: A list of URLs to search.
        :param desync_params: Additional parameters to pass to the client's bulk_search() method.
        :return: A list of dictionaries, each containing a URL and its extracted contacts.
        """
        bulk_info = self.client.bulk_search(target_list=urls, **desync_params)
        bulk_search_id = bulk_info.get("bulk_search_id")
        results = self.client.collect_results(bulk_search_id=bulk_search_id, target_links=urls)
        return [self.extract_from_page(page) for page in results]

    def crawl_and_extract(self, start_url: str, max_depth: int, **desync_params) -> List[Dict[str, Any]]:
        """
        Performs a crawl using the desync_search client starting from the specified URL,
        and extracts contact information from all discovered PageData objects.

        :param start_url: The starting URL for the crawl.
        :param max_depth: The maximum link depth to follow.
        :param desync_params: Additional parameters to pass to the client's crawl() method.
        :return: A list of dictionaries, each containing a URL and its extracted contacts.
        """
        results = self.client.crawl(start_url=start_url, max_depth=max_depth, **desync_params)
        return [self.extract_from_page(page) for page in results]

    def aggregate_contacts(self, pages: List[Any]) -> Dict[str, List[str]]:
        """
        Aggregates contact information (emails and phone numbers) from a list of PageData objects,
        combining all extracted contacts into a single dictionary, with duplicates removed.
        
        :param pages: A list of PageData objects.
        :return: A dictionary with keys 'emails' and 'phone_numbers' containing all found contacts.
        """
        aggregated = {"emails": [], "phone_numbers": []}
        for page in pages:
            extracted = self._extract_from_text(getattr(page, "text_content", "") or "")
            aggregated["emails"].extend(extracted["emails"])
            aggregated["phone_numbers"].extend(extracted["phone_numbers"])
        aggregated["emails"] = list(set(aggregated["emails"]))
        aggregated["phone_numbers"] = list(set(aggregated["phone_numbers"]))
        return aggregated

    def aggregate_bulk_search(self, urls: List[str], **desync_params) -> Dict[str, List[str]]:
        """
        Performs a bulk search using the desync_search client and aggregates contact information
        from all returned PageData objects into a single dictionary.

        :param urls: A list of URLs to search.
        :param desync_params: Additional parameters to pass to the client's bulk_search() method.
        :return: A dictionary with keys 'emails' and 'phone_numbers' containing aggregated contacts.
        """
        pages = self.bulk_search_and_extract(urls, **desync_params)
        aggregated = {"emails": [], "phone_numbers": []}
        for item in pages:
            contacts = item.get("contacts", {})
            aggregated["emails"].extend(contacts.get("emails", []))
            aggregated["phone_numbers"].extend(contacts.get("phone_numbers", []))
        aggregated["emails"] = list(set(aggregated["emails"]))
        aggregated["phone_numbers"] = list(set(aggregated["phone_numbers"]))
        return aggregated

    def aggregate_crawl(self, start_url: str, max_depth: int, **desync_params) -> Dict[str, List[str]]:
        """
        Performs a crawl using the desync_search client and aggregates contact information
        from all discovered PageData objects into a single dictionary.

        :param start_url: The starting URL for the crawl.
        :param max_depth: The maximum link depth to follow.
        :param desync_params: Additional parameters to pass to the client's crawl() method.
        :return: A dictionary with keys 'emails' and 'phone_numbers' containing aggregated contacts.
        """
        pages = self.client.crawl(start_url=start_url, max_depth=max_depth, **desync_params)
        return self.aggregate_contacts(pages)

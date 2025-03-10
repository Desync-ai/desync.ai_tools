from desync_search import DesyncClient
import os

def main():
    my_api_key = os.environ.get("DESYNC_API_KEY")
    client = DesyncClient(my_api_key)
        
    # Test search
    test_data = client.search("https://example.com", search_type="test_search")
    
    # Inspect PageData fields
    print("URL:", test_data.url)
    print("Number of internal links:", len(test_data.internal_links))
    print("Number of external links:", len(test_data.external_links))
    print("Text content length:", len(test_data.text_content))

if __name__ == "__main__":
    main()
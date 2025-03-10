from desync_search import DesyncClient
import os

def main():
    my_api_key = os.environ.get("DESYNC_API_KEY")
    client = DesyncClient(my_api_key)
        
    # Test search
    stealth_data = client.search("https://example.com")
    
    # Inspect PageData fields
    print("URL:", stealth_data.url)
    print("Number of internal links:", len(stealth_data.internal_links))
    print("Number of external links:", len(stealth_data.external_links))
    print("Text content length:", len(stealth_data.text_content))

if __name__ == "__main__":
    main()
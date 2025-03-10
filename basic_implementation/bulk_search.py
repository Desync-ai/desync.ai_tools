from desync_search import DesyncClient
import os

def main():
    my_api_key = os.environ.get("DESYNC_API_KEY")
    client = DesyncClient(my_api_key)

    # A list of URLs to search
    target_list = [
        "https://example.com",
        "https://www.ycombinator.com/",
        # ... up to 1000
    ]

    # Initiate the bulk search
    bulk_info = client.bulk_search(target_list=target_list, extract_html=False)

    print("Message:", bulk_info.get("message"))
    print("Bulk Search ID:", bulk_info.get("bulk_search_id"))
    print("Total links scheduled:", bulk_info.get("total_links"))
    print("Credits cost charged:", bulk_info.get("cost_charged"))

if __name__ == "__main__":
    main()

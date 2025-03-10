from desync_search import DesyncClient
import os

def main():
    my_api_key = os.environ.get("DESYNC_API_KEY")
    client = DesyncClient(my_api_key)
            
    # Crawl up to 3 levels deep on the same domain
    all_pages = client.crawl(
        start_url="https://www.sequoiacap.com/",
        max_depth=2,
        scrape_full_html=False,     # Set True if you need HTML content
        remove_link_duplicates=True # Avoid repeated links
    )

    print(f"Discovered {len(all_pages)} unique pages")

    for page in all_pages:
        print("URL:", page.url, "| Depth:", getattr(page, "depth", None))

if __name__ == "__main__":
    main()

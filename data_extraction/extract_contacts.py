import re
from typing import List, Dict
from desync_search import DesyncClient
from desync_search.data_structures import PageData


def extract_contacts(pages: List[PageData]) -> List[Dict]:
    """
    Extracts contact info (emails, LinkedIn, phones, Twitter, GitHub, Calendly, websites)
    using regex.

    Args:
        pages (List[PageData]): List of DesyncClient PageData objects.

    Returns:
        List[Dict]: One dictionary per page with extracted fields.
    """
    results = []

    # Patterns
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_regex = r"\(?\+?\d{1,3}\)?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    twitter_regex = r"https?://(?:www\.)?(?:x|twitter)\.com/[a-zA-Z0-9_]+"
    github_regex = r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+"
    calendly_regex = r"https?://(?:www\.)?calendly\.com/[a-zA-Z0-9_-]+"
    linkedin_regex = r"https?://(?:www\.)?linkedin\.com/[a-zA-Z0-9/_%-]+"
    website_regex = r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\"'\s<>]*"

    # Extract all href links
    href_regex = r'href=["\'](https?://[^"\']+)["\']'

    for page in pages:
        content = page.text_content or ""
        html = page.html_content or ""

        def find_all(regex):
            return set(re.findall(regex, content) + re.findall(regex, html))

        all_links = set(re.findall(href_regex, html)) | find_all(website_regex)

        # Filter links by type
        linkedins = {l for l in all_links if "linkedin.com" in l}
        twitters = {l for l in all_links if "twitter.com" in l or "x.com" in l}
        githubs = {l for l in all_links if "github.com" in l}
        calendlys = {l for l in all_links if "calendly.com" in l}
        websites = {l for l in all_links if not any(s in l for s in [
            "linkedin.com", "twitter.com", "x.com", "github.com", "calendly.com"
        ])}

        results.append({
            "url": page.url,
            "emails": sorted(find_all(email_regex)),
            "linkedins": sorted(linkedins),
            "phones": sorted(find_all(phone_regex)),
            "twitters": sorted(twitters),
            "githubs": sorted(githubs),
            "calendlys": sorted(calendlys),
            "websites": sorted(websites),
        })

    return results

if __name__ == "__main__":
    client = DesyncClient()

    pages = client.crawl(
        start_url="https://www.sequoiacap.com/our-companies/",
        max_depth=1,
        scrape_full_html=True,
        remove_link_duplicates=True
    )

    contacts = extract_contacts(pages)

    all_emails = set()
    all_linkedins = set()
    all_phones = set()
    all_twitters = set()
    all_githubs = set()
    all_calendlys = set()
    all_websites = set()

    for entry in contacts:
        all_emails.update(e.strip().rstrip(".,;:").lower() for e in entry["emails"])
        all_linkedins.update(link.strip().rstrip("/") for link in entry["linkedins"])
        all_phones.update(p.strip() for p in entry["phones"])
        all_twitters.update(t.strip().rstrip("/") for t in entry["twitters"])
        all_githubs.update(g.strip().rstrip("/") for g in entry["githubs"])      # There aren't supposed to be any GitHubs
        all_calendlys.update(c.strip().rstrip("/") for c in entry["calendlys"])  # There aren't supposed to be any Calendlys either :)

    print("\n=== Summary of Extracted Contacts ===")
    print("\nEmails:", sorted(all_emails))
    print("\nLinkedIns:", sorted(all_linkedins))
    print("\nPhones:", sorted(all_phones))
    print("\nTwitters:", sorted(all_twitters))

# /parsers/link_graph.py

"""
link_graph.py

Builds a link graph from DesyncClient PageData objects.

Use cases:
    - Visualize internal link structure
    - Explore outbound links to uncrawled/external pages
    - Build sitemaps, PageRank graphs, or graph-based ML input

Author: Jackson-Ballow
"""

from typing import List, Tuple
from desync_search.data_structures import PageData
from urllib.parse import urlparse


def extract_link_graph(
    pages: List[PageData],
    include_external_links: bool = False,
    only_include_crawled_pages: bool = False
) -> List[Tuple[str, str]]:
    """
    Extracts a list of (source_url, destination_url) edges from PageData objects.

    Args:
        pages (List[PageData]): DesyncClient results with .internal_links populated.
        include_external_links (bool): If False, skips links to other domains.
        only_include_crawled_pages (bool): If True, restricts to known crawled URLs.

    Returns:
        List[Tuple[str, str]]: Directed edges (source → destination)
    """
    edges = []
    crawled_urls = {page.url for page in pages}

    for page in pages:
        source_domain = urlparse(page.url).netloc

        for link in page.internal_links:
            dest_domain = urlparse(link).netloc

            if not link:
                continue  # skip empty links

            if not include_external_links and dest_domain and dest_domain != source_domain:
                continue  # skip cross-domain links

            if only_include_crawled_pages and link not in crawled_urls:
                continue  # skip uncrawled links if toggled

            edges.append((page.url, link))

    return edges


# === Example Usage ===
if __name__ == "__main__":
    from desync_search import DesyncClient

    print("Crawling site …")
    client = DesyncClient()
    pages = client.crawl(
        start_url="https://www.137ventures.com/team",
        max_depth=1,
        scrape_full_html=False,
        remove_link_duplicates=True
    )

    print(f"Retrieved {len(pages)} pages")

    include_external_links = False      # Change this to include links to external URL's
    only_include_crawled_pages = False  # Change this to only include URLs you visited on your search

    print(f"Building link graph (external={include_external_links}, crawled_only={only_include_crawled_pages}) …")
    graph_edges = extract_link_graph(
        pages,
        include_external_links=include_external_links,
        only_include_crawled_pages=only_include_crawled_pages
    )

    for src, dst in graph_edges[-10:]:
        print(f"{src}  →  {dst}")

    print(f"📦 Extracted {len(graph_edges)} total edges")

    try:
        import networkx as nx
        import matplotlib.pyplot as plt
    except ImportError:
        print("To visualize, run: pip install matplotlib networkx")
        exit()

    G = nx.DiGraph()
    G.add_edges_from(graph_edges)

    plt.figure(figsize=(12, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=800, node_color="skyblue", arrows=True, font_size=8)
    plt.title("Link Graph Visualization")
    plt.tight_layout()
    plt.show()

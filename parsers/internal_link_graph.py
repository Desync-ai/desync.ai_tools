# /parsers/internal_link_graph.py

"""
internal_link_graph.py

Builds a link graph from DesyncClient PageData objects.
Each edge represents a hyperlink from one crawled page to another.

Use case:
    - Visualize how internal pages link to each other
    - Build a sitemap or dependency graph
    - Feed into graph-based ML or PageRank analysis

Author: Jackson-Ballow
"""

from typing import List, Tuple
from desync_search.data_structures import PageData


def extract_internal_link_graph(pages: List[PageData]) -> List[Tuple[str, str]]:
    """
    Extracts a list of (source_url, destination_url) edges from PageData objects.

    Args:
        pages (List[PageData]): DesyncClient results with .internal_links populated.

    Returns:
        List[Tuple[str, str]]: Directed edges from one URL to another.
    """
    edges = []
    url_set = {page.url for page in pages}  # Optional: restrict links to crawled pages

    for page in pages:
        for link in page.internal_links:
            if link in url_set:
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

    print("Building link graph and displaying last 10 edges …")
    graph_edges = extract_internal_link_graph(pages)
    for src, dst in graph_edges[-10:]:  # Only print the last 10 links
        print(f"{src}  →  {dst}")

    print(f"Extracted {len(graph_edges)} total edges")

    try:
        import networkx as nx
        import matplotlib.pyplot as plt
    except:
        print("To see the visualized graph run: pip install matplotlib networkx")
        exit(0)

    # Visualize the graph
    print("Visualizing partial graph …")
    G = nx.DiGraph()
    G.add_edges_from(graph_edges)

    plt.figure(figsize=(12, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color="lightblue", arrows=True, font_size=8)
    plt.title("Link Graph (Sample)")
    plt.tight_layout()
    plt.show()


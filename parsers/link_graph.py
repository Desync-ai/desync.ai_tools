# parsers/link_graph.py

"""
Builds a link graph from DesyncClient PageData objects
using `desync_data.extract_link_graph`.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from desync_data import extract_link_graph

# Initialize the DesyncClient
client = DesyncClient()
# client = DesyncClient(user_api_key="your_api_key_here") # Alternative initialization

# Perform a crawl to get pages with links
pages = client.crawl(start_url="https://www.137ventures.com/team", max_depth=1)

# Define graph parameters
include_external_links = False     # Set to True to include links to other domains
only_include_crawled_pages = False # Set to True to limit to URLs you visited on this crawl


# Extract the link graph edges
graph_edges = extract_link_graph(
    pages,
    include_external_links=include_external_links,
    only_include_crawled_pages=only_include_crawled_pages
)

# Display the extracted edges (showing the last few for brevity)
print(f"Extracted {len(graph_edges)} total edges.")
print("\nExample Link Edges (Source → Destination):")
if graph_edges:
    # Print up to the last 10 edges, or fewer if there aren't that many
    for src, dst in graph_edges[-10:]:
        print(f"  {src} → {dst}")
else:
    print("No link edges were extracted based on the criteria.")
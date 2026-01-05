from collections import defaultdict
from urllib.parse import urlparse

import graphviz
from bs4 import BeautifulSoup
import re
import requests


def normalize(x, xmin, xmax):
    return 1 + (x - xmin) * 2 / (xmax - xmin)


def concat_defaultdicts(dict_one: defaultdict, dict_two: defaultdict):
    for k, v in dict_two.items():
        if k in dict_one:
            dict_one[k].update(dict_two[k])
        else:
            dict_one[k] = dict_two[k]
    return dict_one


def get_root(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_site_search_allowed(root_url: str, permissions: defaultdict[str, bool]) -> bool:
    # Check if this file was already looked at.
    if root_url in permissions:
        return permissions[root_url]

    # Handle the file.
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        robots = requests.get(root_url + "/robots.txt", headers=headers, timeout=5).text
        disallowed = re.search(r"Disallow:\\s*/", robots)
        allowed = re.match("Allow:\\s*/$", robots)

        is_allowed = (allowed and not disallowed) or (not allowed and not disallowed)
        permissions[root_url] = is_allowed

        return is_allowed
    except requests.RequestException:
        return False


def draw_graph(graph: defaultdict[str, set[str]], named_ranks: list, url: str):
    root_url = get_root(url)
    root_wo_column = root_url.replace(":", "")
    graph_name = f"{root_wo_column}_crawler_graph"
    dot = graphviz.Digraph(comment=graph_name)
    dot.node(root_wo_column, style="filled", fillcolor="green")
    dot.attr(rankdir='LR')

    # Create a dictionary for easy lookup of ranks
    rank_dict = {name: float(rank) for rank, name in named_ranks}

    # Find min and max ranks for scaling
    min_rank = None
    max_rank = None
    if rank_dict:
        min_rank = min(rank_dict.values())
        max_rank = max(rank_dict.values())

    for node in graph:
        root_node = True if node == root_url else False

        if node in rank_dict and min_rank is not None and max_rank is not None:
            size = normalize(rank_dict[node], min_rank, max_rank)

            normalized_rank = (rank_dict[node] - min_rank) / (max_rank - min_rank) if max_rank != min_rank else 1

            gray_value = int(235 - (normalized_rank * 135))  # From #EBEBEB (light) to #646464 (dark)
            color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"

            dot.node(
                name=node.replace(":", ""),
                label=f"{url}\\nRank: {float(rank_dict[node]):.10f}",
                style="filled",
                fillcolor="green" if root_node else color,
                height=str(size),
                width=str(size) if size >= 2 else "2",
                fixedsize="true"
            )
        else:
            dot.node(
                node.replace(":", ""),
                style="filled",
                fillcolor="green" if root_node else "white"
            )

    for u in graph:
        for v in graph[u]:
            dot.edge(u.replace(":", ""), v.replace(":", ""))

    dot.render(f'graphs/{graph_name}.gv', cleanup=True)


def search_site(url: str, max_depth: int, sites: defaultdict[str, set[str]],
                permissions: defaultdict[str, bool]) -> defaultdict[str, set[str]]:
    # Site already visited.
    root_url = get_root(url)

    if root_url in sites and len(sites.get(root_url)) > 0:
        return sites

    if not is_site_search_allowed(root_url, permissions):
        print(f"Site {root_url} doesnt allow crawlers.")
        return sites

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        html = requests.get(root_url, headers=headers, timeout=5).text
        soup = BeautifulSoup(html, 'html.parser')
        hyperlinks = set([get_root(link.get('href')) for link in soup.find_all('a', attrs={'href': re.compile("^https://")})])
    except requests.RequestException:
        return sites

    # Add nodes (hyperink roots) to graph.
    for link in hyperlinks:
        if link not in sites:
            sites[link] = set()

    sites[root_url] = set(filter(lambda link: link != root_url, hyperlinks))

    if max_depth > 1:
        for link in hyperlinks:
            if link not in sites or len(sites[link]) == 0:
                search_site(link, max_depth - 1, sites, permissions)

    return sites

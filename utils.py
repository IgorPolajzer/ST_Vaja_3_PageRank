from collections import defaultdict
from urllib.parse import urlparse

import graphviz
from bs4 import BeautifulSoup
import re
import requests


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


def is_site_allowed(url: str, permissions: defaultdict[str, bool]) -> bool:
    root_url = get_root(url)

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


def draw_graph(graph, s, graph_name):
    dot = graphviz.Digraph(comment=graph_name)
    dot.node(s.replace(":", ""), style="filled", fillcolor="green")
    dot.attr(rankdir='LR')

    for u in graph:
        for v in graph[u]:
            dot.edge(u.replace(":", ""), v.replace(":", ""))

    dot.render(f'graphs/{graph_name}.gv')


def search_page(url: str, max_depth: int, sites: defaultdict[str, set[str]], permissions: defaultdict[str, bool]) -> defaultdict[str, set[str]]:
    if url in sites:
        return sites

    if not is_site_allowed(url, permissions):
        print(f"Site {url} doesnt allow crawlers.")
        return sites

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        html = requests.get(url, headers=headers, timeout=5).text
        soup = BeautifulSoup(html, 'html.parser')
        hyperlinks = set([link.get('href') for link in soup.find_all('a', attrs={'href': re.compile("^https://")})])
    except requests.RequestException:
        return sites

    for link in hyperlinks:
        if link not in sites:
            sites[link] = set()

    sites[url] = hyperlinks

    if max_depth > 0:
        for link in hyperlinks:
            if link not in sites or len(sites[link]) == 0:
                search_page(link, max_depth - 1, sites, permissions)

    return sites

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


def is_site_allowed(url: str) -> bool:
    url = get_root(url)
    robots = requests.get(url + "/robots.txt").text
    disallowed = re.match(r"^Disallow:\\s*/$", robots)
    allowed = re.match("^Allow:\\s*/$", robots)

    return (allowed and not disallowed) or (not allowed and not disallowed)


def draw_graph(graph, s, graph_name):
    dot = graphviz.Digraph(comment=graph_name)
    dot.node(s.replace(":", ""), style="filled", fillcolor="green")
    dot.attr(rankdir='LR')

    for u in graph:
        for v in graph[u]:
            dot.edge(u.replace(":", ""), v.replace(":", ""))

    dot.render(f'graphs/{graph_name}.gv')


def search_page(url: str, max_depth: int, sites: defaultdict[str, set[str]]) -> defaultdict[str, set[str]]:
    if sites is None:
        sites = defaultdict(set)

    if not is_site_allowed(url):
        print(f"Site {url} doesnt allow crawlers.")
        return sites

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    hyperlinks = set([link.get('href') for link in soup.find_all('a', attrs={'href': re.compile("^https://")})])
    sites[url] = hyperlinks

    if max_depth > 0:
        for link in hyperlinks:
            if link not in sites:
                concat_defaultdicts(sites, search_page(link, max_depth - 1, sites))

    return sites

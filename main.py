import time
from collections import defaultdict

from utils import search_page, draw_graph

if __name__ == '__main__':
    # depth = input("Configure the maximum allowed crawler depth: ")
    depth = 1
    start = time.time()
    url = "https://igorpolajzer.com"
    sites = search_page(url, depth, defaultdict(set))
    print(f"Exec time: {time.time() - start}")
    print(sites)
    draw_graph(sites, "https://google.com", "crawler_graph")

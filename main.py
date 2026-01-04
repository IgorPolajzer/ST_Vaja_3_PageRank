import time
from collections import defaultdict
import numpy as np

from utils import search_page, draw_graph


def init_test_graph() -> defaultdict[str, set[str]]:
    graph = defaultdict(set)

    graph["y"] = {"y", "a"}
    graph["a"] = {"y", "m"}
    graph["m"] = {"m"}

    return graph


def init_matrices(graph: defaultdict[str, set[str]]) -> np.array:
    n = len(graph)
    r = 1 / n

    # Init r0.
    r = np.full(n, r)

    # Init N.
    N = np.full((n, n), r)

    # Init M.
    M = np.zeros((n, n))

    # Parse to dict for O(1) lookup.
    graph_positions = {page: i for i, page in enumerate(list(graph.keys()))}

    for idx, page in enumerate(graph):
        # Slice column view of matrix.
        col_view = M[:, idx]
        for connection in graph[page]:
            connection_idx = graph_positions[connection]
            non_zero_count = np.count_nonzero(col_view)
            col_view[connection_idx] = 1

            if non_zero_count > 0:
                col_view[col_view != 0] = 1 / (non_zero_count + 1)

    return M, N, r


def init_N(graph: defaultdict[str, set[str]]) -> np.array:
    n = len(graph)
    r = 1 / n
    N = np.full((n, n), r)



if __name__ == '__main__':
    # depth = input("Configure the maximum allowed crawler depth: ")
    # depth = 0
    #
    # start = time.time()
    # url = "https://www.google.com"
    # graph = search_page(url, depth, defaultdict(set))
    # print(f"Exec time: {time.time() - start}")

    B = 0.8
    epsilon = 1e-4 # 1 * 10 ^ -4

    graph = init_test_graph()
    M, N, r_new = init_matrices(graph)
    A = (B * M) + ((1 - B) * N)

    print(r_new)
    delta = None
    while delta is None or delta > epsilon:
        r_old = r_new
        r_new = A.dot(r_old.T)
        delta = np.sum(np.abs(r_new - r_old))

        print(f"Rank: {r_new}")

    indices = np.argsort(-r_new)
    sorted_ranks = r_new[indices]

    top_number = 5 if len(graph) >= 5 else 1
    top_five = sorted_ranks[:top_number]

    print(f"First {top_number} web pages according to PageRank: {top_five}")

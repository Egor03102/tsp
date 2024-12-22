import networkx as nx
import matplotlib.pyplot as plt
from itertools import batched



def read_graph(name, only_nodes=False):
    with open(f'graphs/positions/{name}.txt', "r") as f:
        nodes = list(batched(f.read().split(','), 3))

    if not only_nodes:
        with open(f'graphs/roads/{name}.txt', "r") as f:
            roads = list(batched(f.read().split(','), 3))
        return nodes, roads
    return nodes


def add_nodes(graph, nodes):
    for n, x, y in nodes:
        graph.add_node(n, pos=(int(x), int(y)))

def add_edges(graph, edges, with_color=False):
    if not with_color:
        for first, second, _ in edges:
            graph.add_edge(first, second)
    else:
        for first, second in edges:
            graph.add_edge(first, second)


def draw_graph(graph, path_file, edge_colors='black'):
    pos = nx.get_node_attributes(graph, 'pos')
    nx.draw(graph, pos=pos, with_labels=True, edge_color=edge_colors)
    plt.savefig(path_file, bbox_inches='tight',dpi=200,pad_inches=-0.1)
    plt.close()

     
def image_graph(name):
    G = nx.Graph()
    nodes, roads = read_graph(name)
    add_nodes(G, nodes[:-1])

    add_edges(G, roads[:-1])
    
    draw_graph(G, f"graphs/images/{name}.png")
    

def image_solved_graph(name, path):
    G = nx.Graph()
    nodes = read_graph(name, only_nodes=True)
    add_nodes(G, nodes[:-1])
    colored_edges = []

    path = [str(i + 1) for i in path]
    previous = path[0]
    for n in path[1:]:
        colored_edges.append((previous, n))
        previous = n
    add_edges(G, colored_edges, with_color=True)

    draw_graph(G, f"graphs/solutions/{name}.png", edge_colors='g')




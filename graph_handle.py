import networkx as nx
import matplotlib.pyplot as plt
from itertools import batched
import sqlite3 as sql
from math import sqrt

def points_to_db(cursor, name, points):
    for point, x, y in points:
        cursor.execute('INSERT INTO points VALUES (?,?,?,?)', (name, point, x, y))

def roads_to_db(cursor, name, count):
    points = cursor.execute(f'SELECT point, x, y FROM points WHERE name="{name}"').fetchall()
    dp = {}
    for i, x, y in points:
        dp[i] = (x, y)

    for i in range(1, count + 1):
        for j in range(i + 1,count + 1):
            cursor.execute('INSERT INTO roads VALUES (?,?,?,?)', (name, i, j, sqrt(((dp[i][0] - dp[j][0])**2) + ((dp[i][1] - dp[j][1])**2))))

def graph_to_db(graph):
    bd = sql.connect('solver.db')
    cr = bd.cursor()
    points_to_db(cr, graph.name, graph.points)
    roads_to_db(cr, graph.name, graph.count)
    bd.commit()
    bd.close()


def read_graph(name, only_nodes=False):
    bd = sql.connect('solver.db')
    cr = bd.cursor()
    nodes = cr.execute('SELECT point, x, y FROM points WHERE name=?', (name,)).fetchall()
    if not only_nodes:
        roads = cr.execute(f'SELECT one, two, dist FROM roads WHERE name=?',(name,)).fetchall()
        bd.close()
        return nodes, roads
    bd.close()
    return nodes


def add_nodes(graph, nodes):
    for n, x, y in nodes:
        graph.add_node(n, pos=(x, y))

def add_edges(graph, edges):
    for first, second, _ in edges:
        graph.add_edge(first, second)


def draw_graph(graph, path_file, edge_colors='black'):
    pos = nx.get_node_attributes(graph, 'pos')
    nx.draw(graph, pos=pos, with_labels=True, edge_color=edge_colors)
    plt.savefig(path_file, bbox_inches='tight',dpi=200,pad_inches=-0.1)
    plt.close()

     
def image_graph(name):
    G = nx.Graph()
    nodes, roads = read_graph(name)
    add_nodes(G, nodes)

    add_edges(G, roads)
    
    draw_graph(G, f"assets/images/{name}.png")
    

def image_solved_graph(name, path):
    G = nx.Graph()
    nodes = read_graph(name, only_nodes=True)
    add_nodes(G, nodes)
    colored_edges = []
    path = [i + 1 for i in path]
    previous = path[0]
    for n in path[1:]:
        colored_edges.append((previous, n, 0))
        previous = n
    add_edges(G, colored_edges)

    draw_graph(G, f"assets/solutions/{name}.png", edge_colors='g')




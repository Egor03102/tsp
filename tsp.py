from itertools import batched
import numpy

from ants import Colony

from cnf import ITERATIONS

from graph_handle import image_solved_graph

import sqlite3 as sql

class Graph:
    def __init__(self, name):
        self.name = name
        self.count = 0 
        self.roads = self.generate_array_roads()

        self.cities = {} # key is name of city and value is tuple (number of city, visited (0 or 1))
        self.add_cities(self.count)

    
    def generate_array_roads(self):
        bd = sql.connect('solver.db')
        cr = bd.cursor()
        roads_list = cr.execute('SELECT one, two, dist FROM roads WHERE name=?', (self.name,)).fetchall()
        bd.close()

        self.count = roads_list[-1][1]
        roads_array = numpy.zeros((self.count, self.count), dtype=int)
        for x, y , weight in roads_list:
            roads_array[x - 1][y - 1] = roads_array[y - 1][x - 1] = weight 
        return roads_array
    
    def add_cities(self, n):
        for i in range(n):
            self.cities[i] = 0
    
    def solve_aco(self):
        colony = Colony(self.count)
        for i in range(ITERATIONS):
            colony.move_colony(self.cities, self.roads)
        return colony.get_best_ant() # distance and path in tuple










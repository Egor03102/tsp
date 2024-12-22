
import numpy

import copy

from random import choice

from cnf import ALPHA, BETA, EVAPORATION, ANTS_FACTOR

class Colony:
    def __init__(self, count_cities):
        self.number_ants = round(ANTS_FACTOR * count_cities)

        self.ant_colony = []

        self.setup_ants()

        self.best_distance = 0
        self.best_path = []

        self.pheromones = numpy.ones((count_cities, count_cities))
        for i in range(len(self.pheromones)):
            self.pheromones[i][i] = 0

    def setup_ants(self):
        for i in range(0, self.number_ants):
            self.ant_colony.append(Ant())
    
    def move_colony(self, cities, roads):
        for i in range(self.number_ants):
            ant = self.ant_colony[i]
            ant.visit_all_cities(roads, copy.deepcopy(cities), self.pheromones)
            self.update_pheromones(ant.distance, ant.path)
   
        self.update_best_ant()
        


    def update_pheromones(self, distance, path):
        self.pheromones *= EVAPORATION
        k = 1 / distance
        for i in range(len(path) - 2):
            self.pheromones[path[i]][path[i + 1]] += k
            self.pheromones[path[i + 1]][path[i]] += k
    
    def update_best_ant(self):
        if self.best_distance == 0:
            self.best_distance = self.ant_colony[0].distance
            self.best_path = self.ant_colony[0].path
        for ant in self.ant_colony:
            if self.best_distance > ant.distance:
                self.best_distance = ant.distance
                self.best_path = ant.path

    def get_best_ant(self):
        return self.best_distance, self.best_path
        
        
class Ant:
    def __init__(self):
        self.path = []
        self.distance = 0

        self.current_city = None
        self.start = None
    
    def visit_all_cities(self, roads, cities, pheromones):
        self.cities = cities

        self.roads = roads
        self.connections = {}
        self.path = []
        self.distance = 0
        self.select_random_city()

        self.chances = {}

        for i in range(len(self.cities)):
            self.available_cities()
            if self.connections == {}:
                self.distance += self.roads[self.current_city][self.path[0]]
                self.path.append(self.path[0])
                break
            self.compute_chances(pheromones)
            self.visit_next_city()
        

    def visit_next_city(self):
        max_chance = 0
        for city, chance in self.chances.items():
            if chance > max_chance:
                max_chance = chance
                next_city = city

        self.distance += self.connections[next_city]
        self.path.append(next_city)
        self.cities[self.current_city] = 1
        self.current_city = next_city
       
    def compute_chances(self, pheromones):
        self.chances = {}
        pheromones_on_path = pheromones[self.current_city]
        sum_pheromones = numpy.sum(pheromones_on_path)
        sum_weights = sum(self.connections.values())
        for index, weight in self.connections.items():
            self.chances[index] = ((pheromones_on_path[index])**ALPHA * (1 / weight)**BETA) / ((sum_pheromones)**ALPHA * (1 / sum_weights)**BETA)


    def select_random_city(self):
        self.current_city = choice(list(self.cities.keys()))
        self.path.append(self.current_city)

    
    def available_cities(self):
        self.connections = {}
        for city, visited in self.cities.items():
            if not visited and city != self.current_city:
                self.connections[city] = self.roads[self.current_city][city]
        


# Solver TSP

The app for solving travelling salesman problem using the ant optimization algorithm.

## Installation

Install zip archive and extract all in some folder

Create venv if you need, then install requirements, use:
pip install -r requirements.txt
And all, you can run it.
flet run main.py
## How works ACO
The ant.py is the code with algorithm.
In summary, the first ant in colony go through all cities and leave the pheromones. The next ant go through all cities too, but it takes into account the pheromones of the past. Like in nature. 

The cnf.py configure the algorithm. a impact on distance to city, b on pheromones.

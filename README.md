# Solver TSP

The app for solving travelling salesman problem using the ant optimization algorithm.

## Installation

Install zip archive and extract all in some folder

Create venv if you need, then install requirements, use:
``` bash
pip install -r requirements.txt
```
And all, you can run it.
``` bash
flet run main.py
```
## How works ACO
The ant.py is the code with algorithm.<br>
In summary, the first ant in colony go through all cities and leave the pheromones. The next ant go through all cities too, but it takes into account the pheromones of the past. Like in nature. 

The cnf.py contains the settings of algorithm.

# Solver TSP (RU)
Приложение для решения задачи коммивояжера с использованием алгоритма машинного обучения - муравьиный интеллект.
## Установка
Установите zip-архив и извлеките все в папку
Создайте venv, если нужно, затем установите зависимости, используйте:
``` bash
pip install -r requirements.txt
```
И все, вы можете запускать его.
```bash
flet run main.py
```
## Как работает алгоритм
ant.py Это код с алгоритмом. <br>    
Коротко, первый муравей в колонии проходит через все города и оставляет феромоны. Следующий муравей также посещает все города, но с учетом феромонов прошлого. Как в природе. <br>
cnf.py содержит настройки алгоритма


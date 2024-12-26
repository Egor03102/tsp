import flet as ft
import flet.canvas as cs

import graph_handle

import pandas as pd
import os
from random import randint

from itertools import batched

from numpy import asarray
from base64 import b64encode as en
from io import BytesIO
from PIL import Image as img

from tsp import Graph


if not os.path.exists('graphs'):
    os.mkdir('graphs')
if not os.path.exists('graphs/positions'):
    os.makedirs('graphs/positions')
if not os.path.exists('graphs/images'):
    os.makedirs('graphs/images')
if not os.path.exists('graphs/roads'):
    os.makedirs('graphs/roads')
if not os.path.exists('graphs/solutions'):
    os.makedirs('graphs/roads')

class NewGraph: # класс для описания графа
    name: str
    roads = ''
    nodes = ''
    count = 0

class tspView(ft.Container): # класс для списка задач
    def __init__(self, name):
        super().__init__()
        self.on_click = self.preview
        self.name = name

        btn_delete = ft.IconButton(icon=ft.icons.DELETE, icon_color='red')
        btn_delete.on_click = self.delete_tsp

        row = ft.Row([ft.Text(self.name, size=21, weight='bold'), btn_delete], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.content = row

    def delete_tsp(self, e): # удаление задачи полностью
        os.remove(f'graphs/images/{self.name}.png')
        os.remove(f'graphs/positions/{self.name}')
        os.remove(f'graphs/roads/{self.name}')
        self.parent.controls.remove(self)
        self.page.update()

    def preview(self, e): # добавление меню с preview
        if len(self.parent.parent.controls[2].controls) == 2:
            self.parent.parent.controls[2].controls.pop(1)
        self.parent.parent.controls[2].visible = True
        self.parent.parent.controls[1].visible = False
        self.parent.parent.controls[0].visible = False
        graph.name = self.name
        self.page.update()

class RoadsList(ft.Row):
    def __init__(self, first, second, weight, name):
        super().__init__()
        self.name = name
        self.expand = True

        self.first = first
        self.second = second

        self.field = ft.TextField(hint_text='Введите новый вес')
        self.weight = weight
        self.field.value = str(self.weight)

        self.field.on_submit = self.new_weight

        self.alignment = ft.MainAxisAlignment.CENTER
        self.controls = [ft.Text(str(first), size=25), ft.Text(str(second), size=25), self.field]
    def new_weight(self, e):
        with open(f"graphs/roads/{self.name}.txt", 'r') as r:
            roads = r.read()
        with open (f"graphs/roads/{self.name}.txt", "w") as r:
            r.write(roads.replace(f'{self.first},{self.second},{self.weight}',
            f'{self.first},{self.second},{e.control.value}'))

class PointsList(ft.Row):
    def __init__(self, n, name):
        super().__init__()
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.n = n
        self.name = name

        self.field = ft.TextField(hint_text='Введите новое имя')
        self.field.on_submit = self.new_name

        self.controls = [ft.Text(n, size=25), self.field]

    def new_name(self, e):
        with open(f"graphs/positions/{self.name}.txt", "r") as f:
            string = f.read().split(',')

        with open(f"graphs/positions/{self.name}.txt", "w") as f:
            f.write(",".join(self.new_string(string, e.control.value)))

        with open(f"graphs/roads/{self.name}.txt", "r") as f:
            string = f.read().split(',')

        with open(f"graphs/roads/{self.name}.txt", "w") as f:
            f.write(",".join(self.new_string(string, e.control.value)))

        os.remove(f"graphs/images/{self.name}.png")
        graph_handle.image_graph(self.name)

    def new_string(self, string, new_value):
        for index, i in enumerate(string):
            if i == self.n:
                string[index] = new_value
        return string

graph = NewGraph()


def main(page: ft.Page):
    page.title = 'Solver TSP'
    def pan_start(e: ft.DragStartEvent): # нажатие на canvas
        graph.count += 1
        graph.nodes += f"{graph.count},{int(e.local_x)},{int(page.height - int(e.local_y))},"
        cv.shapes.append( # рисование круга
            cs.Circle(x=e.local_x, y=e.local_y,radius=5, paint=ft.Paint(stroke_width=3)
            )
        )
        cv.update()
        check_next(ft.ControlEvent)

    def check_next(e): # проверка
        if graph.count > 3 and name.value:
            btn_next.disabled = False
        else:
            btn_next.disabled = True
        page.update()

    def new_tsp(e): # показ canvas, кнопка на левой панели Новая задача
        if graph.count != 0:
            graph.roads = ""
            graph.name = ''
            graph.nodes = ""
            graph.count = 0
        main.controls[2].visible = False
        main.controls[3].visible = True
        main.controls[4].visible = False
        page.update()

    def clear_canvas(e): # очистка canvas, кнопка Очистить
        cv.shapes.clear()
        name.value = ''
        btn_next.disabled = True

        graph.nodes = ""
        graph.count = 0
        page.update()

    def complete_tsp(e): # кнопка Готово
        graph_handle.image_graph(graph.name) # генерация графа
        roads.visible = False
        saveline.visible = False
        creating.controls.append(ft.Image(
            src=f"graphs/images/{graph.name}.png",
            expand=True,
        ))
        page.update()

        saveline.visible = True
        cv.visible = True
        roads.visible = False
        name.value = ''
        roads.controls[1].controls[1].value = ''
        creating.controls.pop(3)
        cv.shapes.clear()
        saveline.controls = [btn_clear, name, btn_next]

    def next(e): # кнопка Далее
        saveline.controls = [btn_complete]
        cv.visible = False
        roads.visible = True
        page.update()
        graph.name = name.value
        with open(f'graphs/positions/{graph.name}.txt', "w") as f:
            f.write(graph.nodes)

    def count_roads(n: int): # вычисление количества дорог (сумма от 1 до n - 1 точек)
        count = 0
        for i in range(1, n):
            count += i
        return count


    def generate_roads(e): # генерация дорог после нажатия Enter, в меню генерации при создании
        try:
            n = int(e.control.value)
        except ValueError:
            pass
        else:
            for i in range(1, graph.count + 1):
                for j in range(i + 1, graph.count + 1):
                    graph.roads += f"{i},{j},{randint(1, n)},"

            btn_complete.disabled = False
            page.update()

            with open(f"graphs/roads/{graph.name}.txt", 'w') as r:
                r.write(graph.roads)

    def generateListView(names: list):
        if len(tsps.controls) != 0:
             tsps.controls.clear()
        for i in names:
            tsps.controls.append(tspView(name=i))

    def searching(e):
        if e.control.value != '':
            nameSearch = [x for x in names if x.startswith(e.control.value)]
            generateListView(nameSearch)
        else:
            generateListView(names)
        tsps.update()

    def rail_change(e): # нажатия на левую панель
        if e.control.selected_index == 0:
            main.controls[2].visible = True
            main.controls[3].visible = False
            main.controls[4].visible = False
            if preview in view.controls:
                view.controls[0].visible = True
                view.controls[1].visible = True
                view.controls[2].visible = False
            names = [x.split('.')[0] for x in os.listdir('graphs/images')]
            generateListView(names)
        elif e.control.selected_index == 1:
            main.controls[2].visible = False
            main.controls[3].visible = False
            main.controls[4].visible = True
        page.update()

    # функции preview
    def image_preview(e): # добавляет фотку при нажатии на кнопку Фото
        print(preview.controls)
        if len(preview.controls) == 2:
            preview.controls.pop()
        image1 = ft.Image()
        pil_photo = img.open(f"graphs/images/{graph.name}.png")
        arr = asarray(pil_photo)
        pil_img = img.fromarray(arr)
        buff = BytesIO()
        pil_img.save(buff, format="png")

        newstring = en(buff.getvalue()).decode("utf-8")
        image1.src_base64 = newstring
        preview.controls.append(image1)
        page.update()
        image1.update()

    def generate_roads_list(name):
        roadsList.controls.clear()
        with open(f"graphs/roads/{name}.txt", "r") as f:
            weights = list(batched(f.read().split(','), 3))
        for i in weights[:-1]:
            roadsList.controls.append(RoadsList(i[0], i[1], i[2], name))

    def roads_preview(e):
        if len(preview.controls) == 2:
            preview.controls.pop()
        preview.controls.append(roadsList)
        generate_roads_list(graph.name)
        page.update()

    """def generate_points_list(name):
        nodesList.controls.clear()
        with open(f"graphs/positions/{name}.txt","r") as f:
            nodes = list(batched(f.read().split(','), 3))
        for i in nodes[:-1]:
            nodesList.controls.append(PointsList(i[0], name))

    def points_preview(e):
        if len(preview.controls) == 2:
            preview.controls.pop(1)
        preview.controls.append(nodesList)
        generate_points_list(graph.name)
        page.update()"""
    def solve(e):
        tsp = Graph(graph.name)

        distance, path = tsp.solve_aco()

        graph_handle.image_solved_graph(graph.name, path)
        

        if len(preview.controls) == 2:
            preview.controls.pop()
        solved_image = ft.Image()

        pil_photo = img.open(f"graphs/solutions/{graph.name}.png")
        arr = asarray(pil_photo)
        pil_img = img.fromarray(arr)
        buff = BytesIO()
        pil_img.save(buff, format="png")

        newstring = en(buff.getvalue()).decode("utf-8")
        solved_image.src_base64 = newstring

        solution = ft.Column([ft.Text(f'Дистанция: {distance}', size=25, weight='bold'), solved_image],
                             expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        preview.controls.append(solution)
        page.update()
        solved_image.update()
        




    rail = ft.NavigationRail(min_width=100,
                             min_extended_width=400,
                             leading=ft.FloatingActionButton(text='Новая задача',icon=ft.icons.ADD, on_click=new_tsp),
                             destinations=[ft.NavigationRailDestination(label_content=ft.Text('Меню',size=16, weight='bold'), icon=ft.Image(src='assets/menu.png', width=30, height=30)),
                                           ft.NavigationRailDestination(label_content=ft.Text('О программе',size=16, weight='bold'), icon=ft.Image(src='assets/info.png', width=30, height=30))],
                             on_change=rail_change)

    btn_style = ft.ButtonStyle(bgcolor='blue', color='white', padding=ft.padding.all(18))
    btn_clear = ft.TextButton(text='Очистить', style=btn_style, on_click=clear_canvas)
    name = ft.TextField(hint_text='Название', on_change=check_next)
    btn_complete = ft.TextButton(text='Готово', style=btn_style, disabled=True, on_click=complete_tsp)
    btn_next = ft.TextButton(text='Далее', style=btn_style, disabled=True, on_click=next)

    saveline = ft.Row([btn_clear, name, btn_next], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    cv = cs.Canvas(content=ft.GestureDetector(on_pan_start=pan_start))

    roads = ft.Column([ft.Text('Генерация дорог (рандом)'),
                        ft.Row([ft.Text('Числа до'), ft.TextField(width=100, on_submit=generate_roads)])],
                        expand=True,
                        visible=False,
                        horizontal_alignment=ft.MainAxisAlignment.CENTER)
    creating = ft.Column([saveline, cv, roads], visible=False, expand=True)

    tsps = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)
    names = [x.split('.')[0] for x in os.listdir('graphs/images')]
    generateListView(names) # генерация списка задач

    search = ft.TextField(hint_text='Поиск', on_change=searching)

    btn_style = ft.ButtonStyle(bgcolor='blue', color='white', padding=ft.padding.all(15))
    preview_line = ft.Row([ft.TextButton('Фото', on_click=image_preview, style=btn_style),
                            ft.TextButton('Дороги', on_click=roads_preview, style=btn_style),
                            ft.TextButton('Решить', on_click=solve, style=btn_style)],
                            alignment=ft.MainAxisAlignment.CENTER)

    roadsList = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)
    preview = ft.Column([preview_line], visible=False,
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        expand=True)
    about = ft.Column([ft.Text('О программе',weight='bold', size=21), ft.Text('Новая задача', size=20, weight='bold'),
                       ft.Text(
'После нажатия на кнопку Новая задача, появится поле, которое содержит следующие элементы:\n\n'
' ‧ Кнопка Очистить, которая очищает пространство от точек\n'
' ‧ Поле для ввода названия новой задачи.\n\n'
<<<<<<< HEAD
'На кнопку Далее можно нажать если вы ввели название и создали как минимум 4 точки.\n'
'Чтобы создать точку нужно просто нажать на пустое пространство, кроме левой панели.\n'
'После нажатия кнопки Далее.\nВведите максимальное число для генерации случайного в поле и обязательно нажать клавишу Enter. \n' 
=======
'На кнопку Готово можно нажать если вы ввели название и создали как минимум 4 точки.\n'
'Чтобы создать точку нужно просто нажать на пустое пространство, кроме левой панели.\n '
'После нажатия кнопки Далее ... Ввести число и обязательно нажать клавишу Enter. \n' 
>>>>>>> 7e185999bb3874abcfe662fb33b3f4e97f40c623
'После этого нажмите на кнопку Готово и перед вами появится изображение итогового графа. \n'
'На этом создание графа закончилось и можно переходить в любое меню.\n',size=18),
ft.Text(
'Вкладка Меню', size=20, weight='bold'), 
ft.Text('Меню содержит два элемента\n'
'   1. поле для поиска\n'
'   2. Список ранее созданных задач\n'
'Чтобы найти задачу, начните вводить начальные буквы имени задачи.', size=18), ft.Text('Автор: Егор Пустобаев', text_align=ft.TextAlign.END)], visible=False) 

    view = ft.Column([search, tsps, preview], expand=True)

    main = ft.Row([rail, preview, view, creating, about],expand=True)


    page.add(main)

ft.app(main)

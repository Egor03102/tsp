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
import sqlite3 as sql

bd = sql.connect('solver.db')
cr = bd.cursor()
cr.execute('''CREATE TABLE IF NOT EXISTS points (
           name TEXT,
           point INTEGER,
           x INTEGER,
           y INTEGER
           )''')

cr.execute('''CREATE TABLE IF NOT EXISTS roads (
           name TEXT,
           one INTEGER,
           two INTEGER,
           dist FLOAT
           )''')
cr.execute('''CREATE TABLE IF NOT EXISTS solutions (
        name TEXT,
        path TEXT
)''')
bd.commit()
bd.close()
if not os.path.exists('assets/images'):
    os.makedirs('assets/images')
if not os.path.exists('assets/solutions'):
    os.makedirs('assets/solutions')


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
        os.remove(f'assets/images/{self.name}.png')
        if os.path.exists(f'assets/solutions/{self.name}.png'):
            os.remove(f'assets/solutions/{self.name}.png')
        bd = sql.connect('solver.db')
        cr = bd.cursor()
        cr.execute('DELETE FROM points WHERE name=?', (self.name,))
        cr.execute('DELETE FROM roads WHERE name=?', (self.name,))
        cr.execute('DELETE FROM solutions WHERE name=?', (self.name,))
        bd.commit()
        bd.close()
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

class NewGraph:
    name: str
    count = 0
    points = []
graph = NewGraph()

def main(page: ft.Page):
    
    page.title = 'Solver TSP'

    def pan_start(e: ft.DragStartEvent): # нажатие на canvas
        graph.count += 1
        graph.points.append((graph.count, int(e.local_x), int(page.height - e.local_y)))

        cv.shapes.append( # рисование круга
            cs.Circle(x=e.local_x, y=e.local_y,radius=5, paint=ft.Paint(stroke_width=3)
            )
        )
        cv.update()
        check_complete(ft.ControlEvent)

    def check_complete(e): # проверка, что можно нажать кнопку Готово
        if graph.count > 3 and name.value:
            btn_complete.disabled = False
        else:
            btn_complete.disabled = True
        page.update()

    def new_tsp(e): # показ canvas, кнопка на левой панели Новая задача
        graph.name = ''
        graph.points = []
        graph.count = 0

        main.controls[2].visible = False
        main.controls[3].visible = True
        main.controls[4].visible = False
        page.update()

    def clear_canvas(e): # очистка canvas, кнопка Очистить
        cv.shapes.clear()
        name.value = ''
        btn_complete.disabled = True

        graph.name = ''
        graph.points = []
        graph.count = 0
        page.update()

    def complete_tsp(e): # кнопка Готово
        graph.name = name.value
        cv.visible = False
        graph_handle.graph_to_db(graph)
        graph_handle.image_graph(graph.name) # генерация графа
        saveline.visible = False
        creating.controls.append(ft.Image(
            src=f"assets/images/{graph.name}.png",
            expand=True,
        ))
        page.update()

        saveline.visible = True
        cv.visible = True
        name.value = ''
        creating.controls.pop(2)
        cv.shapes.clear()
        saveline.controls = [btn_clear, name, btn_complete]


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
            names = [x.split('.')[0] for x in os.listdir('assets/images')]
            generateListView(names)
        elif e.control.selected_index == 1:
            main.controls[2].visible = False
            main.controls[3].visible = False
            main.controls[4].visible = True
        page.update()

    # функции preview
    def image_preview(e): # добавляет фотку при нажатии на кнопку Фото
        if len(preview.controls) == 2:
            preview.controls.pop()
        image1 = ft.Image()
        pil_photo = img.open(f"assets/images/{graph.name}.png")
        arr = asarray(pil_photo)
        pil_img = img.fromarray(arr)
        buff = BytesIO()
        pil_img.save(buff, format="png")

        newstring = en(buff.getvalue()).decode("utf-8")
        image1.src_base64 = newstring
        preview.controls.append(image1)
        page.update()
        image1.update()

    def solve(e):
        tsp = Graph(graph.name)
        path = tsp.solve_aco()
        graph_handle.image_solved_graph(graph.name, path)
        
        if len(preview.controls) == 2:
            preview.controls.pop()
        solved_image = ft.Image()
        pil_photo = img.open(f"assets/solutions/{graph.name}.png")
        arr = asarray(pil_photo)
        pil_img = img.fromarray(arr)
        buff = BytesIO()
        pil_img.save(buff, format="png")

        newstring = en(buff.getvalue()).decode("utf-8")
        solved_image.src_base64 = newstring

        solution = ft.Column([solved_image],
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
    name = ft.TextField(hint_text='Название', on_change=check_complete)
    btn_complete = ft.TextButton(text='Готово', style=btn_style, disabled=True, on_click=complete_tsp)

    saveline = ft.Row([btn_clear, name, btn_complete], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    cv = cs.Canvas(content=ft.GestureDetector(on_pan_start=pan_start))

    creating = ft.Column([saveline, cv], visible=False, expand=True)

    tsps = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)
    names = [x.split('.')[0] for x in os.listdir('assets/images')]
    generateListView(names) # генерация списка задач

    search = ft.TextField(hint_text='Поиск', on_change=searching)

    btn_style = ft.ButtonStyle(bgcolor='blue', color='white', padding=ft.padding.all(15))
    preview_line = ft.Row([ft.TextButton('Фото', on_click=image_preview, style=btn_style),
                            ft.TextButton('Решить', on_click=solve, style=btn_style)],
                            alignment=ft.MainAxisAlignment.CENTER)

    preview = ft.Column([preview_line], visible=False,
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        expand=True,
                                        scroll=ft.ScrollMode.ALWAYS)
    about = ft.Column([ft.Text('О программе',weight='bold', size=21), ft.Text('Новая задача', size=20, weight='bold'),
                       ft.Text(
'После нажатия на кнопку Новая задача, появится поле, которое содержит следующие элементы:\n\n'
' ‧ Кнопка Очистить, которая очищает пространство от точек\n'
' ‧ Поле для ввода названия новой задачи.\n\n'
'На кнопку Готова можно нажать если вы ввели название и создали как минимум 4 точки.\n'
'Чтобы создать точку нужно просто нажать на пустое пространство, кроме левой панели.\n'
'После нажатия кнопки Готово перед вами появится изображение итогового графа. \n'
'На этом создание графа закончилось и можно переходить в любое меню в левой панели.\n',size=18),
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

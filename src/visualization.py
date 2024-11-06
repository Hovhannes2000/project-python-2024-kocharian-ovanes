import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
from automaton import *
import tkinter as tk
from PIL import Image, ImageTk

def automaton_to_transition_matrix(fa):
    # Создаем пустую таблицу с состояниями и алфавитом
    transition_matrix = pd.DataFrame(index=fa.states, columns=fa.alphabet)

    # Заполняем таблицу переходами
    for state in fa.states:
        for symbol in fa.alphabet:
            # Получаем все возможные состояния
            next_states = set()  # Используем set для уникальных значений
            
            # Проверяем все возможные переходы из этого состояния по текущему символу
            for (s, sym), next_states_set in fa.transition_function.items():
                if s == state and sym == symbol:
                    next_states.update(next_states_set)  # Добавляем следующее состояние в множество

            # Преобразуем множество в строку или оставляем "∅", если переходов нет
            transition_matrix.at[state, symbol] = ', '.join(next_states) if next_states else '∅'

    return transition_matrix

fields = [
    "Количество состояний:",
    "Алфавит:",
    "Переходы:\n В таком формате\n{(state,symbol): {states},}",
    "Финальные состояния:"
]

class User_Interface:
    def __init__(self):
        self.nfa = NFA()
        self.elements = []
        self.master = tk.Tk()
        self.master.title("Ввод данных для автомата")

        # Устанавливаем размер окна
        self.master.geometry("2900x1500")

        # Инициализируем строку, в которой мы находимся
        self.row = 0
        
        # Список для хранения введенных значений
        self.entries = []
        self.labels = []  # Список для хранения меток с данными

        # Создаем кнопку для подтверждения ввода
        self.submit_button = tk.Button(self.master, text="Подтвердить", command=self.submit_data)
        self.submit_button.grid(row=self.row + 1, column=2, padx=10, pady=10)

        # Добавляем первое поле ввода
        self.add_input_row()

        self.image_label = tk.Label(self.master)

    def submit_data(self):
        # Получаем введенные данные
        if self.row < len(fields):
            if isinstance(self.entries[self.row], tk.Text):
                value = self.entries[self.row].get("1.0", tk.END).strip()
            else:
                value = self.entries[self.row].get()
                
            self.elements.append(value)
            
            # Создаем метку для отображения введенных значений
            label = tk.Label(self.master, text=f"{fields[self.row]} {value}")
            label.grid(row=self.row, column=3, padx=10, pady=10)
            self.labels.append(label)

            self.entries[self.row].config(state="disabled")

            # Переходим к следующему полю ввода
            if self.row + 1 < len(fields):
                self.row += 1
                self.add_input_row()
            else:
                self.submit_button.config(state="disabled")
                self.build_nfa()

    def add_input_row(self):
        # Добавляем метку и поле ввода для текущего поля
        tk.Label(self.master, text=fields[self.row]).grid(row=self.row, column=0, padx=10, pady=10)

        if fields[self.row] == "Переходы:\n В таком формате\n{(state,symbol): {states},}":  
            # Если это поле "Переходы", используем виджет Text
            entry = tk.Text(self.master, height=5, width=20)

            entry.bind("<Return>", self.add_new_line)  # Привязываем событие нажатия Enter
        else:
            entry = tk.Entry(self.master)

        entry.grid(row=self.row, column=1, padx=10, pady=10)
        self.entries.append(entry)  # Сохраняем ссылку на новое поле ввода

    def add_new_line(self, event):
        # Добавляем новую строку в Text виджет
        text_widget = event.widget
        text_widget.insert(tk.END, "\n")  # Вставляем перенос строки
        return "break"  # Прекращаем обработку события
    def build_nfa(self):
        self.nfa.initial_state = 'q0'
        for index in range(int(self.elements[0])):
            self.nfa.states.append(f'q{index}')
        
        self.nfa.alphabet = self.elements[1].split(',')
        self.nfa.transition_function = eval(self.elements[2])
        self.nfa.final_states = set(self.elements[3].split(','))
        self.nfa_buttons()

    def nfa_buttons(self):
        # Заголовок для столбика кнопок
        tk.Label(self.master, text="Visualising", font=("Arial", 16)).grid(row=0, column=4, padx=10, pady=10)

        # Отступ (пустая строка) для отделения других элементов интерфейса
        tk.Label(self.master, text="").grid(row=1, column=4, padx=10, pady=10)

        # Создаем несколько кнопок и размещаем их в правом столбце
        button_one_letter = tk.Button(self.master, text="Однобуквенные", 
                                    command=lambda: self.nfa.make_transitions_single_letter() 
                                    if not self.nfa.is_single_letters else None)
        button_eps_transition = tk.Button(self.master, text="Без пустых переходов", 
                                        command=lambda: self.nfa.remove_epsilon_transitions() 
                                        if not self.nfa.is_without_epsilon else None)
        button_determinism = tk.Button(self.master, text="Детерминированный", 
                                        command=lambda: self.nfa.nfa_to_dfa() 
                                        if not self.nfa.is_dfa else None)
        button_full_dfa = tk.Button(self.master, text="Полный Детерминированный", 
                                    command=lambda: self.nfa.fulling_dfa() 
                                    if not self.nfa.is_full_dka else None)
        self.button_draw = tk.Button(self.master, text="Нарисовать", command=self.show_image)

        # Располагаем кнопки в вертикальном столбце
        column_number = 4  # Позиция колонны (изменен на 4, чтобы кнопки находились под заголовком)
        button_one_letter.grid(row=3, column=column_number, padx=10, pady=5)
        button_eps_transition.grid(row=4, column=column_number, padx=10, pady=5)
        button_determinism.grid(row=5, column=column_number, padx=10, pady=5)
        button_full_dfa.grid(row=6, column=column_number, padx=10, pady=5)
        self.button_draw.grid(row=7, column=column_number, padx=10, pady=5)

    def draw_automaton(self):
        seed = 0
        random.seed(seed)
        np.random.seed(seed)

        G = nx.MultiDiGraph()  # Используем MultiDiGraph для поддержки множественных рёбер

        # Добавляем состояния в граф
        for state in self.nfa.states:
            G.add_node(state)

        # Добавляем рёбра на основе функции переходов
        for (curr_state, symbol), next_states in self.nfa.transition_function.items():
            for next_state in next_states:
                G.add_edge(curr_state, next_state, label=symbol)

        # Определяем позиции узлов для улучшения визуализации
        pos = nx.spring_layout(G)

        plt.figure(figsize=(12, 6))  # Устанавливаем размер графика
        nx.draw(G, pos, with_labels=False, node_size=3000, node_color='lightblue',
                font_size=12, font_weight='bold', arrows=True)

        # Рисуем узлы и их названия
        for state in G.nodes():
            if state in self.nfa.final_states:
                # Финальное состояние - двойной круг
                nx.draw_networkx_nodes(G, pos, nodelist=[state], node_size=3000,
                                    node_color='lightblue', edgecolors='black', linewidths=2)
                nx.draw_networkx_nodes(G, pos, nodelist=[state], node_size=3300,

                                    node_color='none', edgecolors='black', linewidths=4)
            else:
                # Обычное состояние - один круг
                nx.draw_networkx_nodes(G, pos, nodelist=[state], node_size=3000,
                                    node_color='lightblue', edgecolors='black', linewidths=2)

            # Рисуем название состояния
            nx.draw_networkx_labels(G, pos, labels={state: state}, font_size=12)

        edge_labels = {}  # Словарь для хранения меток рёбер и их смещений

        for (u, v, d) in G.edges(data=True):
            # Положение для метки на основе вершин
            x_u, y_u = pos[u]
            x_v, y_v = pos[v]
            if u == v:
                # Параметры для более заметной петли
                loop_radius = 0.15  # Радиус петли
                angle_offset = np.pi / 2  # Угол смещения
                angle_between_symbols = np.pi / 12
                count = 0
                if (u, v) in edge_labels:
                    # Если рёбер с такими концами уже существует, увеличиваем смещение
                    edge_labels[(u, v)] += offset_distance / 5  # Увеличиваем смещение
                    count += 1
                else:
                    edge_labels[(u, v)] = offset_distance  # Начальное смещение

                # Позиция для метки петли
                x_offset = x_u + loop_radius * np.cos(angle_offset + count * angle_between_symbols)
                y_offset = y_u + loop_radius * np.sin(angle_offset + count * angle_between_symbols)

                offset_distance = 0.15  # Основное смещение

                plt.text(x_offset, y_offset, d['label'], color='red', fontsize=12, ha='center')
                continue  # Пропустить стандартную обработку метки

            # Координаты середины ребра
            midpoint_x = (x_u + x_v) / 2
            midpoint_y = (y_u + y_v) / 2

            # Угол между ребром
            angle = np.arctan2(y_v - y_u, x_v - x_u)

            # Смещение вдоль ребра
            offset_distance = 0.2  # Основное смещение
            if (u, v) in edge_labels:
                # Если рёбер с такими концами уже существует, увеличиваем смещение
                edge_labels[(u, v)] += offset_distance / 5  # Увеличиваем смещение
            else:
                edge_labels[(u, v)] = offset_distance  # Начальное смещение

            # Получаем текущее смещение для метки
            current_offset = edge_labels[(u, v)]

            # Смещение метки вдоль ребра
            x_offset = midpoint_x + current_offset * np.cos(angle)
            y_offset = midpoint_y + current_offset * np.sin(angle)

            offset_distance = 0.05
            x_offset += offset_distance * np.cos(angle + np.pi / 2)
            y_offset += offset_distance * np.sin(angle + np.pi / 2)

            plt.text(x_offset, y_offset, d['label'], color='red', fontsize=12, ha='center')

        # Отображаем граф
        plt.title("Конечный автомат")
        plt.axis('off')
        self.nfa_path = 'automaton.png'
        plt.savefig(self.nfa_path)
        plt.close()
    
    def show_image(self):
        self.draw_automaton()

        image_path = self.nfa_path  # Укажите путь к изображению
        self.image_label.grid()
        # Удаляем старое изображение, если оно есть
        if hasattr(self.image_label, 'image'):
            self.image_label.config(image=None)  # Убираем текущее изображение
            self.image_label.image = None  # Очищаем ссылку на изображение

        # Загружаем новое изображение
        image = Image.open(image_path)

        # Конвертируем изображение в формат, который Tkinter может использовать
        tk_image = ImageTk.PhotoImage(image)

        # Устанавливаем новое изображение на метку
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image  # Сохраняем ссылку на новое изображение
        if self.nfa.is_full_dka:
            self.button_draw.config(state="disabled")
            return

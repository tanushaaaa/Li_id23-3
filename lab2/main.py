import tkinter as tk  # основная библиотека для работы с графическим интерфейсом
import json  # используются в качестве файлов для обмена данными
import time  # для работы с текущим временем и контроля над анимацией
import math  # для математических операций (таких как синус, пи)
import os  # предоставляет функции для взаимодействия с операционной системой

# Параметры окна
WINDOW_WIDTH = 800  # ширина
WINDOW_HEIGHT = 600  # высота

# Начальные параметры волн и поплавков
# amplitude - амплитуда волны, которая определяет её высоту (в пикселях)
# wavelenth - длина волны, определяющая расстояние между соседними гребнями волны
# period - период волны, определяющий её скорость (чем меньше период, тем быстрее волна движется)
# x - начальная координата поплавка по оси x
# mass - масса поплавка
# volume - объём поплавка
default_config = {
    "waves": [
        {"amplitude": 50, "wavelength": 200, "period": 2},
        {"amplitude": 30, "wavelength": 150, "period": 1.5},
        {"amplitude": 20, "wavelength": 250, "period": 2.5}
    ],
    "buoys": [
        {"x": 100, "mass": 1, "volume": 1},
        {"x": 400, "mass": 1.5, "volume": 1.2},
        {"x": 600, "mass": 1.2, "volume": 1.0}
    ]
}

config_file = 'config.json'

# Проверка наличия файла конфигурации
if not os.path.exists(config_file):  # проверить, существует ли файл config.json в файловой системе
    # Если файл конфигурации не найден, он будет создан
    with open(config_file, 'w') as f:  # Метод open() открывает указанный файл в режиме записи ('w')
        json.dump(default_config, f)  # записать содержимое переменной default_config в файл config.json в формате JSON

# Чтение конфигурации
with open(config_file, 'r') as f:  # Этот фрагмент кода открывает файл config.json в режиме чтения ('r')
    config = json.load(
        f)  # Если файл существует, то данные загружаются с помощью json.load(), который преобразует данные из формата JSON обратно в структуру данных Python

# Константы
g = 9.81  # Ускорение свободного падения
rho_water = 1000  # Плотность воды

# Создание основного окна
root = tk.Tk()  # создаёт главное окно
root.title("Волны")  # задаёт заголовок окна
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                   bg='white')  # создаёт холст, на котором мы будем рисовать волны и поплавки. Мы задаём его размер и цвет фона
canvas.pack()  # размещает холст в главном окне


# Функция для вычисления высоты волны
# x - горизонтальная координата точки
# t - текущее время
# amplitude - амплитуда волны
# wavelength - длина волны
# period - период волны
def wave_height(x, t, amplitude, wavelength, period):
    k = 2 * math.pi / wavelength  # волновое число
    omega = 2 * math.pi / period  # круговая частота
    return amplitude * math.sin(k * x - omega * t)  # Формула вычисляет синусоиду, представляющую форму волны


# Создание графических объектов волн и поплавков
wave_params = config["waves"]  # проходимся по параметрам waves в файле config
wave_objects = []  # создаем пустой список
for wave in wave_params:
    line = canvas.create_line(0, 0, WINDOW_WIDTH, 0, fill='purple', width=2)  # помещаем в список каждую линию
    wave_objects.append(line)

# Поплавки — создаем круги
bobber_params = config["buoys"]
bobber_objects = []
for bobber in bobber_params:
    x = bobber["x"]
    # canvas.create_oval - каждый поплавок представлен кругом
    # Мы задаём координаты верхней левой и нижней правой точки овала, чтобы создать круг диаметром 20 пикселей
    bobber_obj = canvas.create_oval(x - 10, WINDOW_HEIGHT // 2 - 10, x + 10, WINDOW_HEIGHT // 2 + 10, fill='pink')
    bobber_objects.append(bobber_obj)


# Вычисляем силу Архимеда
# F_arch = rho_water * g * V_submerged
# rho_water - плотность воды
# g - ускорение свободного падения
# volume_bobber - общий объем поплавка в кубических метрах
# density_bobber - плотность поплавка
def archimedes_force(rho_water, g, volume_bobber, density_bobber):
    # Если плотность поплавка меньше плотности воды
    if density_bobber < rho_water:
        # Значит поплавок легче воды, и часть его объема будет погружена.
        V_submerged = volume_bobber * (density_bobber / rho_water)
    else:
        # Больше или равна плотности воды, поплавок будет полностью погружен
        V_submerged = volume_bobber
    return rho_water * g * V_submerged


# Анимация
def animate():
    current_time = time.time()  # получаем текущее время

    # Обновляем волны
    for i, wave in enumerate(wave_params):
        points = []
        for x in range(0, WINDOW_WIDTH, 10):  # шаг по x для волны
            y = wave_height(x, current_time, wave["amplitude"], wave["wavelength"], wave["period"])
            points.append(x)
            points.append(WINDOW_HEIGHT // 2 + y)
        canvas.coords(wave_objects[i], *points)  # обновляем координаты волны

    # Обновляем поплавки
    for i, bobber in enumerate(bobber_params):
        x = bobber["x"]
        wave = wave_params[i % len(wave_params)]
        y_wave = wave_height(x, current_time, wave["amplitude"], wave["wavelength"], wave["period"])

        # Рассчитываем плотность поплавка
        density_bobber = bobber["mass"] / bobber["volume"]

        # Вычисляем силу Архимеда
        F_arch = archimedes_force(rho_water, g, bobber["volume"], density_bobber)
        offset = F_arch / (bobber["mass"] * g) * 10  # Чем больше сила Архимеда, тем выше поплавок

        # Определяем смещение поплавка
        if y_wave > 0:  # Если волна поднимается
            y_bobber = WINDOW_HEIGHT // 2 + y_wave + offset  # Поплавок выше волны
        else:  # Если волна опускается
            y_bobber = WINDOW_HEIGHT // 2 + y_wave - offset  # Поплавок ниже волны

        # Обновляем положение круга
        canvas.coords(bobber_objects[i], x - 10, y_bobber - 10, x + 10, y_bobber + 10)

    # Перезапуск анимации через 20 мс
    root.after(20, animate)


# Запуск анимации
animate()

# Запуск основного цикла программы
root.mainloop()
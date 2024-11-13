import tkinter as tk  # библиотека Python для создания графического интерфейса
import math  # библиотека, которая предоставляет математические функции

# Создаем основное окно
root = tk.Tk()
root.title("Точка, движущаяся по окружности")

# Размеры окна
WIDTH, HEIGHT = 600, 600

# Создаем область для рисования
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()  # размещает этот холст внутри окна

# Параметры окружности
circle_center = (
WIDTH // 2, HEIGHT // 2)  # определяет координаты центра окружности, которая будет находиться в середине окна
circle_radius = 200  # задаёт радиус окружности

# Рисуем окружность
canvas.create_oval(circle_center[0] - circle_radius, circle_center[1] - circle_radius,
                   circle_center[0] + circle_radius, circle_center[1] + circle_radius, outline="black")

# Параметры движения точки
angle = 0  # начальный угол
speed = 0.01  # скорость (можно менять для управления скоростью и направлением)

# Создаем точку на окружности
point_radius = 5  # радиус красной точки
point = canvas.create_oval(circle_center[0] - point_radius, circle_center[1] - point_radius,
                           circle_center[0] + point_radius, circle_center[1] + point_radius, fill="red")  # создаёт круг


# Функция для обновления положения точки
def move_point():
    global angle
    # Вычисляем новые координаты точки
    x = circle_center[0] + circle_radius * math.cos(angle)
    y = circle_center[1] + circle_radius * math.sin(angle)

    # Обновляем положение точки
    canvas.coords(point, x - point_radius, y - point_radius, x + point_radius, y + point_radius)

    # Обновляем угол
    angle += speed

    # Рекурсивно вызываем функцию через определенный интервал времени
    root.after(16, move_point)  # примерно 60 FPS


# Запускаем движение точки
move_point()


# Изменение скоростью через клавиши
def increase_speed(event):  # увеличивает скорость на 0.005, что ускоряет движение точки по часовой стрелке
    global speed
    speed += 0.005


def decrease_speed(
        event):  # уменьшает скорость на 0.005. Если значение скорости становится отрицательным, точка начинает двигаться против часовой стрелки
    global speed
    speed -= 0.005


# Привязка клавиш к изменению скорости
root.bind("<Up>", increase_speed)  # Увеличить скорость
root.bind("<Down>", decrease_speed)  # Уменьшить скорость

# Запуск основного цикла
root.mainloop()
import sys # предоставляет доступ к параметрам и функциям системы
import math # который содержит математические функции, такие как вычисление синуса, косинуса, числа π и другие
from PyQt5.QtCore import Qt, QTimer, QRect # Импортируются классы и константы из модуля QtCore, который отвечает за базовые компоненты PyQt5
from PyQt5.QtGui import QPainter, QColor, QPen # Импортируются классы из модуля QtGui, связанного с графикой и визуализацией
from PyQt5.QtWidgets import ( #Импортируются элементы интерфейса из модуля QtWidgets
    QApplication, QWidget, QSlider, QLabel, QDialog, QFormLayout,
    QHBoxLayout, QVBoxLayout, QPushButton, QSpinBox
)


class WaveSimulation(QWidget): # Этот класс будет представлять основное окно приложения
    def __init__(self):
        super().__init__() # вызывает конструктор родительского класса (QWidget), чтобы правильно инициализировать базовый функционал виджета.
        self.setWindowTitle("Волны и поплавки") # Устанавливается заголовок окна
        self.setGeometry(100, 100, 800, 600) # Устанавливаются начальные координаты и размер окна

        # Загрузка данных
        self.num_waves = 3 # Задает количество волн
        self.wave_params = [{"amplitude": 50, "period": 100, "speed": 0.5} for _ in range(self.num_waves)] # Создается список параметров для каждой волны
        self.poplavok_params = [{"mass": 20, "objem": 15} for _ in range(self.num_waves)] # Создается список параметров для каждого поплавка
        self.poplavok_radius = 15 # радиус поплавков
        self.poplavok_speed = 1.0  # Начальная скорость поплавков
        self.time = 0 # Переменная для отслеживания времени, используется для анимации. Значение увеличивается с каждым шагом.
        self.g = 9.81 # Ускорение свободного падения
        self.offset_scale = 5 # Масштабный коэффициент для расчета вертикального смещения поплавков
        self.clicked_poplavok = None  # Хранение индекса нажатого поплавка
        self.calculate_poplavok_positions() # рассчитывает вертикальное положение (по оси Y) каждой волны и поплавка

        # Таймер для анимации
        self.timer = QTimer(self) # будет управлять циклическим обновлением интерфейса
        self.timer.timeout.connect(self.animate) # Связывается сигнал timeout (истекает через определенные промежутки времени) с методом animate, который отвечает за обновление анимации.
        self.timer.start(30) # обеспечивает плавную анимацию волн и поплавков

        # Интерфейс
        self.init_ui() # который создает элементы интерфейса, такие как слайдеры, кнопки и метки

    def calculate_poplavok_positions(self): # метод рассчитывает вертикальные позиции (по оси Y) для всех поплавков
        self.poplavok_positions = [
            self.height() // (self.num_waves + 1) * (i + 1) for i in range(self.num_waves)
        ]

    def init_ui(self):
        self.amplitude_slider = QSlider(Qt.Horizontal, self) # Создается слайдер (ползунок) для изменения амплитуды вол
        self.amplitude_slider.setRange(10, 200) # диапазон значений слайдера от 10 до 200
        self.amplitude_slider.setValue(50) # начальное значение слайдера (50)
        self.amplitude_slider.setGeometry(10, 550, 200, 30) # положение и размеры слайдера
        self.amplitude_slider.valueChanged.connect(self.update_wave_parameters) # обновляет параметры волн на основе нового значения амплитуды

        # Аналогичен слайдеру амплитуды, но предназначен для изменения периода волн
        self.period_slider = QSlider(Qt.Horizontal, self)
        self.period_slider.setRange(10, 200)
        self.period_slider.setValue(100)
        self.period_slider.setGeometry(10, 590, 200, 30)
        self.period_slider.valueChanged.connect(self.update_wave_parameters)

        # Слайдер для изменения скорости движения поплавков
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(10)
        self.speed_slider.setGeometry(300, 550, 200, 30)
        self.speed_slider.valueChanged.connect(self.update_poplavok_speed)

        # Создается метка для отображения текущей амплитуды, получаемой из значения слайдера
        self.amplitude_label = QLabel(f"Амплитуда: {self.amplitude_slider.value()}", self)
        self.amplitude_label.setGeometry(220, 550, 200, 30) # координаты и размеры

        # Аналогично, метка для отображения текущего периода
        self.period_label = QLabel(f"Период: {self.period_slider.value()}", self)
        self.period_label.setGeometry(220, 590, 200, 30)

        # для отображения текущей скорости поплавков
        self.speed_label = QLabel(f"Скорость: {self.poplavok_speed}", self)
        self.speed_label.setGeometry(520, 550, 200, 30)

        # Кнопки добавления волн
        self.add_wave_button = QPushButton("Добавить волну", self) # Создается кнопка с текстом "Добавить волну"
        self.add_wave_button.setGeometry(580, 550, 200, 30) # Устанавливаются координаты и размеры кнопки
        self.add_wave_button.clicked.connect(self.add_wave) # добавляет новую волну и соответствующий поплавок

        # Аналогично с кнопкой удаления волн
        self.remove_wave_button = QPushButton("Удалить волну", self)
        self.remove_wave_button.setGeometry(580, 590, 200, 30)
        self.remove_wave_button.clicked.connect(self.remove_wave)

    def paintEvent(self, event):
        painter = QPainter(self) # предоставляет методы для рисования фигур, линий, текста и т.д.
        painter.begin(self) # Подготовка QPainter для рисования в текущем виджете (self)

        # Рисуем фон
        painter.setBrush(QColor(135, 206, 250)) # цвет кисти для закрашивания объектов
        painter.drawRect(self.rect()) # Рисуется прямоугольник, который заполняет всю область окна

        # Рисуем волны и поплавки
        for i, wave in enumerate(self.wave_params): # Перебираются параметры всех волн, сохраненные в списке self.wave_params
            amplitude, period, speed = wave["amplitude"], wave["period"], wave["speed"] # Из словаря wave извлекаются параметры
            mass, objem = self.poplavok_params[i]["mass"], self.poplavok_params[i]["objem"] # Из списка self.poplavok_params (параметры поплавков) для текущего индекса i извлекаются масса и объем
            wave_y = self.poplavok_positions[i] # Из списка self.poplavok_positions извлекается вертикальная позиция (ось Y) текущей волны/поплавка

            self.draw_wave(painter, wave_y, amplitude, period, speed) # рисование волны
            poplavok_x = (self.time * self.poplavok_speed * 5) % self.width() # Вычисление положения поплавка по X
            self.draw_poplavok(painter, wave_y, amplitude, period, speed, poplavok_x, mass, objem, i) # Отрисовка поплавка

        painter.end() # Завершение работы с QPainter

    # метод отвечает за отрисовку волны
    def draw_wave(self, painter, wave_y, amplitude, period, speed):
        pen = QPen(QColor(255, 0, 0)) # Создается объект QPen, который определяет, как будет рисоваться линия волны.
        pen.setWidth(2) # толщина линии
        painter.setPen(pen) # Переданный объект painter (графический инструмент для рисования) настроен на использование созданной кисти pen

        for x in range(self.width()): # Цикл перебирает все горизонтальные координаты x в пределах ширины окна.
            # Для каждой горизонтальной координаты x вычисляется вертикальная координата y с учетом волновой функции
            y = wave_y + amplitude * math.sin(2 * math.pi * (x / period) - speed * self.time)
            painter.drawPoint(x, int(y)) # Для каждой координаты x рисуется точка на уровне y

    # метод отвечает за отрисовку поплавка, который движется вдоль волны
    def draw_poplavok(self, painter, wave_y, amplitude, period, speed, poplavok_x, mass, objem, index):
        wave_height = wave_y + amplitude * math.sin(2 * math.pi * (poplavok_x / period) - speed * self.time) # Вычисление высоты волны в точке расположения поплавка
        offset = ((mass - objem) * self.g / (mass + objem)) * self.offset_scale # Вычисление смещения поплавка относительно волны
        poplavok_y = wave_height + offset # Финальная вертикальная позиция поплавка получается как сумма высоты волны и смещения.

        painter.setBrush(QColor(0, 0, 255)) # задает синий цвет для поплавка
        #Рисование поплавка как круга
        painter.drawEllipse(
            int(poplavok_x - self.poplavok_radius), # начальная горизонтальная координата круга
            int(poplavok_y - self.poplavok_radius), # начальная вертикальная координата круга
            self.poplavok_radius * 2, # диаметр круга (по горизонтали и вертикали)
            self.poplavok_radius * 2,
        )

    # метод обрабатывает событие нажатия мыши (клика) и проверяет, попал ли пользователь в область поплавка
    def mousePressEvent(self, event):
        for i, wave_y in enumerate(self.poplavok_positions): # Цикл перебирает все поплавки
            poplavok_x = (self.time * self.poplavok_speed * 5) % self.width() # Вычисление горизонтальной позиции поплавка
            wave_height = wave_y + self.wave_params[i]["amplitude"] * math.sin(
                2 * math.pi * (poplavok_x / self.wave_params[i]["period"]) - self.wave_params[i]["speed"] * self.time
            ) # Вычисление высоты волны под поплавком
            offset = ((self.poplavok_params[i]["mass"] - self.poplavok_params[i]["objem"]) * self.g /
                      (self.poplavok_params[i]["mass"] + self.poplavok_params[i]["objem"])) * self.offset_scale # Вычисление смещения поплавка (с учетом силы Архимеда)
            poplavok_y = wave_height + offset # Финальная вертикальная позиция поплавка — сумма высоты волны и смещения.

            # Создание прямоугольной области поплавка
            rect = QRect(
                int(poplavok_x - self.poplavok_radius), # левый верхний угол по X
                int(poplavok_y - self.poplavok_radius), # левый верхний угол по Y
                self.poplavok_radius * 2, # ширина и высота области равны диаметру поплавка
                self.poplavok_radius * 2,
            )

            # Проверка попадания клика в поплавок
            if rect.contains(event.pos()):
                self.clicked_poplavok = i # Если клик попал в поплавок, его индекс i сохраняется в переменной
                self.open_float_dialog(i) # открывает диалог для изменения параметров поплавка с индексом
                break # После нахождения поплавка, на который кликнули, цикл прерывается

    # Открывает модальное диалоговое окно для работы с поплавком
    def open_float_dialog(self, index):
        dialog = FloatDialog(index, self) # Создаёт объект диалогового окна, в котором, возможно, настраиваются параметры поплавка
        dialog.exec_() # Запускает диалоговое окно и блокирует взаимодействие с основным окном до закрытия диалога

    # Обновляет параметры волн (амплитуда и период) и отображает их в интерфейс
    def update_wave_parameters(self):
        for wave in self.wave_params: # Перебирает все параметры волн, хранящиеся в списке self.wave_params
            wave["amplitude"] = self.amplitude_slider.value() # Устанавливает амплитуду текущей волны, беря значение из ползунка
            wave["period"] = self.period_slider.value() # Устанавливает период

        self.amplitude_label.setText(f"Амплитуда: {self.amplitude_slider.value()}") # Отображает текущую амплитуду на метке
        self.period_label.setText(f"Период: {self.period_slider.value()}") # Отображает текущий период

    # Обновляет скорость поплавка, основываясь на значении слайдера скорости
    def update_poplavok_speed(self):
        self.poplavok_speed = self.speed_slider.value() / 10.0 # Сохраняет значение скорости поплавка
        self.speed_label.setText(f"Скорость: {self.poplavok_speed}") # Отображает обновлённую скорость на метке

    # Анимация, обновляющая состояние интерфейса
    def animate(self):
        self.time += 0.05 # Увеличивает внутренний счётчик времени
        self.update() # Перерисовывает интерфейс (например, графику или состояние объектов)

    # Добавляет новую волну и связанный с ней поплавок
    def add_wave(self):
        self.num_waves += 1 # Увеличивает счётчик количества волн
        self.wave_params.append({"amplitude": 50, "period": 100, "speed": 0.5}) # Добавляет параметры новой волны
        self.poplavok_params.append({"mass": 20, "objem": 15}) # Добавляет параметры нового поплавка
        self.calculate_poplavok_positions() # Пересчитывает положения всех поплавков, исходя из параметров волн
        self.update() # Перерисовывает интерфей

    # Удаляет последнюю волну и соответствующий поплавок
    def remove_wave(self):
        if self.num_waves > 1: # Проверяет, что в системе больше одной волны (нельзя удалить последнюю)
            self.num_waves -= 1 # Уменьшает счётчик волн
            self.wave_params.pop() # Удаляет параметры последней волны из списка
            self.poplavok_params.pop() # Удаляет параметры последнего поплавка
            self.calculate_poplavok_positions() # Пересчитывает положения оставшихся поплавков
            self.update() # Перерисовывает интерфейс

# Создает диалоговое окно
class FloatDialog(QDialog):
    def __init__(self, index, parent=None):
        super().__init__(parent) # Инициализация базового класса QDialog с передачей родительского объекта
        self.index = index # Сохраняет индекс поплавка в атрибуте объекта
        self.parent = parent # Сохраняет ссылку на родительский объект для взаимодействия с ним

        self.setWindowTitle("Настройка поплавка") # заголовок окна диалога
        layout = QFormLayout() # Создает макет. Он автоматически организует элементы в формате "метка-значение"

        # SpinBox для настройки массы
        self.mass_spinbox = QSpinBox() # Создаёт числовой ввод (SpinBox) для выбора массы поплавка
        self.mass_spinbox.setValue(self.parent.poplavok_params[index]["mass"]) # Устанавливает текущее значение SpinBox, беря массу поплавка из parent.poplavok_params по индексу
        self.mass_spinbox.setRange(1, 100) # Задаёт диапазон допустимых значений для массы от 1 до 100
        layout.addRow("Масса:", self.mass_spinbox) # Добавляет в макет новую строку: метка "Масса:" и SpinBox для изменения значения

        # SpinBox для настройки объёма (аналагично с Spinbox для настройки массы)
        self.objem_spinbox = QSpinBox()
        self.objem_spinbox.setValue(self.parent.poplavok_params[index]["objem"])
        self.objem_spinbox.setRange(1, 100)
        layout.addRow("Объем:", self.objem_spinbox)

        # Кнопки "Сохранить" и "Отмена"
        button_layout = QHBoxLayout() # Создаёт горизонтальный макет для размещения кнопок в одной строке
        save_button = QPushButton("Сохранить") # Создаёт кнопку с надписью "Сохранить"
        save_button.clicked.connect(self.save_and_close) # Подключает сигнал нажатия кнопки к методу save_and_close
        button_layout.addWidget(save_button) # Добавляет кнопку в горизонтальный макет

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close) # Подключает сигнал нажатия к методу self.close, который просто закрывает диалог без сохранения изменений
        button_layout.addWidget(cancel_button)

        layout.addRow(button_layout) # Добавляет строку в основной макет, содержащую обе кнопки
        self.setLayout(layout) # Устанавливает основной макет (с полями для массы, объёма и кнопками) для диалогового окна

    # Сохраняет изменения в параметрах поплавка и закрывает окно
    def save_and_close(self):
        self.parent.poplavok_params[self.index]["mass"] = self.mass_spinbox.value() # Сохраняет новое значение массы из SpinBox в параметры поплавка родительского объекта
        self.parent.poplavok_params[self.index]["objem"] = self.objem_spinbox.value() # Сохраняет новое значение объёма из SpinBox в параметры поплавка
        self.close() # Закрывает диалоговое окно


if __name__ == "__main__": # Проверяет, запускается ли этот скрипт напрямую, или он импортирован как модуль
    app = QApplication(sys.argv) # Создаёт объект QApplication, который должен существовать до создания окон и виджетов
    window = WaveSimulation() # Сохраняет ссылку на это окно в переменной window
    window.show() # Отображает главное окно приложения на экране
    sys.exit(app.exec_()) # Код завершения используется операционной системой для определения успешности или неуспешности завершения приложения

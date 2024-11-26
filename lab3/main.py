import sys
import math
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSlider, QLabel, QDialog, QFormLayout,
    QHBoxLayout, QVBoxLayout, QPushButton, QSpinBox
)


class WaveSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Волны и поплавки")
        self.setGeometry(100, 100, 800, 600)

        # Загрузка данных
        self.num_waves = 3
        self.wave_params = [{"amplitude": 50, "period": 100, "speed": 0.5} for _ in range(self.num_waves)]
        self.poplavok_params = [{"mass": 20, "objem": 15} for _ in range(self.num_waves)]
        self.poplavok_radius = 15
        self.poplavok_speed = 1.0  # Начальная скорость поплавков
        self.time = 0
        self.g = 9.81
        self.offset_scale = 5
        self.clicked_poplavok = None  # Хранение индекса нажатого поплавка
        self.calculate_poplavok_positions()

        # Таймер для анимации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

        # Интерфейс
        self.init_ui()

    def calculate_poplavok_positions(self):
        self.poplavok_positions = [
            self.height() // (self.num_waves + 1) * (i + 1) for i in range(self.num_waves)
        ]

    def init_ui(self):
        self.amplitude_slider = QSlider(Qt.Horizontal, self)
        self.amplitude_slider.setRange(10, 200)
        self.amplitude_slider.setValue(50)
        self.amplitude_slider.setGeometry(10, 550, 200, 30)
        self.amplitude_slider.valueChanged.connect(self.update_wave_parameters)

        self.period_slider = QSlider(Qt.Horizontal, self)
        self.period_slider.setRange(10, 200)
        self.period_slider.setValue(100)
        self.period_slider.setGeometry(10, 590, 200, 30)
        self.period_slider.valueChanged.connect(self.update_wave_parameters)

        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(10)
        self.speed_slider.setGeometry(300, 550, 200, 30)
        self.speed_slider.valueChanged.connect(self.update_poplavok_speed)

        self.amplitude_label = QLabel(f"Амплитуда: {self.amplitude_slider.value()}", self)
        self.amplitude_label.setGeometry(220, 550, 200, 30)

        self.period_label = QLabel(f"Период: {self.period_slider.value()}", self)
        self.period_label.setGeometry(220, 590, 200, 30)

        self.speed_label = QLabel(f"Скорость: {self.poplavok_speed}", self)
        self.speed_label.setGeometry(520, 550, 200, 30)

        # Кнопки добавления и удаления волн
        self.add_wave_button = QPushButton("Добавить волну", self)
        self.add_wave_button.setGeometry(580, 550, 200, 30)
        self.add_wave_button.clicked.connect(self.add_wave)

        self.remove_wave_button = QPushButton("Удалить волну", self)
        self.remove_wave_button.setGeometry(580, 590, 200, 30)
        self.remove_wave_button.clicked.connect(self.remove_wave)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.begin(self)

        # Рисуем фон
        painter.setBrush(QColor(135, 206, 250))
        painter.drawRect(self.rect())

        # Рисуем волны и поплавки
        for i, wave in enumerate(self.wave_params):
            amplitude, period, speed = wave["amplitude"], wave["period"], wave["speed"]
            mass, objem = self.poplavok_params[i]["mass"], self.poplavok_params[i]["objem"]
            wave_y = self.poplavok_positions[i]

            self.draw_wave(painter, wave_y, amplitude, period, speed)
            poplavok_x = (self.time * self.poplavok_speed * 5) % self.width()
            self.draw_poplavok(painter, wave_y, amplitude, period, speed, poplavok_x, mass, objem, i)

        painter.end()

    def draw_wave(self, painter, wave_y, amplitude, period, speed):
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)

        for x in range(self.width()):
            y = wave_y + amplitude * math.sin(2 * math.pi * (x / period) - speed * self.time)
            painter.drawPoint(x, int(y))

    def draw_poplavok(self, painter, wave_y, amplitude, period, speed, poplavok_x, mass, objem, index):
        wave_height = wave_y + amplitude * math.sin(2 * math.pi * (poplavok_x / period) - speed * self.time)
        offset = ((mass - objem) * self.g / (mass + objem)) * self.offset_scale
        poplavok_y = wave_height + offset

        painter.setBrush(QColor(0, 0, 255))
        painter.drawEllipse(
            int(poplavok_x - self.poplavok_radius),
            int(poplavok_y - self.poplavok_radius),
            self.poplavok_radius * 2,
            self.poplavok_radius * 2,
        )

    def mousePressEvent(self, event):
        # Проверка попадания клика на поплавок
        for i, wave_y in enumerate(self.poplavok_positions):
            poplavok_x = (self.time * self.poplavok_speed * 5) % self.width()
            wave_height = wave_y + self.wave_params[i]["amplitude"] * math.sin(
                2 * math.pi * (poplavok_x / self.wave_params[i]["period"]) - self.wave_params[i]["speed"] * self.time
            )
            offset = ((self.poplavok_params[i]["mass"] - self.poplavok_params[i]["objem"]) * self.g /
                      (self.poplavok_params[i]["mass"] + self.poplavok_params[i]["objem"])) * self.offset_scale
            poplavok_y = wave_height + offset

            rect = QRect(
                int(poplavok_x - self.poplavok_radius),
                int(poplavok_y - self.poplavok_radius),
                self.poplavok_radius * 2,
                self.poplavok_radius * 2,
            )

            if rect.contains(event.pos()):
                self.clicked_poplavok = i
                self.open_float_dialog(i)
                break

    def open_float_dialog(self, index):
        dialog = FloatDialog(index, self)
        dialog.exec_()

    def update_wave_parameters(self):
        for wave in self.wave_params:
            wave["amplitude"] = self.amplitude_slider.value()
            wave["period"] = self.period_slider.value()

        self.amplitude_label.setText(f"Амплитуда: {self.amplitude_slider.value()}")
        self.period_label.setText(f"Период: {self.period_slider.value()}")

    def update_poplavok_speed(self):
        self.poplavok_speed = self.speed_slider.value() / 10.0
        self.speed_label.setText(f"Скорость: {self.poplavok_speed}")

    def animate(self):
        self.time += 0.05
        self.update()

    def add_wave(self):
        self.num_waves += 1
        self.wave_params.append({"amplitude": 50, "period": 100, "speed": 0.5})
        self.poplavok_params.append({"mass": 20, "objem": 15})
        self.calculate_poplavok_positions()
        self.update()

    def remove_wave(self):
        if self.num_waves > 1:
            self.num_waves -= 1
            self.wave_params.pop()
            self.poplavok_params.pop()
            self.calculate_poplavok_positions()
            self.update()


class FloatDialog(QDialog):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.parent = parent

        self.setWindowTitle("Настройка поплавка")
        layout = QFormLayout()

        self.mass_spinbox = QSpinBox()
        self.mass_spinbox.setValue(self.parent.poplavok_params[index]["mass"])
        self.mass_spinbox.setRange(1, 100)
        layout.addRow("Масса:", self.mass_spinbox)

        self.objem_spinbox = QSpinBox()
        self.objem_spinbox.setValue(self.parent.poplavok_params[index]["objem"])
        self.objem_spinbox.setRange(1, 100)
        layout.addRow("Объем:", self.objem_spinbox)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_and_close)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def save_and_close(self):
        self.parent.poplavok_params[self.index]["mass"] = self.mass_spinbox.value()
        self.parent.poplavok_params[self.index]["objem"] = self.objem_spinbox.value()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WaveSimulation()
    window.show()
    sys.exit(app.exec_())

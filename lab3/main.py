import sys
import math
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QDialog, QSpinBox, QComboBox
)


class PoplavokSettingsDialog(QDialog):
    def __init__(self, poplavok_params, index, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Настройки поплавка {index + 1}")

        self.layout = QVBoxLayout(self)
        self.mass_label = QLabel("Масса:", self)
        self.layout.addWidget(self.mass_label)

        self.mass_spinbox = QSpinBox(self)
        self.mass_spinbox.setRange(1, 100)
        self.mass_spinbox.setValue(poplavok_params["mass"])
        self.layout.addWidget(self.mass_spinbox)

        self.volume_label = QLabel("Объем:", self)
        self.layout.addWidget(self.volume_label)

        self.volume_spinbox = QSpinBox(self)
        self.volume_spinbox.setRange(1, 100)
        self.volume_spinbox.setValue(poplavok_params["objem"])
        self.layout.addWidget(self.volume_spinbox)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.poplavok_params = poplavok_params

    def save_changes(self):
        self.poplavok_params["mass"] = self.mass_spinbox.value()
        self.poplavok_params["objem"] = self.volume_spinbox.value()
        self.accept()


class WaveSettingsDialog(QDialog):
    def __init__(self, wave_params, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки волн")
        self.wave_params = wave_params

        self.setLayout(QVBoxLayout())

        for i, wave in enumerate(self.wave_params):
            wave_frame = QVBoxLayout()

            amplitude_slider = self.create_slider(10, 200, wave["amplitude"])
            amplitude_slider.valueChanged.connect(
                lambda value, idx=i: self.update_wave_param(idx, "amplitude", value)
            )
            wave_frame.addWidget(QLabel(f"Волна {i + 1} Амплитуда:"))
            wave_frame.addWidget(amplitude_slider)

            period_slider = self.create_slider(10, 200, wave["period"])
            period_slider.valueChanged.connect(
                lambda value, idx=i: self.update_wave_param(idx, "period", value)
            )
            wave_frame.addWidget(QLabel(f"Волна {i + 1} Период:"))
            wave_frame.addWidget(period_slider)

            speed_slider = self.create_slider(1, 100, int(wave["speed"] * 10))
            speed_slider.valueChanged.connect(
                lambda value, idx=i: self.update_wave_param(idx, "speed", value / 10)
            )
            wave_frame.addWidget(QLabel(f"Волна {i + 1} Скорость:"))
            wave_frame.addWidget(speed_slider)

            self.layout().addLayout(wave_frame)

    def create_slider(self, min_val, max_val, initial_value):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(initial_value)
        return slider

    def update_wave_param(self, index, param, value):
        self.wave_params[index][param] = value


class WaveSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Волны и поплавки")
        self.setGeometry(100, 100, 800, 600)

        self.num_waves = 3
        self.wave_params = [{"amplitude": 50, "period": 100, "speed": 0.5} for _ in range(self.num_waves)]
        self.poplavok_params = [{"mass": 20, "objem": 15} for _ in range(self.num_waves)]
        self.poplavok_radius = 15
        self.time = 0
        self.g = 9.81
        self.offset_scale = 5
        self.calculate_poplavok_positions()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

        self.init_ui()

    def calculate_poplavok_positions(self):
        self.poplavok_positions = [
            self.height() // (self.num_waves + 1) * (i + 1) for i in range(self.num_waves)
        ]

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        button_layout = QHBoxLayout()
        wave_settings_button = QPushButton("Изменение волн", self)
        wave_settings_button.clicked.connect(self.open_wave_settings)
        button_layout.addWidget(wave_settings_button)

        add_wave_button = QPushButton("Добавить волну", self)
        add_wave_button.clicked.connect(self.add_wave)
        button_layout.addWidget(add_wave_button)

        # Добавим выпадающий список для выбора волны
        self.remove_wave_combo = QComboBox(self)
        self.update_wave_list()
        button_layout.addWidget(self.remove_wave_combo)

        remove_wave_button = QPushButton("Удалить волну", self)
        remove_wave_button.clicked.connect(self.remove_wave)
        button_layout.addWidget(remove_wave_button)

        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def update_wave_list(self):
        self.remove_wave_combo.clear()
        for i in range(self.num_waves):
            self.remove_wave_combo.addItem(f"Волна {i + 1}")

    def open_wave_settings(self):
        dialog = WaveSettingsDialog(self.wave_params, self)
        dialog.exec_()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.begin(self)
        painter.setBrush(QColor(135, 206, 250))
        painter.drawRect(self.rect())

        for i, wave in enumerate(self.wave_params):
            amplitude, period, speed = wave["amplitude"], wave["period"], wave["speed"]
            mass, objem = self.poplavok_params[i]["mass"], self.poplavok_params[i]["objem"]
            wave_y = self.poplavok_positions[i]

            self.draw_wave(painter, wave_y, amplitude, period, speed)
            poplavok_x = (self.time * 5) % self.width()
            self.draw_poplavok(painter, wave_y, amplitude, period, speed, poplavok_x, mass, objem)

        painter.end()

    def draw_wave(self, painter, wave_y, amplitude, period, speed):
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)

        for x in range(self.width()):
            y = wave_y + amplitude * math.sin(2 * math.pi * (x / period) - speed * self.time)
            painter.drawPoint(x, int(y))

    def draw_poplavok(self, painter, wave_y, amplitude, period, speed, poplavok_x, mass, objem):
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
        for i, wave in enumerate(self.wave_params):
            poplavok_x = (self.time * 5) % self.width()
            poplavok_y = self.poplavok_positions[i] + self.wave_params[i]["amplitude"] * math.sin(
                2 * math.pi * (poplavok_x / self.wave_params[i]["period"]) - self.wave_params[i]["speed"] * self.time
            )
            offset = ((self.poplavok_params[i]["mass"] - self.poplavok_params[i]["objem"]) * self.g /
                      (self.poplavok_params[i]["mass"] + self.poplavok_params[i]["objem"])) * self.offset_scale
            poplavok_y += offset

            if (event.x() - poplavok_x) ** 2 + (event.y() - poplavok_y) ** 2 <= self.poplavok_radius ** 2:
                dialog = PoplavokSettingsDialog(self.poplavok_params[i], i, self)
                dialog.exec_()
                self.update()

    def animate(self):
        self.time += 0.1
        self.update()

    def add_wave(self):
        new_wave = {"amplitude": 50, "period": 100, "speed": 0.5}
        self.wave_params.append(new_wave)
        self.poplavok_params.append({"mass": 20, "objem": 15})
        self.num_waves += 1
        self.calculate_poplavok_positions()
        self.update_wave_list()

    def remove_wave(self):
        selected_wave = self.remove_wave_combo.currentIndex()
        if selected_wave != -1:
            self.wave_params.pop(selected_wave)
            self.poplavok_params.pop(selected_wave)
            self.num_waves -= 1
            self.calculate_poplavok_positions()
            self.update_wave_list()
            self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WaveSimulation()
    window.show()
    sys.exit(app.exec_())

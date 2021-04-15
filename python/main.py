import sys
import matplotlib
import numpy as np
import serial
import time
import datetime
import random

from serial.tools import list_ports

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

use_emulator = True
serial.protocol_handler_packages.append("emulator_handler")

matplotlib.use('Qt5Agg')


class DataExtractor(QtCore.QObject):

    finished = QtCore.pyqtSignal()
    connected = QtCore.pyqtSignal()
    failed_to_connect = QtCore.pyqtSignal()
    disconnected_signal = QtCore.pyqtSignal()

    def __init__(self, output_dir=None, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        if output_dir is None:
            self.output_dir = "Output/Output-"
        else:
            self.output_dir = output_dir
        self.obtained_data = [[], [], []]
        self.continue_record = None
        self.port = None
        self.port_str = None
        self.baudrate = None
        self.disconnect_req = False

    def start_record(self):
        self.obtained_data = [[], [], []]
        self.continue_record = True
        output_file_path = self.output_dir + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".txt"
        with open(output_file_path, "w") as output_file:
            start_time = datetime.datetime.now().timestamp()
            while self.continue_record:
                raw_data = [None, None, None]
                for i in range(2):
                    self.port.write(("get" + str(i) + "\n").encode())
                    raw_data[i] = self.port.read_until(expected='\n'.encode()).decode().strip()
                raw_data[2] = datetime.datetime.now().timestamp() - start_time

                self.obtained_data[0].append(parse_measure(raw_data[0]))
                self.obtained_data[1].append(parse_measure(raw_data[1]))
                self.obtained_data[2].append(raw_data[2])

                # print("{}\t{}\t{}".format(*raw_data))
                output_file.write("{}\t{}\t{}\n".format(*raw_data))
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop_record(self):
        self.continue_record = False

    def connect_to_port(self):
        if self.port_str == "emulator":
            self.port = serial.serial_for_url("emulator://", baudrate=self.baudrate, timeout=10)
        else:
            self.port = serial.Serial(port=self.port_str, baudrate=self.baudrate, timeout=2)
        answer = self.port.read_until().decode().strip()
        if answer != "ready":
            self.failed_to_connect.emit()
            print("failed to connect")
            if self.port.isOpen():
                self.port.close()
        else:
            print(answer)
            self.connected.emit()

    def disconnect(self):
        if self.port.isOpen():
            self.port.close()
        self.disconnected_signal.emit()


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(1, 1, 1)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QWidget):

    # make a stop and start signals to communicate with the worker in another thread
    stop_recording_signal = QtCore.pyqtSignal()
    start_recording_signal = QtCore.pyqtSignal()

    connect_signal = QtCore.pyqtSignal()
    disconnect_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Buttons:
        self.btn_record = QtWidgets.QPushButton('Start record')
        self.btn_record.resize(self.btn_record.sizeHint())
        self.btn_record.setDisabled(True)

        self.btn_connection = QtWidgets.QPushButton('Connect')
        self.btn_connection.resize(self.btn_connection.sizeHint())

        self.combo_ports = QtWidgets.QComboBox(self)
        available_ports = list_ports.comports()
        self.combo_ports.addItems([i.device for i in available_ports])
        self.combo_ports.addItem("emulator")

        self.combo_baudrate = QtWidgets.QComboBox(self)
        self.combo_baudrate.addItems([str(i) for i in serial.Serial.BAUDRATES])
        self.combo_baudrate.addItem("2000000")
        self.combo_baudrate.setCurrentIndex(len(serial.Serial.BAUDRATES))

        self.canvas = MplCanvas(self, width=10, height=7, dpi=100)

        # GUI title, size, etc...
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle('Mititoyo plot')
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.canvas, 0, 0, 5, 6)
        self.layout.addWidget(self.combo_ports, 6, 2)
        self.layout.addWidget(self.combo_baudrate, 6, 3)
        self.layout.addWidget(self.btn_connection, 6, 4)
        self.layout.addWidget(self.btn_record, 6, 5)
        self.setLayout(self.layout)

        # Thread:
        self.thread = QtCore.QThread()
        self.worker = DataExtractor()
        self.worker.moveToThread(self.thread)

        self.connect_signal.connect(self.worker.connect_to_port)
        self.disconnect_signal.connect(self.worker.disconnect)

        self.worker.connected.connect(self.enable_recording)
        self.worker.failed_to_connect.connect(self.on_disconnect)
        self.worker.disconnected_signal.connect(self.on_disconnect)
        self.start_recording_signal.connect(self.worker.start_record)
        self.stop_recording_signal.connect(self.worker.stop_record, type=QtCore.Qt.DirectConnection)

        self.thread.start()

        # connect buttons to their functions
        self.btn_record.clicked.connect(self.btn_record_action)
        self.btn_connection.clicked.connect(self.btn_connection_action)

        self.update_plot()
        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def btn_connection_action(self):
        if self.btn_connection.text() == "Connect":
            self.worker.port_str = self.combo_ports.currentText()
            self.worker.baudrate = self.combo_baudrate.currentText()
            self.connect_signal.emit()
            self.btn_connection.setDisabled(True)
        else:
            self.stop_recording_signal.emit()
            self.disconnect_signal.emit()
            self.btn_connection.setText("Connect")

    def enable_recording(self):
        self.btn_record.setEnabled(True)
        self.btn_connection.setText("Disconnect")
        self.btn_connection.setEnabled(True)

    def btn_record_action(self):
        if self.btn_record.text() == "Start record":
            self.start_recording_signal.emit()
            self.btn_record.setText("Stop record")
        else:
            self.stop_recording_signal.emit()
            # self.worker.stop_record()
            self.btn_record.setText("Start record")
        pass

    def on_disconnect(self):
        # set everything to initial state
        self.btn_connection.setEnabled(True)
        self.btn_connection.setText("Connect")
        self.btn_record.setDisabled(True)
        self.btn_record.setText("Start record")

    def update_plot(self):
        # self.xdata = self.worker.obtained_data[0]
        # self.ydata = self.worker.obtained_data[2]
        #
        # # Drop off the first y element, append a new one.
        # # self.ydata = self.ydata[1:] + [random.randint(0, 10)]
        # self.canvas.axes.cla()  # Clear the canvas.
        # self.canvas.axes.plot(self.xdata, self.ydata, 'r')
        # # Trigger the canvas to update and redraw.
        # self.canvas.draw()

        if len(self.worker.obtained_data) > 1:
            # if not len(self.canvas.axes.lines):
            #     self.canvas.axes.plot(0, 0, "-ro")
            # line = self.canvas.axes.lines[0]
            # self.canvas.axes.lines[0].set_xdata(self.worker.obtained_data[0][:-1])
            # self.canvas.axes.lines[0].set_ydata(self.worker.obtained_data[2][:-1])
            self.canvas.axes.cla()  # Clear the canvas.
            self.canvas.axes.plot(self.worker.obtained_data[2][:-1], self.worker.obtained_data[0][:-1], 'r-')
            self.canvas.axes.plot(self.worker.obtained_data[2][:-1], self.worker.obtained_data[1][:-1], 'b-')
            # self.canvas.axes.autoscale()
            # Trigger the canvas to update and redraw.
            self.canvas.draw()


def parse_measure(raw_data: str):
    if len(raw_data) == 0:
        return None
    value = int(raw_data[5:11]) *\
            10 ** (-int(raw_data[11])) *\
            (-1 if int(raw_data[4]) == 8 else 1)
    return value


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()

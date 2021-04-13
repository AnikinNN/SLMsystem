import sys
import matplotlib
import numpy as np
import serial
import time
import datetime

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')


class DataExtractor(QtCore.QObject):
    finished = QtCore.pyqtSignal()  # give worker class a finished signal

    def __init__(self, port, output_file_path=None, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        if output_file_path is None:
            self.output_file_path = "Output/Output-"
        else:
            self.output_file_path = output_file_path
        self.obtained_data = []
        self.output_file = None
        self.continue_run = True  # provide a bool run condition for the class

        self.port = serial.Serial(port=port, baudrate=115200, timeout=10)
        print(self.port.read_until().decode().strip())

    def start(self):
        self.continue_run = True  # provide a bool run condition for the class
        self.output_file_path += datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".txt"
        self.output_file = open(self.output_file_path, "w")
        while self.continue_run:
            raw_data = [None, None, None]
            for i in range(2):
                self.port.write(("get" + str(i)).encode())
                raw_data[i] = self.port.read_until().decode().strip()
            raw_data[2] = datetime.datetime.now().timestamp()
            self.obtained_data.append(raw_data)
            self.output_file.write("{}\t{}\t{}\n".format(*raw_data))
        self.output_file.close()
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QWidget):

    # make a stop and start signals to communicate with the worker in another thread
    stop_recording_signal = QtCore.pyqtSignal()
    start_recording_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Buttons:
        self.btn_record = QtWidgets.QPushButton('Start')
        self.btn_record.resize(self.btn_record.sizeHint())

        self.btn_connection = QtWidgets.QPushButton('Connect')
        self.btn_connection.resize(self.btn_connection.sizeHint())
        self.btn_connection.setCheckable(True)

        self.combo_ports = QtWidgets.QComboBox(self)
        self.combo_ports.addItems(["COM5", "COM6"])

        self.canvas = MplCanvas(self, width=10, height=7, dpi=100)
        # self.setCentralWidget(self.canvas)

        # GUI title, size, etc...
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle('Mititoyo plot')
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.canvas, 0, 0, 5, 6)
        self.layout.addWidget(self.combo_ports, 6, 3)
        self.layout.addWidget(self.btn_connection, 6, 4)
        self.layout.addWidget(self.btn_record, 6, 5)
        self.setLayout(self.layout)

        # Thread:
        self.thread = QtCore.QThread()
        self.worker = DataExtractor("COM5")
        self.stop_recording_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.start_recording_signal.connect(self.worker.start)  # connect stop signal to worker start method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.start)
        self.thread.finished.connect(self.worker.stop)

        self.btn_record.clicked.connect(self.btn_record_action)
        self.btn_connection.clicked.connect(self.btn_connection_action)

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

        self.update_plot()
        self.show()

    def btn_connection_action(self):
        if self.btn_connection.isChecked():
            self.btn_connection.setText("Disconnect")
        else:
            self.btn_connection.setText("Connect")

    def btn_record_action(self):

        pass

    def update_plot(self):
        return None
        if self.worker.continue_run:
            self.canvas.axes.cla()  # Clear the canvas.
            self.canvas.axes.plot(self.worker.obtained_data[:][0], self.worker.obtained_data[:][2], 'ro-')
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

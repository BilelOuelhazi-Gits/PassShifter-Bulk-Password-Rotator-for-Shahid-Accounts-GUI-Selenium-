from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, \
    QFileDialog, QMessageBox, QLineEdit
from PySide6.QtCore import Slot, QThread, Signal
import selenium_script
import os


class WorkerThread(QThread):
    status_signal = Signal(str)
    progress_signal = Signal(int)

    def __init__(self, credentials_file, output_file, new_password, chrome_driver_path):
        super().__init__()
        self.credentials_file = credentials_file
        self.output_file = output_file
        self.new_password = new_password
        self.chrome_driver_path = chrome_driver_path

    def run(self):
        selenium_script.CREDENTIALS_FILE = self.credentials_file
        selenium_script.NEW_PASSWORDS_OUTPUT_FILE = self.output_file
        selenium_script.NEW_PASSWORD = self.new_password
        selenium_script.CHROME_DRIVER_PATH = self.chrome_driver_path
        selenium_script.status_update = self.update_status
        self.status_signal.emit("Starting...")
        selenium_script.main()
        self.status_signal.emit("Completed.")
        self.progress_signal.emit(100)

    def update_status(self, message, progress):
        self.status_signal.emit(message)
        self.progress_signal.emit(progress)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PassShifter")
        self.setGeometry(100, 100, 600, 600)

        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create and style widgets
        self.browse_credentials_button = QPushButton("Browse Credentials File")
        self.browse_output_button = QPushButton("Browse Output File")
        self.browse_chromedriver_button = QPushButton("Browse ChromeDriver")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter new password (not working for now, password will be PassShifter)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.start_button = QPushButton("Start Process")
        self.status_label = QLabel("Status: Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Add widgets to layout
        self.layout.addWidget(self.browse_credentials_button)
        self.layout.addWidget(self.browse_output_button)
        self.layout.addWidget(self.browse_chromedriver_button)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.progress_bar)

        # Set up connections
        self.browse_credentials_button.clicked.connect(self.browse_credentials)
        self.browse_output_button.clicked.connect(self.browse_output)
        self.browse_chromedriver_button.clicked.connect(self.browse_chromedriver)
        self.start_button.clicked.connect(self.start_process)

        # Initialize variables
        self.credentials_file = None
        self.output_file = None
        self.chrome_driver_path = None

        # Create and configure the worker thread
        self.worker = None

        # Apply dark theme
        self.apply_dark_theme()

    @Slot()
    def browse_credentials(self):
        self.credentials_file, _ = QFileDialog.getOpenFileName(self, "Select Credentials File", "",
                                                               "Text Files (*.txt)")
        if self.credentials_file:
            self.status_label.setText(f"Selected credentials file: {os.path.basename(self.credentials_file)}")

    @Slot()
    def browse_output(self):
        self.output_file, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "Text Files (*.txt)")
        if self.output_file:
            self.status_label.setText(f"Selected output file: {os.path.basename(self.output_file)}")

    @Slot()
    def browse_chromedriver(self):
        self.chrome_driver_path, _ = QFileDialog.getOpenFileName(self, "Select ChromeDriver Executable", "",
                                                                 "Executable Files (*.exe)")
        if self.chrome_driver_path:
            self.status_label.setText(f"Selected ChromeDriver: {os.path.basename(self.chrome_driver_path)}")

    @Slot()
    def start_process(self):
        if not self.credentials_file:
            QMessageBox.warning(self, "Error", "Please select a credentials file.")
            return
        if not self.output_file:
            QMessageBox.warning(self, "Error", "Please select an output file.")
            return
        if not self.chrome_driver_path:
            QMessageBox.warning(self, "Error", "Please select the ChromeDriver executable.")
            return
        new_password = self.password_input.text()
        if not new_password:
            QMessageBox.warning(self, "Error", "Please enter a new password.")
            return

        self.status_label.setText("Status: Processing...")
        self.start_button.setEnabled(False)
        self.worker = WorkerThread(self.credentials_file, self.output_file, new_password, self.chrome_driver_path)
        self.worker.status_signal.connect(self.update_status)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.start()

    @Slot(str)
    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

    @Slot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def apply_dark_theme(self):
        dark_stylesheet = """
        QMainWindow {
            background-color: #1E1E1E;
            color: #FFFFFF;
            font-family: Arial, sans-serif;
        }
        QWidget {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #3C3C3C;
            border: 1px solid #4A4A4A;
            color: #FFFFFF;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #4A4A4A;
        }
        QLabel {
            color: #CCCCCC;
            font-size: 16px;
        }
        QLineEdit {
            background-color: #3C3C3C;
            border: 1px solid #4A4A4A;
            color: #FFFFFF;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        }
        QProgressBar {
            border: 1px solid #4A4A4A;
            border-radius: 5px;
            background-color: #3C3C3C;
            text-align: center;
            height: 20px;
        }
        QProgressBar::chunk {
            background-color: #4A90D9;
            border-radius: 5px;
        }
        """
        self.setStyleSheet(dark_stylesheet)


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()

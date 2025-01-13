import sys
from PySide6.QtWidgets import QApplication
from app_logic import AppLogic
from app import MainWindow


def main():
    app = QApplication(sys.argv)    
    # logic = AppLogic()
    window = MainWindow()

    window.show()
    app.exec()


if __name__ == "__main__":
    main()

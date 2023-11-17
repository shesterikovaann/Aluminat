import sqlite3
import sys
import io

from PyQt5 import uic, QtGui  # Импортируем uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QTableWidgetItem, QLineEdit
from time import sleep


class Aluminat(QMainWindow):  # окно с выбором, что делать
    def __init__(self):  # start передаёт значение - это начинает выполняться программа или это выход назад в меню
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(700, 400, 420, 240)
        self.setWindowTitle('Aluminat - главное меню')
        pal = self.palette()  # ниже задаём цвет фона
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor("#98FB98"))
        self.setPalette(pal)

        self.calc_button = QPushButton('Расчёт структур', self)
        self.calc_button.show()
        self.calc_button.move(230, 180)
        self.calc_button.resize(150, 30)
        self.calc_button.clicked.connect(self.start_calculate)

        self.data_book = QPushButton('Справочник', self)
        self.data_book.show()
        self.data_book.move(50, 180)
        self.data_book.clicked.connect(self.open_book)

        self.pixmap = QPixmap('aluminat_text.png')
        self.image = QLabel(self)
        self.image.move(50, -70)
        self.image.resize(300, 250)
        self.image.setPixmap(self.pixmap)


    def start_calculate(self):
        self.hide()
        self.al = Raschet()
        self.al.show()

    def open_book(self):
        self.hide()
        self.book = Book()
        self.book.show()


class StartForm(QWidget):  # окно загрузки начальное
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self): # запускаем окошко с загрузкой на 2 секунды (чист по приколу:)) так официальнее
        self.setGeometry(700, 400, 500, 300)
        self.setWindowTitle('Вступаете в общество Алюминатов?')
        self.pixmap = QPixmap('logo.png')
        self.image = QLabel(self)
        self.image.move(120, 10)
        self.image.resize(250, 250)
        self.image.setPixmap(self.pixmap)

        self.start_button = QPushButton("Начать", self)
        self.start_button.show()
        self.start_button.move(190, 250)
        self.start_button.resize(90, 30)
        self.start_button.clicked.connect(self.start)

    def start(self):
        self.hide()
        self.main_window = Aluminat()
        self.main_window.show()

        # начальное окно - картинка и загрузка


class Raschet(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('stroenie.ui', self)
        self.initUI()

    def initUI(self):
        self.pixmap = QPixmap('mini_logo.png')
        self.image = QLabel(self)
        self.image.move(720, 450)
        self.image.resize(250, 250)
        self.image.setPixmap(self.pixmap)
        self.back_button.clicked.connect(self.back)
        self.get_formule_button.clicked.connect(self.build)

    def back(self):
        self.hide()
        self.main_window = Aluminat()
        self.main_window.show()

    def build(self):
        name = self.enter_name.text()


class Book(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('data_book.ui', self)
        self.con = sqlite3.connect("himiya.sqlite")
        self.initUI()
        self.fill_elements()
        self.fill_groups()

    def initUI(self):
        self.to_menu_button.clicked.connect(self.back)
        self.add_to_bd.clicked.connect(self.add)
        self.del_from_bd.clicked.connect(self.delete)

    def fill_elements(self):
        self.cur = self.con.cursor()
        que = "SELECT * from elements"
        elements = self.cur.execute(que).fetchall()
        # print(elements)

        # Заполнили размеры таблицы
        self.elements.setRowCount(len(elements))
        self.elements.setColumnCount(len(elements[0]))
        self.elements.setHorizontalHeaderLabels(
            ['ID', "Название", "Формула", "ID группы"])

        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(elements):
            for j, val in enumerate(elem):
                self.elements.setItem(i, j, QTableWidgetItem(str(val)))

    def fill_groups(self):
        self.cur = self.con.cursor()
        que2 = "SELECT * from alk"
        groups = self.cur.execute(que2).fetchall()
        # print(groups)

        # Заполнили размеры таблицы
        self.groups.setRowCount(len(groups))
        self.groups.setColumnCount(len(groups[0]))
        self.groups.setHorizontalHeaderLabels(
            ['ID', "Название", "Формула", "ID группы"])

        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(groups):
            for j, val in enumerate(elem):
                self.groups.setItem(i, j, QTableWidgetItem(str(val)))

    def back(self):
        self.hide()
        self.main_window = Aluminat()
        self.main_window.show()

    def add(self):
        self.add_form = AddForm(self)
        self.add_form.show()

    def delete(self):
        self.del_form = DelForm(self)
        self.del_form.show()


class DelForm(QMainWindow):
    def __init__(self, root):
        super().__init__(root)
        uic.loadUi('empty.ui', self)
        self.main = root
        self.con = sqlite3.connect("himiya.sqlite")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Удалить элемент')

        self.del_id = QLabel("Введите ID элемента:", self)
        self.del_id.move(30, 20)
        self.del_id.resize(300, 30)
        self.del_id.show()

        self.name_text = QLineEdit("", self)
        self.name_text.move(30, 70)
        self.name_text.resize(300, 30)
        self.name_text.show()

        self.del_element = QPushButton("Удалить", self)
        self.del_element.move(30, 120)
        self.del_element.resize(100, 30)
        self.del_element.show()
        self.del_element.clicked.connect(self.del_from_elements)

    def del_from_elements(self):
        cur = self.con.cursor()
        delable_id = self.name_text.text()
        cur.execute(f"DELETE from elements where id = {delable_id}")
        self.con.commit()
        self.main.fill_elements()
        self.close()


class AddForm(QMainWindow):
    def __init__(self, root):
        super().__init__(root)
        uic.loadUi('empty.ui', self)
        self.main = root
        self.con = sqlite3.connect("himiya.sqlite")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Добавить элемент')

        self.add_name = QLabel("Введите название:", self)
        self.add_name.move(20, 10)
        self.add_name.resize(300, 30)
        self.add_name.show()

        self.name_text = QLineEdit("", self)
        self.name_text.move(20, 30)
        self.name_text.resize(300, 30)
        self.name_text.show()

        self.add_formule = QLabel("Введите формулу:", self)
        self.add_formule.move(20, 70)
        self.add_formule.resize(300, 30)
        self.add_formule.show()

        self.formule_text = QLineEdit("", self)
        self.formule_text.move(20, 90)
        self.formule_text.resize(300, 30)
        self.formule_text.show()

        self.text = QLabel("Вещество добавится в пользовательскую группу.", self)
        self.text.move(20, 120)
        self.text.resize(400, 30)
        self.text.show()

        self.text2 = QLabel("Индекс группы веществ - 6.", self)
        self.text2.move(20, 140)
        self.text2.resize(400, 30)
        self.text2.show()

        self.add_element = QPushButton("Добавить", self)
        self.add_element.move(20, 175)
        self.add_element.resize(100, 30)
        self.add_element.show()
        self.add_element.clicked.connect(self.add_to_elements)

    def add_to_elements(self):
        cur = self.con.cursor()
        id = cur.execute("SELECT max(id) FROM elements").fetchone()[0] + 1
        name_of_element = self.name_text.text()
        element_formule = self.formule_text.text()
        alk_id = 6
        new_data = (id, name_of_element, element_formule, alk_id)
        cur.execute("INSERT INTO elements VALUES (?,?,?,?)", new_data)
        self.con.commit()
        self.main.fill_elements()
        self.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StartForm()
    ex.show()
    sys.exit(app.exec_())
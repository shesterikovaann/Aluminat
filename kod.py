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
        self.get_formule_button.clicked.connect(self.show_build)
        self.clear_button.clicked.connect(self.clearing)

    def clearing(self):
        self.structure_formule_place.clear()

    def show_build(self):
        chain, name, connection = self.build()  # здесь выведем вещество в виджет вместе со связями
        joined_chain = chain[1][0]
        for i in range(len(chain[1]) - 1):
            if name.endswith("ен"):
                if i + 1 in connection:
                    joined_chain += "  =  "
                else:
                    joined_chain += "  -  "
            elif name.endswith("ин"):
                if i + 1 in connection:
                    joined_chain += "  ≡  "
                else:
                    joined_chain += "  -  "
            else:
                joined_chain += "  -  "
            joined_chain += chain[1][i + 1]
        chain[1] = joined_chain
        # print(chain)

        up_branch = [" "] * (len(chain[1]) + 10)
        down_branch = [" "] * (len(chain[1]) + 10)
        up_indexes_of_palochka = []
        down_indexes_of_palochka = []
        for i in range(len(chain[1])):
            if chain[1][i] == "C":
                if chain[0][0]:
                    up_indexes_of_palochka.append(i)
                    up_branch[i:i + len(chain[0][0])] = list(chain[0][0])
                del chain[0][0]
                if chain[2][0]:
                    down_indexes_of_palochka.append(i)
                    down_branch[i:i + len(chain[2][0])] = list(chain[2][0])
                del chain[2][0]
        chain[0] = "".join(up_branch).rstrip()
        chain[2] = "".join(down_branch).rstrip()
        up_palochki = [" "] * len(up_branch)
        down_palochki = [" "] * len(down_branch)
        for i in up_indexes_of_palochka:
            up_palochki[i] = "|"
        for i in down_indexes_of_palochka:
            down_palochki[i] = "|"
        chain.insert(1, "".join(up_palochki))
        chain.insert(3, "".join(down_palochki))
        print("\n".join(chain))
        self.structure_formule_place.appendPlainText("\n".join(chain))


    def back(self):
        self.hide()
        self.main_window = Aluminat()
        self.main_window.show()

    def build(self):  # возвращает список компонентов структуры вещества, название и список, где какие связи
        self.name = "".join(self.enter_name.text().split())
        self.join_bd()
        branch_nums, branches, main_element, connection = self.components()
        print(branch_nums, branches, main_element, connection)

        if main_element == "метан":
            return [[''], ['CH4'], ['']], main_element, connection
        # если класс алкил у вещества, то строим из бд его обычную формулу
        for i in self.elements[:11]:
            if i[0] == main_element and i[2] == "алкил":
                return [[''], [i[1]], ['']], main_element, connection
        # остальные вещества для которых есть алгоритм
        try:
            len_c = 0
            for i in self.elements:
                if main_element == i[0]:
                    len_c = int(i[1][1])
                    break
                # элемент точно есть в списке, мы уже проверяли это при вычислении компонентов
            chain = [[""] * len_c, ["CH"] * len_c, [""] * len_c]
            for i in branch_nums:
                el = self.branch_formule(branches[0])
                if not chain[0][i - 1]:
                    chain[0][i - 1] = el
                else:
                    chain[2][i - 1] = el
                branches = branches[1:]
            # вывод
            # for i in chain:
            #     print(i)
            if (branch_nums and sorted(branch_nums)[-1] > len_c) or \
                    (connection and sorted(connection)[-1] >= len_c):  # хим ошибка
                raise ValueError
            if main_element[-2:] == "ен":  # проверяем на двойную водородную связь
                # ошибка при вводе логическая по теории химии
                if (main_element.endswith("диен") and str(len(connection)) not in "02") \
                        or (main_element[-4:-2] != "ди" and str(len(connection)) not in "01"):
                    raise ValueError  # чисто химическая ошибка

                last_double = False
                # вещества для которых не пишутся, где двойные соединения, так как только 1 вариант - код отдельный
                if main_element == "пропадиен" and len(connection) == 0:
                    connection = [1, 2]
                if main_element == "этен" and len(connection) == 0:
                    connection = [1]
                for i in range(len(chain[1])):
                    h = 4
                    h = h - (branch_nums.count(i + 1))
                    if last_double:
                        h -= 2
                        last_double = False
                    else:
                        if i != 0:
                            h -= 1
                    if i + 1 in connection:
                        last_double = True
                        h -= 2
                    else:
                        if i != len(chain[1]) - 1:
                            h -= 1
                    if h < 0:
                        raise ValueError
                    str_h = f"H{h}" if h != 1 else "H"
                    chain[1][i] = "C" + (str_h if h else "")
                print(chain)

            if main_element[-2:] == "ан":  # проверяем на одинокую:_( водородную связь
                for i in range(len(chain[1])):
                    h = 4
                    if branch_nums:
                        h = h - (branch_nums.count(i + 1))
                    h -= 1  # так как все вещества соединены, хотя бы на 1 водород меньше
                    # а вот если вещество между двух - то вычитается 2 водорода, 2 связи занято
                    if i != 0 and i != len(chain[1]) - 1:
                        h -= 1
                    if h < 0:
                        raise ValueError
                    str_h = f"H{h}" if h != 1 else "H"
                    chain[1][i] = "C" + (str_h if h else "")
                print(chain)

            if main_element[-2:] == "ин":  # проверяем на тройную водородную связь
                last_triple = False
                if main_element == "этин" and len(connection) == 0:
                    connection = [1]
                elif len(connection) != 1:
                    raise ValueError
                for i in range(len(chain[1])):
                    h = 4
                    h = h - (branch_nums.count(i + 1))
                    if last_triple:
                        h -= 3
                        last_triple = False
                    else:
                        if i != 0:
                            h -= 1
                    if i + 1 in connection:
                        last_triple = True
                        h -= 3
                    else:
                        if i != len(chain[1]) - 1:
                            h -= 1
                    if h < 0:
                        raise ValueError
                    str_h = f"H{h}" if h != 1 else "H"
                    chain[1][i] = "C" + (str_h if h else "")
                print(chain)
            return chain, main_element, connection

        except Exception:
            self.structure_formule_place.appendPlainText("Неверный ввод")

    def branch_formule(self, elem):
        for i in self.elements:  # элемент точно есть в списке, мы уже проверяли это при вычислении компонентов
            if i[0] == elem:
                return i[1]

    def join_bd(self):
        self.con = sqlite3.connect("himiya.sqlite")
        self.cur = self.con.cursor()
        que = '''SELECT
                    elements.name,
                    elements.structure,
                    alk.alk_name
                FROM
                    elements
                JOIN alk
                    ON elements.alk_id=alk.id;'''
        self.elements = self.cur.execute(que).fetchall()
        # print(self.elements)

    def components(self):
        name = self.name[:]
        try:
            if "-" not in name:
                # for i in self.elements:
                #     if i[0] == name:
                #         struct, alk = i[1], i[2]
                #         print(struct, alk)
                #         break
                # else:
                #     raise ValueError
                return [], [], name, []
            connect = []
            if name[-1] in "1234567890":  # проверяем на наличие двойных связей - циферок в конце
                name = name.split("-")
                connect = list(map(int, name[-1].split(",")))
                name = "-".join(name[:-1])

            main_el = ""
            for i in self.elements:  # выделяем основной элемент - от которого и будем далее плясать
                if name.endswith(i[0]):
                    main_el = i[0]
                    name = name[:-len(i[0])]

            numbers, names = [], []
            if "-" in name:  # проверяем оставшиеся циферки которые обязательно соединяются '-'
                for i in name.split("-"):
                    if i[0] in "1234567890":
                        numbers += list(map(int, i.split(",")))
                    else:
                        names.append(i)
                new_names = []
                for i in names:
                    if i.startswith("ди"):
                        new_names.append(i[2:])
                        new_names.append(i[2:])
                    elif i.startswith("три"):
                        new_names.append(i[3:])
                        new_names.append(i[3:])
                        new_names.append(i[3:])
                    elif i.startswith("тетра"):
                        new_names.append(i[5:])
                        new_names.append(i[5:])
                        new_names.append(i[5:])
                        new_names.append(i[5:])
                    else:
                        new_names.append(i)
                names = new_names[:]
            if not main_el:
                raise ValueError
            possible_elements = [i[0] for i in self.elements]
            for i in names:
                if i not in possible_elements:
                    raise ValueError
            return numbers, names, main_el, connect

        except Exception:
            self.structure_formule_place.appendPlainText("Неверный ввод")


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

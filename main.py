import os

from PyQt5 import QtCore, QtWidgets, QtGui
import sys
import platform
import subprocess
from configparser import ConfigParser
from itertools import (product, count)
from string import ascii_lowercase
from os import (path, mkdir)
import webbrowser
import json
import matplotlib.pyplot as plt
from source.widgets_content import (StageContent, FlowContent, OWFlowContent, DFactorContent, Result)
from source.math_module import EpidemicModel
from source.ui_py.main_ui import Ui_MainWindow
from source.stage_widget import StageWidget
from source.flow_widget import FlowWidget
from source.owflow_widget import OWFlowWidget
from source.dfactor_widget import DFactorWidget
from source.result_widget import ResultWidget
from source.description_dialog import DescriptionDialog
from source.settings import Settings, DeepSettings, UserSettings
from source.settings_dialog import SettingsDialog, QuestionDialog
from source.new_model_dialog import NewModelDialog
from source.message import Message, ErrorMessage
from source.global_func import input_to_num
import traceback
import logging


class RecentModelAct(QtWidgets.QAction):
    def __init__(self, name, parent_w):
        super(RecentModelAct, self).__init__(name)
        self.filename = name
        self.parent_w = parent_w

    def load_model(self):
        self.parent_w.model_open = True
        self.parent_w.set_all_enabled(True)
        self.parent_w.open_recent_model(self.filename)


class WarningClose(QuestionDialog):
    def __init__(self, parent_w, question, title, yes_text, no_text, cancel_text):
        try:
            super(WarningClose, self).__init__(parent_w=parent_w, question=question, title=title,
                                               yes_text=yes_text, no_text=no_text)
            self.cancel_btn = QtWidgets.QPushButton(cancel_text)
            self.btn_box.addButton(self.cancel_btn, QtWidgets.QDialogButtonBox.RejectRole)
            self.cancel_btn.clicked.connect(self.cancel)
            self.answer = -1
            self.setWindowIcon(QtGui.QIcon(parent_w.deep_settings.window_icon_filename))
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def cancel(self):
        try:
            self.answer = -1
            self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, settings, deep_settings):
        try:
            super(MainWindow, self).__init__()
            self.setupUi(self)
            self.settings = settings
            self.deep_settings = deep_settings
            self.user_settings = UserSettings(deep_settings)
            self.user_settings = UserSettings.get_user_settings(self.user_settings)
            self.create_parser()

            self.system_name = platform.system()

            # настройка размеров основного окна
            # screen = QtWidgets.QDesktopWidget().availableGeometry()
            # self.setGeometry(screen)
            self.setWindowState(QtCore.Qt.WindowMaximized)

            # создаём переменные для модели, для её имени и описания, для имени файла модели
            self.model = None
            self.model_name = None
            self.description = ""
            self.path = None
            self.filename = self.deep_settings.default_filename
            self.changed = False
            self.model_open = False

            # создание списков со стадиями, потоками, однонаправленными потоками, динамическими факторами
            # именами файлов результатов, именами файлов результатов для отображения
            self.list_stage = []
            self.list_flow = []
            self.list_owflow = []
            self.list_dfactor = []
            self.list_result = []
            self.list_result_show = []

            # функции при нажатии на кнопки
            self.Add_stage_btn.clicked.connect(self.add_stage)
            self.Add_flow_btn.clicked.connect(self.add_flow)
            self.Add_owflow_btn.clicked.connect(self.add_owflow)
            self.Add_dfactor_btn.clicked.connect(self.add_dfactor)
            self.Add_result_file_btn.clicked.connect(self.add_file_result)
            self.Joint_show_btn.clicked.connect(self.show_result)
            self.Add_description_btn.clicked.connect(self.add_description)
            self.Manual_stop_rbtn.toggled.connect(self.change_stop_mode)
            self.Start_model_btn.clicked.connect(self.start_model)

            # функции действий меню
            self.Act_exit.triggered.connect(self.close)
            self.Act_save.triggered.connect(self.save_model)
            self.Act_save_as.triggered.connect(self.save_as_model)
            self.Act_open_model.triggered.connect(self.open_file_model)
            self.Act_new_model.triggered.connect(self.new_model)
            self.Act_settings.triggered.connect(self.open_settings)
            self.Act_clear_last.triggered.connect(self.full_clear_recent)
            self.Act_help.triggered.connect(self.open_help)
            self.Act_about.triggered.connect(self.show_splash)

            self.Act_save.setShortcut("Ctrl+S")
            self.Act_save_as.setShortcut("Ctrl+Alt+S")
            self.Act_open_model.setShortcut("Ctrl+O")
            self.Act_new_model.setShortcut("Ctrl+N")

            self.recent_lst = []
            self.update_recent_lst()

            # создание зон скролинга для стадий, потоков, однонаправленных потоков, результатов, динамических факторов
            self.scroll_stages = QtWidgets.QScrollArea()
            self.scroll_flows = QtWidgets.QScrollArea()
            self.scroll_owflows = QtWidgets.QScrollArea()
            self.scroll_results = QtWidgets.QScrollArea()
            self.scroll_dfactors = QtWidgets.QScrollArea()

            # настройка зон скролинга
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.scroll_stages.setWidgetResizable(True)
            self.scroll_stages.setSizePolicy(sizePolicy)
            self.scroll_flows.setWidgetResizable(True)
            self.scroll_flows.setSizePolicy(sizePolicy)
            self.scroll_owflows.setWidgetResizable(True)
            self.scroll_owflows.setSizePolicy(sizePolicy)
            self.scroll_results.setWidgetResizable(True)
            self.scroll_results.setSizePolicy(sizePolicy)
            self.scroll_dfactors.setWidgetResizable(True)
            self.scroll_dfactors.setSizePolicy(sizePolicy)

            # в столбцы вставляем зоны скролинга
            self.Stage_column_layout.insertWidget(3, self.scroll_stages)
            self.Flow_column_layout.insertWidget(3, self.scroll_flows)
            self.Owflow_dfactor_column_layout.insertWidget(3, self.scroll_owflows)
            self.Owflow_dfactor_column_layout.insertWidget(7, self.scroll_dfactors)
            self.Model_column_layout.insertWidget(14, self.scroll_results)

            # создаём виджеты для контента для зон скролинга
            self.scroll_flows_cont = QtWidgets.QWidget()
            self.scroll_stages_cont = QtWidgets.QWidget()
            self.scroll_owflows_cont = QtWidgets.QWidget()
            self.scroll_results_cont = QtWidgets.QWidget()
            self.scroll_dfactors_cont = QtWidgets.QWidget()

            # создаём компановщики для виждетов контента
            self.stages_layout = QtWidgets.QVBoxLayout()
            self.scroll_stages_cont.setLayout(self.stages_layout)
            self.flows_layout = QtWidgets.QVBoxLayout()
            self.scroll_flows_cont.setLayout(self.flows_layout)
            self.owflows_layout = QtWidgets.QVBoxLayout()
            self.scroll_owflows_cont.setLayout(self.owflows_layout)
            self.results_layout = QtWidgets.QVBoxLayout()
            self.scroll_results_cont.setLayout(self.results_layout)
            self.dfactors_layout = QtWidgets.QVBoxLayout()
            self.scroll_dfactors_cont.setLayout(self.dfactors_layout)

            # добавляем виджет контента в зону скролинга
            self.scroll_stages.setWidget(self.scroll_stages_cont)
            self.scroll_flows.setWidget(self.scroll_flows_cont)
            self.scroll_owflows.setWidget(self.scroll_owflows_cont)
            self.scroll_results.setWidget(self.scroll_results_cont)
            self.scroll_dfactors.setWidget(self.scroll_dfactors_cont)

            # создание спейсера в столбец результатов
            self.results_layout.addItem(
                QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

            # создаём генератор имён для стадий и генератор имён динамических факторов
            self.stage_name_generator = self.get_stage_name()
            self.dfactor_name_generator = self.get_factor_name()

            # настройка параметров симуляции
            self.update_settings_model()
            self.update_show_result()
            app.processEvents()

            self.Menu_bar.setNativeMenuBar(False)

            self.setWindowIcon(QtGui.QIcon(self.deep_settings.window_icon_filename))
            # установка надписей на нужном языке
            self.set_text()
            self.setWindowTitle(self.deep_settings.program_title.format(self.filename))
            self.show()
            if len(app.arguments()) > 1:
                self.model_open = True
                self.set_all_enabled(True)
                self.filename = app.arguments()[1]
                self.setWindowTitle(self.deep_settings.program_title.format(self.filename))
                self.load_file_model()
            else:
                self.set_all_enabled(False)
                self.new_model()
            logger.debug("Init MainWindow")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def show_splash(self):
        try:
            self.splash = QtWidgets.QSplashScreen(QtGui.QPixmap(self.deep_settings.splash_filename))
            #self.splash.showMessage("ss", 1, "red")
            #self.splash.showMessage(self.deep_settings.program_version, 2, QtGui.QColor(255, 0, 0, 255))
            self.splash.showMessage("<font face='Cambria' size=4>Version {}</font>".format(self.deep_settings.program_version),
                                    QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight, QtCore.Qt.black)
            self.splash.show()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def open_help(self):
        try:
            logger.debug("Open help with")
            filename = self.deep_settings.help_dir + self.deep_settings.help_filename.format(self.user_settings.language)

            if not path.exists(filename):
                filename = self.deep_settings.help_dir + self.deep_settings.help_filename.format("english")

            if self.system_name == "Windows":
                os.startfile(filename)
            elif self.system_name == "Darwin":
                subprocess.call(("open", filename))
            else:
                subprocess.call(('xdg-open', filename))

        except Exception:
            logger.warning("Cannot open help file", exc_info=True)
            section = self.user_settings.language.upper()
            title = self.lang_parser.get(section, "Warning_title", fallback="Warning_title")
            message = self.lang_parser.get(section, "Help_open_error_msg", fallback="Help_open_error_msg\n{dir}")
            message = message.format(dir=self.deep_settings.help_dir)
            msg = Message(message, title, self)
            msg.exec_()

    def set_all_enabled(self, enabled):
        logger.debug("set_all_enabled {}".format(enabled))
        for widget in self.findChildren(QtWidgets.QWidget):
            if not isinstance(widget, (QtWidgets.QMenu, QtWidgets.QMenuBar, QtWidgets.QAction)):
                widget.setEnabled(enabled)
        if not self.model_open:
            self.Act_save.setEnabled(False)
            self.Act_save_as.setEnabled(False)
        else:
            self.Act_save.setEnabled(True)
            self.Act_save_as.setEnabled(True)

    def full_update(self):
        logger.debug("full_update")
        logger.debug("in full_update 1" + str(self.user_settings.dfactor_file_head))
        self.create_parser()
        logger.debug("in full_update 2" + str(self.user_settings.dfactor_file_head))
        self.set_text()
        logger.debug("in full_update 3" + str(self.user_settings.dfactor_file_head))
        self.update_show_result()
        logger.debug("in full_update 4" + str(self.user_settings.dfactor_file_head))
        self.update_stages()
        logger.debug("in full_update 5" + str(self.user_settings.dfactor_file_head))
        self.update_flows()
        self.update_owflows()
        self.update_dfactors()
        self.update_results()

    def create_parser(self):
        # self.lang_parser = ConfigParser()
        self.lang_parser = ConfigParser()
        self.lang_parser.read(self.deep_settings.language_file.format(self.user_settings.language.lower()),
                              encoding="utf-8-sig")

    def set_text(self):
        # настроить все надписи в интерфейсе в соответствии с языком
        section = self.user_settings.language.upper()
        for widget in self.findChildren((QtWidgets.QWidget, QtWidgets.QAction)):
            if widget.objectName() != "":
                # if self.lang_parser.has_option(section, widget.objectName()):
                if isinstance(widget, (QtWidgets.QLabel, QtWidgets.QPushButton,
                                        QtWidgets.QCheckBox, QtWidgets.QRadioButton, QtWidgets.QAction)):
                    widget.setText(self.lang_parser.get(section, widget.objectName(), fallback=widget.objectName()))
                elif isinstance(widget, (QtWidgets.QGroupBox, QtWidgets.QMenu)):
                    widget.setTitle(self.lang_parser.get(section, widget.objectName(), fallback=widget.objectName()))

    @staticmethod
    def get_factor_name_old():
        for size in count(1):
            for s in product(ascii_lowercase, repeat=size):
                yield "".join(s)

    @staticmethod
    def get_stage_name_old():
        num = 1
        while True:
            yield "Stage_" + str(num)
            num += 1

    def get_factor_name(self):
        for size in count(1):
            for s in product(ascii_lowercase, repeat=size):
                name = "".join(s)
                if name in [df.name for df in self.list_dfactor]:
                    continue
                else:
                    yield "".join(s)

    def get_stage_name(self):
        num = 1
        while True:
            name = "Stage_" + str(num)
            if name in [stage.name for stage in self.list_stage]:
                num += 1
                continue
            else:
                yield name
                num += 1

    def get_model_name(self, location):
        file_id = 1
        name_mask = self.deep_settings.default_model_name + "_{:03d}"
        file_mask = location + name_mask + self.deep_settings.file_extension
        filename = file_mask.format(file_id)
        while path.exists(filename):
            file_id += 1
            filename = file_mask.format(file_id)
        return name_mask.format(file_id)

    def get_filename(self):
        file_id = 1
        file_mask = self.deep_settings.result_file
        filename = file_mask.format(self.model_name, file_id)
        while path.exists(filename):
            file_id += 1
            filename = file_mask.format(self.model_name, file_id)
        return filename

    def take_default(self):
        logger.debug("take_default")
        self.changed = False
        self.list_stage = []
        self.list_flow = []
        self.list_owflow = []
        self.list_dfactor = []
        self.list_result = []
        self.list_result_show = []
        self.update_stages()
        self.update_flows()
        self.update_owflows()
        self.update_dfactors()
        self.update_results()
        self.update_info()
        self.model_name = ""
        self.description = ""
        self.path = self.deep_settings.default_path
        self.filename = self.deep_settings.default_filename
        self.settings.take_default()
        self.update_settings_model()
        self.stage_name_generator = self.get_stage_name()
        self.dfactor_name_generator = self.get_factor_name()

    def new_model(self):
        try:
            logger.info("new_model")
            if self.changed:
                self.changed = not self.warning_close()
            if not self.changed:
                dialog = NewModelDialog(self)
                dialog.exec_()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def create_new_model(self, name="", location=""):
        logger.debug("create_new_model")
        self.take_default()
        if location != "":
            self.path = location
        else:
            self.path = self.deep_settings.default_path

        if name == "" or name == self.deep_settings.default_model_name:
            self.model_name = self.get_model_name(self.path)
        else:
            self.model_name = name

        self.update_settings_model()

    def save_model(self):
        try:
            logger.info("save_model")
            if self.filename == self.deep_settings.default_filename:
                self.save_as_model()
            else:
                self.update_info()
                self.save_file_model()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def save_as_model(self):
        try:
            logger.debug("save_as_model")
            self.update_info()
            last_filename = self.filename
            filename = self.path + self.model_name + self.deep_settings.file_extension
            title = self.lang_parser.get(self.user_settings.language.upper(), "Save_model_title", fallback="Save_model_title")
            self.filename = QtWidgets.QFileDialog.getSaveFileName(self, title, directory=filename)[0]
            if self.filename != "":
                self.save_file_model()
            else:
                self.filename = last_filename
                # self.filename = self.deep_settings.default_filename

            self.setWindowTitle(self.deep_settings.program_title.format(self.filename))

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def save_file_model(self):
        logger.info("save_file_model: {}".format(self.filename))
        common_dic = {"Model_name": self.model_name, "Description": self.description,
                      "Stages": [], "Flows": [], "Ow_flows": [], "Dfactors": [],
                      "Settings": dict(vars(self.settings)), "Associated result files": []}

        for res in self.list_result:
            result = {}
            result["filename"] = res.f_path + res.file_result
            result["info"] = res.info
            common_dic["Associated result files"].append(result)

        for st in self.list_stage:
            stage = dict(vars(st))
            stage.pop("parent_w")
            common_dic["Stages"].append(stage)

        for fl in self.list_flow:
            flow = dict(vars(fl))
            flow.pop("list_factor")
            flow.pop("parent_w")
            common_dic["Flows"].append(flow)

        for ow_fl in self.list_owflow:
            ow_flow = dict(vars(ow_fl))
            ow_flow.pop("list_factor")
            ow_flow.pop("parent_w")
            common_dic["Ow_flows"].append(ow_flow)

        for df in self.list_dfactor:
            dfactor = dict(vars(df))
            dfactor.pop("parent_w")
            common_dic["Dfactors"].append(dfactor)

        with open(self.filename, "w", encoding="utf-8-sig") as file:
            json.dump(common_dic, file, indent=4)

        self.add_recent_file()
        self.changed = False

    def open_file_model(self):
        try:
            logger.info("open_file_model")
            if self.changed:
                self.changed = not self.warning_close()
            if not self.changed:
                title = self.lang_parser.get(self.user_settings.language.upper(), "Open_model_title",
                                             fallback="Open_model_title")
                open_filename = QtWidgets.QFileDialog.getOpenFileName(self, title)[0]
                if open_filename != "":
                    last_filename = self.filename
                    self.filename = open_filename
                    if self.load_file_model():
                        logger.debug("Not remember")
                        self.changed = False
                        self.model_open = True
                    else:
                        logger.debug("Remember last filename")
                        self.filename = last_filename
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def load_file_model(self):
        logger.debug("load_file_model")
        try:
            with open(self.filename, "r", encoding="utf-8-sig") as file:
                common_dic = json.load(file)
            filename = self.filename
            self.setWindowTitle(self.deep_settings.program_title.format(self.filename))
            self.take_default()
            self.filename = filename
            self.description = common_dic["Description"]
            self.model_name = common_dic["Model_name"]

            for st in common_dic["Stages"]:
                self.list_stage.append(StageContent(parent_w=self, **st))
            for df in common_dic["Dfactors"]:
                self.list_dfactor.append(DFactorContent(parent_w=self, **df))
            for fl in common_dic["Flows"]:
                self.list_flow.append(FlowContent(list_factor=self.list_dfactor, parent_w=self, **fl))
            for ow_fl in common_dic["Ow_flows"]:
                self.list_owflow.append(OWFlowContent(list_factor=self.list_dfactor, parent_w=self, **ow_fl))
            for res in common_dic["Associated result files"]:
                if not path.exists(res["filename"]):
                    msg = self.get_message_text(["Not_exist_result", res["filename"], ""])
                    self.show_message(msg, "Warning_save_title")
                    logger.warning("Not exist result {0}".format(res["filename"]))
                else:
                    if not res["filename"] in [r.f_path + r.file_result for r in self.list_result]:
                        self.list_result.append(Result(parent_w=self, delimiter=self.user_settings.file_delimiter,
                                                   floating_point=self.user_settings.floating_point,
                                                   **res))
                    else:
                        msg = self.get_message_text(["Exist_result", res["filename"], ""])
                        self.show_message(msg, "Warning_save_title")
                        logger.warning("Exist result {0}".format(res["filename"]))
                # self.list_result.append(ResultContent(user_settings=self.user_settings, **res))

            self.settings = Settings(**common_dic["Settings"])
            self.full_update()
            self.update_settings_model()
            self.add_recent_file()
            self.set_all_enabled(True)
            self.model_open = True
            self.full_update()

            return True

        except json.decoder.JSONDecodeError:
            logger.debug("json.decoder.JSONDecodeError")
            info = ["Incorrect_model_file", self.filename, ""]
            msg = self.get_message_text(info)
            title = "Warning_title"
            self.show_message(msg, title)

            return False

    def warning_close(self):
        logger.debug("warning_close")
        section = self.user_settings.language.upper()
        question = self.lang_parser.get(section, "Warning_question", fallback="Warning_question").format(self.filename)
        title = self.lang_parser.get(section, "Warning_save_title", fallback="Warning_save_title")
        yes_text = self.lang_parser.get(section, "Yes", fallback="Yes")
        no_text = self.lang_parser.get(section, "No", fallback="No")
        cancel_text = self.lang_parser.get(section, "Cancel", fallback="Cancel")
        warning = WarningClose(self, question, title, yes_text, no_text, cancel_text)
        warning.exec_()
        if warning.answer == 1:
            self.save_model()
            return True
        elif warning.answer == 0:
            return True
        else:
            return False

    def add_recent_file(self):
        logger.debug("add_recent_file")
        file_list = []
        if path.exists(self.deep_settings.recent_file):
            with open(self.deep_settings.recent_file, "r", encoding="utf-8-sig") as file:
                for fname in file:
                    file_list.append(fname.strip())
        if self.filename in file_list:
            file_list.remove(self.filename)
        if len(file_list) > self.deep_settings.max_recent_file - 1:
            file_list = file_list[-(self.deep_settings.max_recent_file - 1):]

        file_list.append(self.filename)

        with open(self.deep_settings.recent_file, "w", encoding="utf-8-sig") as file:
            for fname in file_list:
                file.write(fname + "\n")

        self.update_recent_lst()

    def clear_recent_lst(self):
        logger.debug("clear_recent_lst")
        self.recent_lst = []
        self.Menu_last_models.clear()

        self.Menu_last_models.addAction(self.Act_clear_last)

    def full_clear_recent(self):
        logger.debug("full_clear_recent")
        self.clear_recent_lst()
        with open(self.deep_settings.recent_file, "w", encoding="utf-8-sig") as file:
            pass
        self.Act_clear_last.setEnabled(False)

    def update_recent_lst(self):
        logger.debug("update_recent_lst")
        self.clear_recent_lst()
        if path.exists(self.deep_settings.recent_file):
            with open(self.deep_settings.recent_file, "r", encoding="utf-8-sig") as file:
                count_recent = 0
                last_line = file.readline().strip()
                while last_line != "" and count_recent < self.deep_settings.max_recent_file:
                    self.recent_lst.append(RecentModelAct(last_line, self))
                    last_line = file.readline().strip()

            for act_i in range(len(self.recent_lst) - 1, -1, -1):
                #self.recent_lst[act_i].triggered.connect()
                self.Menu_last_models.insertAction(self.Act_clear_last, self.recent_lst[act_i])
                self.recent_lst[act_i].triggered.connect(self.recent_lst[act_i].load_model)

            if self.recent_lst:
                self.Menu_last_models.insertSeparator(self.Act_clear_last)
                self.Act_clear_last.setEnabled(True)
            else:
                self.Act_clear_last.setEnabled(False)

    def open_recent_model(self, filename):
        try:
            logger.info("open_recent_model {}".format(filename))
            if self.changed:
                self.changed = not self.warning_close()
            if not self.changed:
                last_filename = self.filename
                self.filename = filename
                if not self.load_file_model():
                    self.filename = last_filename
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def add_file_result(self):
        try:
            logger.debug("add_file_result")
            title = self.lang_parser.get(self.user_settings.language.upper(), "Open_result_title",
                                         fallback="Open_result_title")
            filename = QtWidgets.QFileDialog.getOpenFileName(self, title,
                                                             directory=self.deep_settings.result_dir)[0]

            if filename != "":
                self.add_result(filename, False)

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def get_message_text(self, info):
        section = self.user_settings.language.upper()
        message_text = self.lang_parser.get(section, info[0], fallback=info[0])
        element = self.lang_parser.get(section, info[2], fallback=info[2])
        message_text = message_text.format(el_no=info[1], el_type=element)
        return message_text

    def show_message(self, msg_text, msg_title):
        title = self.lang_parser.get(self.user_settings.language.upper(), msg_title, fallback=msg_title)
        msg_window = Message(msg_text, title, self)
        msg_window.exec_()

    def make_model(self):
        logger.debug("make_model")
        # проверка стадий
        check = True
        info = []
        element = ""
        title = "Model_check_title"
        stages = []
        flows = []
        ow_flows = []
        dfactors = []

        self.update_info()
        self.update_stages()
        self.update_flows()
        self.update_owflows()
        self.update_dfactors()

        try:
            # добавление и проверка стадий
            element = "Stage"
            if len(self.list_stage) < 1:
                info.append(["Num_stages", "", ""])
                check = False
            else:
                set_stage = set([st.name for st in self.list_stage])
                if len(set_stage) < len(self.list_stage):
                    info.append(["Identical_stage_name", "", ""])
                    check = False
                el_i = 1
                for st in self.list_stage:
                    dis_stage, check_add, info_add = st.get_stage(el_i)
                    if check_add:
                        stages.append(dis_stage)
                    else:
                        check = False
                        info += info_add
                    el_i += 1

                if all(st.num == 0 for st in stages):
                    info.append(["Zero_start_num", "", ""])
                    check = False

            # добавление и проверка потоков
            element = "Flow"
            el_i = 1
            if len(self.list_flow) < 1:
                info.append(["Num_flows", "", ""])
                check = False
            else:
                # сумма коэффициентов для каждой стадии как источника
                source_f_sum = {st.name: 0 for st in self.list_stage}

                for fl in self.list_flow:
                    flow, check_add, info_add = fl.get_flow(el_i)
                    if check_add:
                        flows.append(flow)

                        # добавляет к сумме коэффициентов стадий как источников
                        if not fl.dynamic:
                            source_f_sum[fl.source] += input_to_num(fl.sfactor)

                        for tar in flow.target:
                            if not tar in [st.name for st in stages]:
                                info.append(["Not_exist_flow_target", el_i, tar])
                                check = False
                        if flow.induction:
                            for ind_s in flow.inducing_stages:
                                if not ind_s in [st.name for st in stages]:
                                    info.append(["Not_exist_flow_istage", el_i, ind_s])
                                    check = False
                    else:
                        check = False
                        info += info_add
                    el_i += 1

                for source in source_f_sum:
                    if source_f_sum[source] >= 1 and not self.settings.divided_n:
                        info.append(["Large_sum_factor_stage_as_source", source, ""])
                        logger.warning("Large sum factor stage as source: {}".format(source))
                        check = False

            # добавление и проверка однонаправленных потоков
            element = "Ow_flow"
            el_i = 1
            for o_fl in self.list_owflow:
                ow_flow, check_add, info_add = o_fl.get_ow_flow(el_i)
                if check_add:
                    ow_flows.append(ow_flow)
                else:
                    check = False
                    info += info_add
                el_i += 1

        except Exception as e:
            msg = traceback.format_exc() + "Last element: {0} No.{1}"
            logger.error(msg.format(element, el_i))
            emsg = ErrorMessage(message=msg.format(element, el_i), parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

        if self.settings.stop_mode == "m":
            check_add, info_add = self.settings.check_limit_step()
            if not check_add:
                check = False
                info += info_add

        if not check:
            message = ""
            for i in info:
                message += self.get_message_text(i) + "\n"
            title = self.lang_parser.get(self.user_settings.language.upper(), title, fallback=title)
            msg_window = Message(message, title, self)
            msg_window.exec_()
            self.model = None
        else:
            self.model = EpidemicModel(stages, flows, ow_flows, dict(vars(self.settings)))

    def start_model(self):
        try:
            logger.info("start_model")
            answer = self.warning_close()
            if answer:
                self.make_model()
                if self.model is not None:
                    filename = self.get_filename()

                    self.model.start_model()
                    self.add_result(filename, True)
                    # self.add_result(filename[:-4] + "_flows.csv", False)
                else:
                    logger.warning("model not maked")
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def change_stop_mode(self):
        try:
            logger.debug("change_stop_mode")
            if self.Manual_stop_rbtn.isChecked():
                self.settings.stop_mode = "m"
                self.Num_step_lbl.setEnabled(True)
                self.Num_step_edit.setEnabled(True)
            else:
                self.settings.stop_mode = "a"
                self.Num_step_lbl.setEnabled(False)
                self.Num_step_edit.setEnabled(False)

            self.changed = True

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def add_description(self):
        try:
            logger.debug("add_description")
            dialog = DescriptionDialog(self.description, self)
            dialog.exec_()
            self.description = dialog.content
            del dialog
            self.changed = True
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def open_settings(self):
        try:
            logger.debug("open_settings")
            dialog = SettingsDialog(self.settings, self.user_settings, self)
            dialog.exec_()
            # self.settings = dialog.new_settings
            del dialog
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def add_dfactor(self):
        try:
            logger.info("add_dfactor")
            self.update_info()
            self.list_dfactor.append(DFactorContent(next(self.dfactor_name_generator), parent_w=self))
            self.update_dfactors()
            self.update_flows()
            self.update_owflows()

            self.changed = True
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def add_stage(self):
        try:
            logger.info("add_stage")
            self.update_info()
            self.list_stage.append(StageContent(next(self.stage_name_generator), parent_w=self))
            self.update_stages()
            self.update_flows()
            self.update_owflows()

            self.changed = True

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def add_flow(self):
        try:
            logger.info("add_flow")
            self.update_info()
            self.list_flow.append(FlowContent(list_factor=self.list_dfactor, parent_w=self))
            self.update_flows()
            self.changed = True

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def add_owflow(self):
        try:
            logger.info("add_owflow")
            self.update_info()
            self.list_owflow.append(OWFlowContent(list_factor=self.list_dfactor, parent_w=self))
            self.update_owflows()

            self.changed = True

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def add_result(self, filename, new, result_dic=None):
        try:
            logger.info("add_result")
            self.update_info()
            if filename in [r.f_path + r.file_result for r in self.list_result]:
                msg = self.get_message_text(["Exist_result", filename, ""])
                self.show_message(msg, "Warning_title")
                logger.warning("Exist result {0}".format(filename))
            else:
                if new:
                    if result_dic is not None:
                        self.list_result.append(Result(filename, self, delimiter=self.user_settings.file_delimiter,
                                                       floating_point=self.user_settings.floating_point,
                                                       result_dic=result_dic))
                        self.list_result[-1].write_result()
                    else:
                        self.list_result.append(Result(filename, self,
                                                       delimiter=self.user_settings.file_delimiter,
                                                       floating_point=self.user_settings.floating_point,
                                                       model_name=self.model_name, file_model=self.filename,
                                                       description=self.description, model=self.model))
                        self.list_result[-1].write_result()
                        self.list_result[-1].write_info()
                else:
                    self.list_result.append(Result(filename, self,
                                                   delimiter=self.user_settings.file_delimiter,
                                                   floating_point=self.user_settings.floating_point))

                self.update_results()
                self.changed = True
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def update_show_result(self):
        logger.debug("update_show_result")
        self.list_result_show = []
        for i in range(len(self.list_result)):
            if self.list_result[i].show:
                self.list_result_show.append([i, len(self.list_result[i].result_dic)])
        temple = self.lang_parser.get(self.user_settings.language.upper(), self.Joint_show_btn.objectName(),
                                      fallback=self.Joint_show_btn.objectName())
        self.Joint_show_btn.setText(temple.format(str(self.user_settings.max_num_graphs - len(self.list_result_show))))
        if self.user_settings.max_num_graphs - len(self.list_result_show) < 0:
            self.Joint_show_btn.setEnabled(False)
        else:
            self.Joint_show_btn.setEnabled(True)

    def show_result(self):
        try:
            logger.debug("show_result")
            self.update_show_result()
            if self.list_result_show and len(self.list_result_show) < self.user_settings.max_num_graphs + 1:
                if len(self.list_result_show) < self.user_settings.max_num_graphs + 1:
                    colors = []
                    for i in range(max([r[1] for r in self.list_result_show]) - 1):
                        colors.append(None)
                    plots = []
                    for r_i in range(len(self.list_result_show)):
                        if r_i == 0:
                            linestyle = "-"
                        elif r_i == 1:
                            linestyle = "--"
                        elif r_i == 2:
                            linestyle = "-."
                        else:
                            linestyle = ":"
                        i = 0
                        for name in self.list_result[self.list_result_show[r_i][0]].result_dic:
                            if name != "step":
                                label = self.list_result[self.list_result_show[r_i][0]].file_result[
                                        :self.deep_settings.num_char_label] + "..." + \
                                        self.list_result[self.list_result_show[r_i][0]].file_result[-6:-4] + " ->"+ name
                                #label = "..." + self.list_result[self.list_result_show[r_i][0]].file_result[
                                #                -self.deep_settings.num_char_label:-4] + " -> " + name
                                plots += plt.plot(self.list_result[self.list_result_show[r_i][0]].result_dic["step"],
                                                  self.list_result[self.list_result_show[r_i][0]].result_dic[name],
                                                  label=label, color=colors[i], linestyle=linestyle)
                                colors[i] = plots[-1].get_color()
                                i += 1
                    plt.legend()
                    plt.grid()
                    plt.show()

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def delete_stage(self, stage_num):
        try:
            logger.info("delete_stage")
            self.update_info()
            self.list_stage.pop(stage_num)
            self.update_stages()
            self.update_flows()
            self.update_owflows()
            self.changed = True
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def delete_flow(self, flow_num):
        try:
            logger.info("delete_flow")
            self.update_info()
            self.list_flow.pop(flow_num)
            self.update_flows()
            self.changed = True
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def delete_owflow(self, owflow_num):
        try:
            logger.info("delete_owflow")
            self.update_info()
            self.list_owflow.pop(owflow_num)
            self.update_owflows()

            self.changed = True
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def delete_dfactor(self, dfactor_num):
        try:
            logger.info("delete_dfactor")
            self.update_info()
            self.list_dfactor.pop(dfactor_num)
            self.update_dfactors()
            self.update_flows()
            self.update_owflows()
            self.changed = True

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    def delete_result(self, result_num):
        try:
            logger.info("delete_result")
            self.update_info()
            self.list_result.pop(result_num)
            self.update_results()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)

    @staticmethod
    def clear_widgets(layout):
        deleted_widget = layout.takeAt(0)
        while deleted_widget is not None:
            if not isinstance(deleted_widget, QtWidgets.QSpacerItem):
                del_widget = deleted_widget.widget()
                del_widget.deleteLater()
            del deleted_widget
            deleted_widget = layout.takeAt(0)

        layout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

    def update_stages(self):
        logger.debug("update_stages")
        self.clear_widgets(self.stages_layout)
        for st_i in range(len(self.list_stage)):
            self.stages_layout.insertWidget(st_i, StageWidget(self.list_stage[st_i], st_i, self))

    def update_flows(self):
        logger.debug("update_flows")
        self.clear_widgets(self.flows_layout)
        for fl_i in range(len(self.list_flow)):
            self.flows_layout.insertWidget(fl_i, FlowWidget(self.list_flow[fl_i], fl_i, self))

    def update_owflows(self):
        logger.debug("update_owflows")
        self.clear_widgets(self.owflows_layout)
        for ofl_i in range(len(self.list_owflow)):
            self.owflows_layout.insertWidget(ofl_i, OWFlowWidget(self.list_owflow[ofl_i], ofl_i, self))

    def update_dfactors(self):
        logger.debug("update_dfactors")
        self.clear_widgets(self.dfactors_layout)
        for df_i in range(len(self.list_dfactor)):
            self.dfactors_layout.insertWidget(df_i,
                                              DFactorWidget(self.list_dfactor[df_i], df_i, self, self.user_settings))

    def update_results(self):
        logger.debug("update_results")
        self.clear_widgets(self.results_layout)
        for r_i in range(len(self.list_result)):
            if self.list_result[r_i].correct:
                self.results_layout.insertWidget(r_i, ResultWidget(self.list_result[r_i], r_i, self))
            else:
                self.list_result.pop(r_i)

    def update_info(self):
        logger.debug("update_info")
        for i in range(len(self.list_stage)):
            self.list_stage[i].name = self.stages_layout.itemAt(i).widget().Stage_name_edit.text()
            self.list_stage[i].start_num = self.stages_layout.itemAt(i).widget().Stage_start_num_edit.text()
        for i in range(len(self.list_flow)):
            self.list_flow[i].dynamic = self.flows_layout.itemAt(i).widget().Flow_dfactor_cbox.isChecked()
            self.list_flow[i].source = self.flows_layout.itemAt(i).widget().Flow_source_name_box.currentText()
            self.list_flow[i].dfactor = self.flows_layout.itemAt(i).widget().Flow_dfactor_name_box.currentText()
            self.list_flow[i].sfactor = self.flows_layout.itemAt(i).widget().Flow_sfactor_value_edit.text()
            self.list_flow[i].induction = self.flows_layout.itemAt(i).widget().Flow_induction_cbox.isChecked()
        for i in range(len(self.list_owflow)):
            self.list_owflow[i].dynamic = self.owflows_layout.itemAt(i).widget().Owflow_dfactor_cbox.isChecked()
            self.list_owflow[i].stage = self.owflows_layout.itemAt(i).widget().Owflow_stage_name_box.currentText()
            self.list_owflow[i].sfactor = self.owflows_layout.itemAt(i).widget().Owflow_sfactor_value_edit.text()
            self.list_owflow[i].dfactor = self.owflows_layout.itemAt(i).widget().Owflow_dfactor_name_box.currentText()

            if self.owflows_layout.itemAt(i).widget().Owflow_direction_in_rbtn.isChecked():
                self.list_owflow[i].direction = True
            else:
                self.list_owflow[i].direction = False

            if self.owflows_layout.itemAt(i).widget().Owflow_relativity_stage_rbtn.isChecked():
                self.list_owflow[i].relativity = "stage"
            elif self.owflows_layout.itemAt(i).widget().Owflow_relativity_common_rbtn.isChecked():
                self.list_owflow[i].relativity = "common"
            else:
                self.list_owflow[i].relativity = "absoluteness"

        for i in range(len(self.list_dfactor)):
            self.list_dfactor[i].name = self.dfactors_layout.itemAt(i).widget().Dfactor_name_edit.text()

        self.model_name = self.Model_name_edit.text()
        self.settings.limit_step = self.Num_step_edit.text()

    def update_settings_model(self):
        logger.debug("update_settings_model")
        self.Model_name_edit.setText(self.model_name)
        self.Num_step_edit.setText(str(self.settings.limit_step))

        if self.settings.stop_mode == "a":
            self.Auto_stop_rbtn.setChecked(True)
        elif self.settings.stop_mode == "m":
            self.Manual_stop_rbtn.setChecked(True)

    def closeEvent(self, event):
        try:
            logger.info("closeEvent")
            if self.changed:
                self.changed = not self.warning_close()
                if not self.changed:
                    event.accept()
                else:
                    event.ignore()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self)
            emsg.exec_()
            raise SystemExit(1)


if __name__ == "__main__":
    program_name = path.basename(sys.argv[0])
    program_path = path.abspath(sys.argv[0])
    program_path = program_path[:-len(program_name)]
    deep_settings = DeepSettings(program_path, program_version="0.0.3 beta")
    settings = Settings()

    if not path.exists(deep_settings.result_dir):
        mkdir(deep_settings.result_dir)
    if not path.exists(deep_settings.data_dir):
        mkdir(deep_settings.data_dir)
    if not path.exists(deep_settings.log_dir):
        mkdir(deep_settings.log_dir)
    if not path.exists(deep_settings.report_dir):
        mkdir(deep_settings.report_dir)
    if not path.exists(deep_settings.default_path):
        mkdir(deep_settings.default_path)

    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)

    file_log = logging.FileHandler(deep_settings.log_dir + deep_settings.get_log_filename())
    console_log = logging.StreamHandler()

    file_log.setLevel(logging.INFO)
    console_log.setLevel(logging.DEBUG)

    file_format = logging.Formatter(deep_settings.file_log_format)
    console_format = logging.Formatter(deep_settings.console_log_format)

    file_log.setFormatter(file_format)
    console_log.setFormatter(console_format)

    logger.addHandler(file_log)
    logger.addHandler(console_log)

    app = QtWidgets.QApplication(sys.argv)
    logger.debug("Start {name}".format(name=deep_settings.full_name))
    app.processEvents()
    main_window = MainWindow(settings, deep_settings)
    sys.exit(app.exec_())


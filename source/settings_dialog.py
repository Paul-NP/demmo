from source.ui_py.settings_ui import Ui_SettingsDialog_2
from source.message import ErrorMessage
from PyQt5 import QtCore, QtWidgets, QtGui
from source.settings import Settings, UserSettings
import os
from source.message import Message
import logging
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class QuestionDialog(QtWidgets.QDialog):
    def __init__(self, parent_w, question, title, yes_text, no_text):
        try:
            super(QuestionDialog, self).__init__()
            self.question_layout = QtWidgets.QVBoxLayout(self)
            self.parent_w = parent_w
            self.answer = 0

            self.setWindowTitle(title)
            self.question_lbl = QtWidgets.QLabel(question)

            self.question_layout.addWidget(self.question_lbl)
            self.question_layout.addWidget(self.question_lbl)
            self.btn_box = QtWidgets.QDialogButtonBox(self)
            self.question_layout.addWidget(self.btn_box)

            yes_btn = QtWidgets.QPushButton(yes_text)
            no_btn = QtWidgets.QPushButton(no_text)

            self.btn_box.addButton(yes_btn, QtWidgets.QDialogButtonBox.YesRole)
            self.btn_box.addButton(no_btn, QtWidgets.QDialogButtonBox.ResetRole)
            self.btn_box.setCenterButtons(True)

            yes_btn.clicked.connect(self.yes)
            no_btn.clicked.connect(self.no)

            logger.debug("Init QuestionDialog")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def yes(self):
        try:
            self.answer = 1
            self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def no(self):
        try:
            self.answer = 0
            self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)


class SettingsDialog(QtWidgets.QDialog, Ui_SettingsDialog_2):
    def __init__(self, settings, user_settings, parent_w):
        try:
            self.new_settings = Settings(settings)
            self.new_user_settings = UserSettings(parent_w.deep_settings, user_settings)
            self.deep_settings = parent_w.deep_settings
            super(SettingsDialog, self).__init__()
            self.setupUi(self)
            self.parent_w = parent_w
            self.lang_list = []
            self.fill_boxes()
            self.set_text()
            self.update_btn_box()

            self.Set_default_btn.clicked.connect(self.set_default)
            self.setWindowIcon(QtGui.QIcon(self.parent_w.deep_settings.window_icon_filename))
            logger.debug("Init SettingsDialog")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def fill_boxes(self):
        # заполнение combobox существующими в папке locales языками
        self.Set_language_box.clear()
        self.lang_list = []
        if os.path.exists(self.deep_settings.language_dir):
            file_list = os.listdir(self.deep_settings.language_dir)
            for filename in file_list:
                if filename.endswith(".ini"):
                    self.lang_list.append(filename[:-4])
                    self.Set_language_box.addItem(filename[:-4])
            for lang_i in range(len(self.lang_list)):
                if self.lang_list[lang_i] == self.new_user_settings.language:
                    self.Set_language_box.setCurrentIndex(lang_i)

        # заполнение остальных полей
        self.Set_breaking_dist_edit.setText(str(self.new_settings.braking_dist))
        self.Set_delimiter_edit.setText(str(self.new_user_settings.file_delimiter))
        self.Set_threshold_edit.setText(str(self.new_settings.threshold))
        self.Set_check_period_edit.setText(str(self.new_settings.check_period))
        self.Set_max_graphs_edit.setText(str(self.new_user_settings.max_num_graphs))
        self.Set_max_step_edit.setText(str(self.new_settings.max_step))
        self.Set_df_file_head_cbox.setChecked(self.new_user_settings.dfactor_file_head)
        self.Set_divided_n_cbox.setChecked(self.new_settings.divided_n)

    def update_btn_box(self):
        section = self.parent_w.user_settings.language.upper()
        self.Set_btn_box.clear()
        ok_text = self.parent_w.lang_parser.get(section, self.Set_btn_box.objectName() + "_ok",
                                                fallback=self.Set_btn_box.objectName() + "_ok")
        cancel_text = self.parent_w.lang_parser.get(section, self.Set_btn_box.objectName() + "_cancel",
                                                    fallback=self.Set_btn_box.objectName() + "_cancel")
        reset_text = self.parent_w.lang_parser.get(section, self.Set_btn_box.objectName() + "_default",
                                                   fallback=self.Set_btn_box.objectName() + "_default")
        apply_text = self.parent_w.lang_parser.get(section, self.Set_btn_box.objectName() + "_apply",
                                                   fallback=self.Set_btn_box.objectName() + "_apply")

        self.Set_btn_box.addButton(ok_text, QtWidgets.QDialogButtonBox.AcceptRole)
        self.Set_btn_box.addButton(cancel_text, QtWidgets.QDialogButtonBox.RejectRole)

        reset_btn = QtWidgets.QPushButton(reset_text)
        self.Set_btn_box.addButton(reset_btn, QtWidgets.QDialogButtonBox.ResetRole)
        apply_btn = QtWidgets.QPushButton(apply_text)
        self.Set_btn_box.addButton(apply_btn, QtWidgets.QDialogButtonBox.ApplyRole)

        reset_btn.clicked.connect(self.set_reset)
        apply_btn.clicked.connect(self.apply)
        self.Set_btn_box.rejected.connect(self.close)
        self.Set_btn_box.accepted.connect(self.accept)

        self.Set_btn_box.setLayoutDirection(QtCore.Qt.LeftToRight)

    def set_reset(self):
        try:
            section = self.parent_w.user_settings.language.upper()
            question = self.parent_w.lang_parser.get(section, "Reset_question_lbl", fallback="Reset_question_lbl")
            title = self.parent_w.lang_parser.get(section, "Reset_title", fallback="Reset_title")
            yes_text = self.parent_w.lang_parser.get(section, "Yes", fallback="Yes")
            no_text = self.parent_w.lang_parser.get(section, "No", fallback="No")
            question = QuestionDialog(self.parent_w, question, title, yes_text, no_text)
            question.exec_()

            if question.answer == 1:
                self.new_settings = Settings()
                self.new_user_settings = UserSettings(self.deep_settings)
                self.fill_boxes()
                self.apply()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_default(self):
        try:
            self.new_settings = Settings()
            self.fill_boxes()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def apply(self):
        try:
            self.new_user_settings.file_delimiter = self.Set_delimiter_edit.text()
            self.new_user_settings.max_num_graphs = self.Set_max_graphs_edit.text()
            self.new_user_settings.dfactor_file_head = self.Set_df_file_head_cbox.isChecked()
            self.new_user_settings.language = self.Set_language_box.currentText()
            self.new_settings.divided_n = self.Set_divided_n_cbox.isChecked()
            self.new_settings.braking_dist = self.Set_breaking_dist_edit.text()
            self.new_settings.threshold = self.Set_threshold_edit.text()
            self.new_settings.check_period = self.Set_check_period_edit.text()
            self.new_settings.max_step = self.Set_max_step_edit.text()

            check_s, info_s = self.new_settings.check_settings()
            check_us, info_us = self.new_user_settings.check_settings()
            if check_s and check_us:
                self.new_user_settings.write_user_settings()
                self.parent_w.settings = Settings(self.new_settings)
                self.parent_w.user_settings = UserSettings(self.parent_w.deep_settings, self.new_user_settings)
                self.parent_w.full_update()
                self.set_text()
                self.update_btn_box()
                self.fill_boxes()
                return True
            else:
                message = ""
                for i in info_s:
                    message += self.parent_w.get_message_text(i) + "\n"
                for i in info_us:
                    message += self.parent_w.get_message_text(i) + "\n"

                title = "Settings_error"
                title = self.parent_w.lang_parser.get(self.parent_w.user_settings.language.upper(), title,
                                                      fallback=title)
                msg_window = Message(message, title, self.parent_w)
                msg_window.exec_()
                return False

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def accept(self):
        try:
            if self.apply():
                self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_text(self):
        section = self.parent_w.user_settings.language.upper()

        title_text = self.parent_w.lang_parser.get(section, "Settings_title", fallback="Settings_title")
        self.setWindowTitle(title_text)

        for widget in self.findChildren(QtWidgets.QWidget):
            if isinstance(widget, QtWidgets.QTabWidget):
                text_auto_set = self.parent_w.lang_parser.get(section, self.Set_auto_stop_tab.objectName(),
                                                              fallback=self.Set_auto_stop_tab.objectName())
                widget.setTabText(0, text_auto_set)
                text_general_set = self.parent_w.lang_parser.get(section, self.Set_general_tab.objectName(),
                                                                 fallback=self.Set_general_tab.objectName())
                widget.setTabText(1, text_general_set)
            elif isinstance(widget, (QtWidgets.QLabel, QtWidgets.QCheckBox, QtWidgets.QPushButton)):
                widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(),
                                                             fallback=widget.objectName()))

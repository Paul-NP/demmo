from source.ui_py.result_ui import Ui_Result
from source.ui_py.result_info_ui import Ui_InfoDialog
from source.group_dialog import GroupDialog
from source.message import ErrorMessage
from PyQt5 import QtGui, QtWidgets
from os import path
import logging
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class ResultWidget(QtWidgets.QWidget, Ui_Result):
    def __init__(self, result_c, number, parent_w):
        try:
            super(ResultWidget, self).__init__()
            self.setupUi(self)
            self.content = result_c
            self.parent_w = parent_w
            self.number = number

            self.suffix = ""
            # настройка галочки отображения
            self.Result_show_cbox.stateChanged.connect(self.change_show)
            self.Result_show_cbox.setChecked(self.content.show)

            # настройка кнопок
            #self.Del_result_btn.setIcon(QtGui.QIcon("icon/delete_icon_2.png"))
            self.Del_result_btn.clicked.connect(self.delete)
            self.Result_info_btn.clicked.connect(self.show_info)
            self.Result_set_group_btn.clicked.connect(self.set_group)
            self.Result_group_res_btn.clicked.connect(self.add_result_group)

            self.set_text()

            logger.debug("Init ResultWidget")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def get_suffix(self):
        i = 1
        temple = self.parent_w.deep_settings.group_suffix
        while path.exists(self.content.f_path + self.content.file_result[:-4] + temple.format(i)):
            i += 1
        return temple.format(i)

    def add_result_group(self):
        try:
            if self.content.groups:
                self.suffix = self.get_suffix()
                self.content.add_group_info(self.suffix)
                new_filename = self.content.file_result[:-4] + self.suffix
                result_dic = self.content.create_group_result()
                self.parent_w.add_result(self.content.f_path + new_filename, result_dic=result_dic, new=True)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_group(self):
        try:
            dialog = GroupDialog(self.content.result_dic, self.content.groups, self.parent_w)
            dialog.exec_()
            self.content.groups = list(dialog.groups)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def show_info(self):
        try:
            dialog = ResultInfoDialog(self.parent_w, self.content.info)
            dialog.exec_()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def delete(self):
        try:
            self.parent_w.delete_result(self.number)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def change_show(self):
        try:
            self.content.show = self.Result_show_cbox.isChecked()
            self.parent_w.update_show_result()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_text(self):
        section = self.parent_w.user_settings.language.upper()
        for widget in self.findChildren((QtWidgets.QLabel, QtWidgets.QPushButton,
                                        QtWidgets.QCheckBox)):
            widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(), fallback=widget.objectName()))
        self.Result_lbl.setText(self.Result_lbl.text().format(self.content.file_result))


class ResultInfoDialog(QtWidgets.QDialog, Ui_InfoDialog):
    def __init__(self, parent_w, info):
        try:
            super(ResultInfoDialog, self).__init__(parent_w)
            self.setupUi(self)
            section = parent_w.user_settings.language.upper()
            self.Info_lbl.setText(parent_w.lang_parser.get(section, self.Info_lbl.objectName(),
                                                           fallback=self.Info_lbl.objectName()))
            self.setWindowTitle(parent_w.lang_parser.get(section, "Info_title", fallback="Info_title"))
            self.Info_txt.setText(info)
            self.Info_txt.setReadOnly(True)
            logger.debug("Init ResultInfoDialog")
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)


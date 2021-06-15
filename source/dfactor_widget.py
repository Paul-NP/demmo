from source.ui_py.dfactor_ui import Ui_Dfactor
from PyQt5 import QtGui, QtWidgets
from os import path
from source.math_module import DynamicFactor
import logging
import traceback
from source.message import ErrorMessage

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class DFactorWidget(QtWidgets.QWidget, Ui_Dfactor):
    def __init__(self, dfactor_c, number, parent_w, user_settings):
        try:
            super(DFactorWidget, self).__init__()
            self.setupUi(self)
            self.number = number
            self.content = dfactor_c
            self.parent_w = parent_w

            self.file_head = user_settings.dfactor_file_head
            self.delimiter = user_settings.file_delimiter

            self.Dfactor_name_edit.setText(self.content.name)

            self.Del_dfactor_btn.clicked.connect(self.delete)
            #self.Del_dfactor_btn.setIcon(QtGui.QIcon("icon/delete_icon_2.png"))
            self.Dfactor_add_step_btn.clicked.connect(self.add_step_value)
            self.Dfactor_del_step_btn.clicked.connect(self.del_step_value)
            self.Dfactor_clear_step_btn.clicked.connect(self.clear_step_value)
            self.Dfactor_browse_btn.clicked.connect(self.select_file)
            self.Dfactor_load_btn.clicked.connect(self.load_value)

            self.Dfactor_name_edit.textEdited.connect(self.update_parents_flows)

            self.set_text()

            for step in self.content.dic_values:
                self.Dfactor_value_lst.addItem("{0}: {1}".format(step, self.content.dic_values[step]))

            logger.debug("Init DFactorWidget")
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def update_parents_flows(self):
        self.parent_w.update_info()
        self.parent_w.update_flows()
        self.parent_w.update_owflows()

    def add_step_value(self):
        try:
            if self.Dfactor_step_edit.text() != "" and self.Dfactor_value_step_edit.text():
                if self.Dfactor_step_edit.text() in self.content.dic_values:
                    for i in range(self.Dfactor_value_lst.count()):
                        if self.Dfactor_value_lst.item(i).text() == "{0}: {1}".format(
                                self.Dfactor_step_edit.text(),
                                self.content.dic_values[self.Dfactor_step_edit.text()]):
                            self.Dfactor_value_lst.item(i).setText("{0}: {1}".format(
                                self.Dfactor_step_edit.text(),
                                self.Dfactor_value_step_edit.text()))
                else:
                    self.Dfactor_value_lst.addItem("{0}: {1}".format(self.Dfactor_step_edit.text(),
                                                               self.Dfactor_value_step_edit.text()))
                self.content.dic_values[self.Dfactor_step_edit.text()] = self.Dfactor_value_step_edit.text()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def del_step_value(self):
        try:
            if self.Dfactor_value_lst.currentItem() is not None:
                step, _ = self.Dfactor_value_lst.currentItem().text().split(":")
                del self.content.dic_values[step]
                self.Dfactor_value_lst.takeItem(self.Dfactor_value_lst.currentRow())
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def clear_step_value(self):
        try:
            self.Dfactor_value_lst.clear()
            self.content.dic_values = {}
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def select_file(self):
        try:
            section = self.parent_w.user_settings.language.upper()
            title = self.parent_w.lang_parser.get(section, "Open_dfactor_title", fallback="Open_dfactor_title")
            self.Dfactor_file_name_edit.setText(
                QtWidgets.QFileDialog.getOpenFileName(self.parent_w, title)[0])
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def load_value(self):
        try:
            filename = self.Dfactor_file_name_edit.text()
            if path.exists(filename):
                x, y = DynamicFactor.take_file(filename, self.file_head, self.delimiter)
                for i in range(len(x)):
                    self.content.dic_values[str(x[i])] = str(y[i])
                    self.Dfactor_value_lst.addItem("{0}: {1}".format(str(x[i]), str(y[i])))
        except (ValueError, IndexError):
            info = ["incorrect_dfactor_file", filename, ""]
            msg = self.parent_w.get_message_text(info)
            title = "Warning_title"
            self.parent_w.show_message(msg, title)

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def delete(self):
        try:
            self.parent_w.delete_dfactor(self.number)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_text(self):
        section = self.parent_w.user_settings.language.upper()
        for widget in self.findChildren(QtWidgets.QWidget):
            if isinstance(widget, (QtWidgets.QLabel, QtWidgets.QPushButton)):
                # if self.parent_w.lang_parser.has_option(section, widget.objectName()):
                widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(),
                                                             fallback=widget.objectName()))
        self.Dfactor_lbl.setText(self.Dfactor_lbl.text().format(str(self.number + 1)))

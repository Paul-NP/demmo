from PyQt5 import QtWidgets
from source.ui_py.group_ui import Ui_GroupWidget
from source.message import ErrorMessage
import logging
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class GroupContent:
    def __init__(self, name):
        self.stage_lst = []
        self.name = name

        logger.debug("Init GroupContent")


class GroupWidget(QtWidgets.QWidget, Ui_GroupWidget):
    def __init__(self, group_c, number, parent_w):
        try:
            super(GroupWidget, self).__init__()
            self.setupUi(self)
            self.content = group_c
            self.number = number
            self.parent_w = parent_w
            self.lang_parser = self.parent_w.parent_w.lang_parser

            self.Group_name_edit.setText(self.content.name)
            # добавить стадии в комбобокс
            for stage in self.parent_w.stages:
                self.Group_stage_box.addItem(stage)

            # добавить стадии группы в список
            for stage in self.content.stage_lst:
                self.Group_stage_lst.addItem(stage)

            self.Del_group_btn.clicked.connect(self.del_group)
            self.Group_stage_add_btn.clicked.connect(self.add_stage)
            self.Group_stage_del_btn.clicked.connect(self.del_stage)

            self.set_text()

            logger.debug("Init GroupWidget")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def del_group(self):
        try:
            self.parent_w.del_group(self.number)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def add_stage(self):
        try:
            if self.Group_stage_box.currentText() != "":
                self.Group_stage_lst.addItem(self.Group_stage_box.currentText())
                self.content.stage_lst.append(self.Group_stage_box.currentText())
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def del_stage(self):
        try:
            if self.Group_stage_lst.currentItem() is not None:
                stage = self.Group_stage_lst.currentItem().text()
                self.content.stage_lst.pop(self.content.stage_lst.index(stage))
                self.Group_stage_lst.takeItem(self.Group_stage_lst.currentRow())
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_text(self):
        section = self.parent_w.parent_w.user_settings.language.upper()
        for widget in self.findChildren((QtWidgets.QLabel, QtWidgets.QPushButton)):
            widget.setText(self.lang_parser.get(section, widget.objectName(), fallback=widget.objectName()))
        self.Group_lbl.setText(self.Group_lbl.text().format(self.number + 1))

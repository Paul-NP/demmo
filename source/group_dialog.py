from source.ui_py.group_dialog_ui import Ui_GroupDialog
from source.group_widget import GroupWidget, GroupContent
from source.message import ErrorMessage
from PyQt5 import QtCore, QtWidgets, QtGui
import logging
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class GroupDialog(QtWidgets.QDialog, Ui_GroupDialog):
    def __init__(self, result_dic, groups, parent_w):
        try:
            super(GroupDialog, self).__init__()
            self.setupUi(self)
            self.parent_w = parent_w
            self.stages = []
            self.old_groups = list(groups)
            self.groups = list(groups)
            self.name_generator = self.parent_w.get_factor_name()

            self.set_text()
            self.update_btn_box()

            for st in result_dic:
                if st != "step":
                    self.stages.append(st)

            self.scroll_groups = QtWidgets.QScrollArea()
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.scroll_groups.setWidgetResizable(True)
            self.scroll_groups.setSizePolicy(sizePolicy)
            self.Group_dialog_layout.insertWidget(3, self.scroll_groups)
            self.scroll_groups_cont = QtWidgets.QWidget()
            self.groups_layout = QtWidgets.QVBoxLayout()
            self.scroll_groups_cont.setLayout(self.groups_layout)
            self.scroll_groups.setWidget(self.scroll_groups_cont)

            self.Group_dialog_add_group_btn.clicked.connect(self.add_group)

            self.update_groups()
            self.setWindowIcon(QtGui.QIcon(self.parent_w.deep_settings.window_icon_filename))

            logger.debug("Init GroupDialog")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def update_groups(self):
        self.parent_w.clear_widgets(self.groups_layout)
        for gr_i in range(len(self.groups)):
            self.groups_layout.insertWidget(gr_i, GroupWidget(self.groups[gr_i], gr_i, self))

    def add_group(self):
        try:
            self.update_info()
            self.groups.append(GroupContent(next(self.name_generator)))
            self.update_groups()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def del_group(self, group_num):
        try:
            self.update_info()
            self.groups.pop(group_num)
            self.update_groups()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def cancel(self):
        try:
            self.groups = list(self.old_groups)
            self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def apply(self):
        try:
            self.update_info()
            self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def update_btn_box(self):
        section = self.parent_w.user_settings.language.upper()
        self.Group_dialog_btn_box.clear()
        ok_text = self.parent_w.lang_parser.get(section, self.Group_dialog_btn_box.objectName() + "_ok",
                                                fallback=self.Group_dialog_btn_box.objectName() + "_ok")
        cancel_text = self.parent_w.lang_parser.get(section, self.Group_dialog_btn_box.objectName() + "_cancel",
                                                    fallback=self.Group_dialog_btn_box.objectName() + "_cancel")
        self.Group_dialog_btn_box.addButton(ok_text, QtWidgets.QDialogButtonBox.AcceptRole)
        self.Group_dialog_btn_box.addButton(cancel_text, QtWidgets.QDialogButtonBox.RejectRole)

        self.Group_dialog_btn_box.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Group_dialog_btn_box.rejected.connect(self.cancel)
        self.Group_dialog_btn_box.accepted.connect(self.apply)

    def update_info(self):
        for gr_i in range(len(self.groups)):
            self.groups[gr_i].name = self.groups_layout.itemAt(gr_i).widget().Group_name_edit.text()

    def set_text(self):
        section = self.parent_w.user_settings.language.upper()

        title_text = self.parent_w.lang_parser.get(section, "Groups_title", fallback="Groups_title")
        self.setWindowTitle(title_text)

        for widget in self.findChildren((QtWidgets.QLabel, QtWidgets.QPushButton)):
            # if self.parent_w.lang_parser.has_option(section, widget.objectName()):
            if isinstance(widget, (QtWidgets.QLabel, QtWidgets.QPushButton)):
                widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(),
                                                             fallback=widget.objectName()))

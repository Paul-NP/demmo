from source.ui_py.description_ui import Ui_DescriptionDialog
from source.message import ErrorMessage
from PyQt5 import QtCore, QtGui, QtWidgets
import logging
import traceback


logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class DescriptionDialog(QtWidgets.QDialog, Ui_DescriptionDialog):
    def __init__(self, description, parent_w):
        try:
            super(DescriptionDialog, self).__init__()
            self.setupUi(self)
            self.parent_w = parent_w
            self.content = description
            self.Decription_btn_box.rejected.connect(self.close)
            self.Decription_btn_box.accepted.connect(self.apply)
            self.update_btn_box()
            self.set_text()
            self.fill_boxes()
            self.setWindowIcon(QtGui.QIcon(self.parent_w.deep_settings.window_icon_filename))
            logger.debug("Init DescriptionDialog")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def fill_boxes(self):
        self.Description_edit.setText(self.content)

    def update_btn_box(self):
        section = self.parent_w.user_settings.language.upper()
        self.Decription_btn_box.clear()
        ok_text = self.parent_w.lang_parser.get(section, self.Decription_btn_box.objectName() + "_ok",
                                                fallback=self.Decription_btn_box.objectName() + "_ok")
        cancel_text = self.parent_w.lang_parser.get(section, self.Decription_btn_box.objectName() + "_cancel",
                                                    fallback=self.Decription_btn_box.objectName() + "_cancel")
        self.Decription_btn_box.addButton(ok_text, QtWidgets.QDialogButtonBox.AcceptRole)
        self.Decription_btn_box.addButton(cancel_text, QtWidgets.QDialogButtonBox.RejectRole)
        self.Decription_btn_box.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Decription_btn_box.rejected.connect(self.close)
        self.Decription_btn_box.accepted.connect(self.apply)

    def set_text(self):
        section = self.parent_w.user_settings.language.upper()

        title_text = self.parent_w.lang_parser.get(section, "Description_title", fallback="Description_title")
        self.setWindowTitle(title_text)

        for widget in self.findChildren(QtWidgets.QWidget):
            # if self.parent_w.lang_parser.has_option(section, widget.objectName()):
            if isinstance(widget, QtWidgets.QLabel):
                widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(),
                                                             fallback=widget.objectName()))

    def apply(self):
        try:
            self.content = self.Description_edit.toPlainText()
            self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

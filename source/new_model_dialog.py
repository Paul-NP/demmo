from source.ui_py.new_model_ui import Ui_NewModelDialog
from source.message import ErrorMessage
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class NewModelDialog(QtWidgets.QDialog, Ui_NewModelDialog):
    def __init__(self, parent_w):
        try:
            super(NewModelDialog, self).__init__(parent_w)
            self.setupUi(self)
            self.parent_w = parent_w
            self.set_text()
            self.update_btn_box()
            self.fill_boxes()
            self.center()
            self.setFixedSize(self.size())
            self.New_location_btn.clicked.connect(self.select_location)
            self.setWindowIcon(QtGui.QIcon(self.parent_w.deep_settings.window_icon_filename))
            logger.debug("Init NewModelDialog")
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def select_location(self):
        try:
            section = self.parent_w.user_settings.language.upper()
            location = QtWidgets.QFileDialog.getExistingDirectory(
                self, self.parent_w.lang_parser.get(section, "New_location_title", fallback="New_location_title"))
            if location != "":
                self.New_location_edit.setText(location + "/")
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def apply(self):
        try:
            self.parent_w.take_default()
            name = self.New_name_edit.text()
            location = self.New_location_edit.text()
            self.parent_w.create_new_model(name, location)
            self.parent_w.model_open = True
            self.parent_w.set_all_enabled(True)
            self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def fill_boxes(self):
        self.New_name_edit.setText(self.parent_w.deep_settings.default_model_name)
        self.New_location_edit.setText(self.parent_w.deep_settings.default_path)

    def update_btn_box(self):
        section = self.parent_w.user_settings.language.upper()
        self.New_btn_box.clear()
        ok_text = self.parent_w.lang_parser.get(section, self.New_btn_box.objectName() + "_ok",
                                                fallback=self.New_btn_box.objectName() + "_ok")
        load_text = self.parent_w.lang_parser.get(section, self.New_btn_box.objectName() + "_load",
                                                  fallback=self.New_btn_box.objectName() + "_load")
        load_btn = QtWidgets.QPushButton(load_text)
        cancel_text = self.parent_w.lang_parser.get(section, "Cancel", fallback="Cancel")
        self.New_btn_box.addButton(ok_text, QtWidgets.QDialogButtonBox.AcceptRole)
        self.New_btn_box.addButton(cancel_text, QtWidgets.QDialogButtonBox.RejectRole)
        self.New_btn_box.addButton(load_btn, QtWidgets.QDialogButtonBox.ActionRole)
        self.New_btn_box.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.New_btn_box.accepted.connect(self.apply)
        self.New_btn_box.rejected.connect(self.close)
        load_btn.clicked.connect(self.load_model)

    def load_model(self):
        try:
            self.parent_w.open_file_model()
            if self.parent_w.model_open:
                self.parent_w.set_all_enabled(True)
                self.close()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_text(self):
        section = self.parent_w.user_settings.language.upper()
        title_text = self.parent_w.lang_parser.get(section, "New_title", fallback="New_title")
        self.setWindowTitle(title_text)

        for widget in self.findChildren((QtWidgets.QLabel, QtWidgets.QPushButton)):
            # if self.parent_w.lang_parser.has_option(section, widget.objectName()):
            widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(), fallback=widget.objectName()))


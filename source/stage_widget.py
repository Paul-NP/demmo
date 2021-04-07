from source.ui_py.stage_ui import Ui_Stage
from source.message import ErrorMessage
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class StageWidget(QtWidgets.QWidget, Ui_Stage):
    def __init__(self, stage_c, number, parent_w):
        try:
            super(StageWidget, self).__init__()
            self.setupUi(self)
            self.number = number
            self.parent_w = parent_w

            self.Stage_name_edit.setText(stage_c.name)
            self.Stage_start_num_edit.setText(str(stage_c.start_num))
            self.Del_stage_btn.clicked.connect(self.delete)
            #self.Del_stage_btn.setIcon(QtGui.QIcon("icon/delete_icon_2.png"))
            #self.Del_stage_btn.setIconSize(QtCore.QSize(20, 20))

            self.set_text()

            logger.debug("Init StageWidget")

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
                widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(),
                                                             fallback=widget.objectName()))

        self.Stage_lbl.setText(self.Stage_lbl.text().format(str(self.number + 1)))

    def delete(self):
        try:
            self.parent_w.delete_stage(self.number)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)


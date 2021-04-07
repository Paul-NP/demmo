from source.ui_py.ow_flow_ui import Ui_Owflow
from source.message import ErrorMessage
from PyQt5 import QtWidgets
import logging
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class OWFlowWidget(QtWidgets.QWidget, Ui_Owflow):
    def __init__(self, owflow_c, number, parent_w):
        try:
            super(OWFlowWidget, self).__init__()
            self.setupUi(self)
            self.number = number
            self.parent_w = parent_w
            self.content = owflow_c

            self.Owflow_sfactor_value_edit.setText(str(self.content.sfactor))

            # добавить все возможные стадии в комбобоксы
            for stage in parent_w.list_stage:
                self.Owflow_stage_name_box.addItem(stage.name)

            # добавить все возможные динамические факторы в комбобоксы
            for factor in parent_w.list_dfactor:
                self.Owflow_dfactor_name_box.addItem(factor.name)

            # если контент потока знает конкретную стадию устанавливает её в соответствующем комбобоксе
            for st_i in range(len(parent_w.list_stage)):
                if parent_w.list_stage[st_i].name == self.content.stage:
                    self.Owflow_stage_name_box.setCurrentIndex(st_i)

            if self.content.dynamic:
                # если фатор должен быть динамическим
                # если контент потока знает конкретный динамический фактор увстнавливает его в соответствующем комбобоксе
                know = False
                for df_i in range(len(parent_w.list_dfactor)):
                    if parent_w.list_dfactor[df_i].name == self.content.dfactor:
                        self.Owflow_dfactor_name_box.setCurrentIndex(df_i)
                        know = True
                if not know:
                    self.content.dfactor = ""
            else:
                # если фатор должен быть статическим
                self.Owflow_sfactor_value_edit.setText(str(self.content.sfactor))

            # настройка кнопок
            self.Del_owflow_btn.clicked.connect(self.delete)
            #self.Del_owflow_btn.setIcon(QtGui.QIcon("icon/delete_icon_2.png"))

            # настройка галочки в соответствии с контентом
            self.Owflow_dfactor_cbox.stateChanged.connect(self.change_factor)
            self.Owflow_dfactor_cbox.setChecked(self.content.dynamic)

            self.change_factor()

            # настройка QRadioButton о относительности в соответствии с контентом
            if self.content.relativity == "stage":
                self.Owflow_relativity_stage_rbtn.setChecked(True)
            elif self.content.relativity == "common":
                self.Owflow_relativity_common_rbtn.setChecked(True)
            else:
                self.Owflow_absoluteness_rbtn.setChecked(True)

            # настройка QRadioButton о направлении в соответствии с контентом
            if self.content.direction:
                self.Owflow_direction_in_rbtn.setChecked(True)
            else:
                self.Owflow_direction_out_rbtn.setChecked(True)

            self.set_text()

            logger.debug("Init OWFlowWidget")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def delete(self):
        try:
            self.parent_w.delete_owflow(self.number)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def change_factor(self):
        try:
            if self.Owflow_dfactor_cbox.isChecked():
                self.Owflow_dfactor_name_lbl.setEnabled(True)
                self.Owflow_dfactor_name_box.setEnabled(True)
                self.Owflow_sfactor_value_lbl.setEnabled(False)
                self.Owflow_sfactor_value_edit.setEnabled(False)
            else:
                self.Owflow_dfactor_name_lbl.setEnabled(False)
                self.Owflow_dfactor_name_box.setEnabled(False)
                self.Owflow_sfactor_value_lbl.setEnabled(True)
                self.Owflow_sfactor_value_edit.setEnabled(True)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_text(self):
        section = self.parent_w.user_settings.language.upper()
        for widget in self.findChildren(QtWidgets.QWidget):
            if isinstance(widget, QtWidgets.QGroupBox):
                widget.setTitle(self.parent_w.lang_parser.get(section, widget.objectName(),
                                                              fallback=widget.objectName()))
            elif isinstance(widget, (QtWidgets.QPushButton, QtWidgets.QLabel, QtWidgets.QCheckBox,
                                     QtWidgets.QRadioButton)):
                widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(),
                                                             fallback=widget.objectName()))

        self.Owflow_lbl.setText(self.Owflow_lbl.text().format(str(self.number + 1)))
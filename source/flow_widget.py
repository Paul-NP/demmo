from source.ui_py.flow_ui import Ui_Flow
from source.message import ErrorMessage
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class FlowWidget(QtWidgets.QWidget, Ui_Flow):
    def __init__(self, flow_c, number, parent_w):
        try:
            super(FlowWidget, self).__init__()
            self.setupUi(self)
            self.number = number
            self.parent_w = parent_w
            self.content = flow_c

            # self.Flow_lbl.setText(self.Flow_label.text() + str(self.number + 1))

            # добавить все возможные стадии в комбобоксы
            for stage in parent_w.list_stage:
                self.Flow_source_name_box.addItem(stage.name)
                self.Flow_target_name_box.addItem(stage.name)
                self.Flow_istage_name_box.addItem(stage.name)

            # добавить все возможные факторы в комбокс
            for factor in parent_w.list_dfactor:
                self.Flow_dfactor_name_box.addItem(factor.name)

            # если контент потока знает конкретный источник устанавливает его в соответствующем комбобоксе
            for st_i in range(len(parent_w.list_stage)):
                if parent_w.list_stage[st_i].name == self.content.source:
                    self.Flow_source_name_box.setCurrentIndex(st_i)

            # устанавить галочку индуцированности в соответствии с контентом
            self.Flow_induction_cbox.setChecked(self.content.induction)
            self.change_induction()

            # устанавить галочку динамического фактора в соответствии с контентом
            self.Flow_dfactor_cbox.setChecked(self.content.dynamic)

            self.change_factor()

            if self.content.dynamic:
                # если фатор должен быть динамическим
                # если контент потока знает конкретный динамический фактор увстнавливает его в соответствующем комбобоксе
                know = False
                for df_i in range(len(parent_w.list_dfactor)):
                    if parent_w.list_dfactor[df_i].name == self.content.dfactor:
                        self.Flow_dfactor_name_box.setCurrentIndex(df_i)
                        know = True
                if not know:
                    self.content.dfactor = ""
            else:
                # если фатор должен быть статическим
                self.Flow_sfactor_value_edit.setText(str(self.content.sfactor))

            # добавить все известные контенту потока цели в виджет списка
            for tar in self.content.dic_target:
                self.Flow_target_lst.addItem("{0}: {1}".format(tar, self.content.dic_target[tar]))

            # добавить все известные контенту потока индуцирующие стадии в виджет списка
            for ind in self.content.dic_ind:
                self.Flow_istage_lst.addItem("{0}: {1}".format(ind, self.content.dic_ind[ind]))

            # настройка кнопок
            self.Del_flow_btn.clicked.connect(self.delete)
            # self.Del_flow_btn.setIcon(QtGui.QIcon("icon/delete_icon_2.png"))
            self.Flow_add_target_btn.clicked.connect(self.add_target)
            self.Flow_del_target_btn.clicked.connect(self.del_target)
            self.Flow_add_istage_btn.clicked.connect(self.add_ind_stage)
            self.Flow_del_istage_btn.clicked.connect(self.del_ind_stage)

            self.Flow_induction_cbox.stateChanged.connect(self.change_induction)
            self.Flow_dfactor_cbox.stateChanged.connect(self.change_factor)

            self.set_text()

            logger.debug("Init FlowWidget")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def delete(self):
        try:
            self.parent_w.delete_flow(self.number)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def add_target(self):
        try:
            if self.Flow_target_name_box.currentText() != "" and self.Flow_target_propab_edit.text() != "":
                if self.Flow_target_name_box.currentText() in self.content.dic_target:
                    for i in range(self.Flow_target_lst.count()):
                        if self.Flow_target_lst.item(i).text() == "{0}: {1}".format(
                                self.Flow_target_name_box.currentText(),
                                self.content.dic_target[self.Flow_target_name_box.currentText()]):
                            self.Flow_target_lst.item(i).setText("{0}: {1}".format(
                                self.Flow_target_name_box.currentText(), self.Flow_target_propab_edit.text()))
                else:
                    self.Flow_target_lst.addItem("{0}: {1}".format(self.Flow_target_name_box.currentText(),
                                                                   self.Flow_target_propab_edit.text()))
                self.content.dic_target[self.Flow_target_name_box.currentText()] = self.Flow_target_propab_edit.text()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def del_target(self):
        try:
            if self.Flow_target_lst.currentItem() is not None:
                target_name, _ = self.Flow_target_lst.currentItem().text().split(":")
                del self.content.dic_target[target_name]
                self.Flow_target_lst.takeItem(self.Flow_target_lst.currentRow())
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def add_ind_stage(self):
        try:
            if self.Flow_istage_name_box.currentText() != "" and self.Flow_istage_infect_edit.text() != "":
                if self.Flow_istage_name_box.currentText() in self.content.dic_ind:
                    for i in range(self.Flow_istage_lst.count()):
                        if self.Flow_istage_lst.item(i).text() == "{0}: {1}".format(
                                self.Flow_istage_name_box.currentText(),
                                self.content.dic_ind[self.Flow_istage_name_box.currentText()]):
                            self.Flow_istage_lst.item(i).setText("{0}: {1}".format(
                                self.Flow_istage_name_box.currentText(), self.Flow_istage_infect_edit.text()))
                else:
                    self.Flow_istage_lst.addItem("{0}: {1}".format(self.Flow_istage_name_box.currentText(),
                                                                   self.Flow_istage_infect_edit.text()))
                self.content.dic_ind[self.Flow_istage_name_box.currentText()] = self.Flow_istage_infect_edit.text()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def del_ind_stage(self):
        try:
            if self.Flow_istage_lst.currentItem() is not None:
                ind_stage_name, _ = self.Flow_istage_lst.currentItem().text().split(":")
                del self.content.dic_ind[ind_stage_name]
                self.Flow_istage_lst.takeItem(self.Flow_istage_lst.currentRow())
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def change_factor(self):
        try:
            if self.Flow_dfactor_cbox.isChecked():
                self.Flow_dfactor_name_lbl.setEnabled(True)
                self.Flow_dfactor_name_box.setEnabled(True)
                self.Flow_sfactor_value_lbl.setEnabled(False)
                self.Flow_sfactor_value_edit.setEnabled(False)
            else:
                self.Flow_dfactor_name_lbl.setEnabled(False)
                self.Flow_dfactor_name_box.setEnabled(False)
                self.Flow_sfactor_value_lbl.setEnabled(True)
                self.Flow_sfactor_value_edit.setEnabled(True)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def change_induction(self):
        try:
            if self.Flow_induction_cbox.isChecked():
                self.Flow_istage_lbl.setEnabled(True)
                self.Flow_istage_name_lbl.setEnabled(True)
                self.Flow_istage_name_box.setEnabled(True)
                self.Flow_istage_infect_lbl.setEnabled(True)
                self.Flow_istage_infect_edit.setEnabled(True)
                self.Flow_add_istage_btn.setEnabled(True)
                self.Flow_istage_lst.setEnabled(True)
                self.Flow_del_istage_btn.setEnabled(True)
            else:
                self.Flow_istage_lbl.setEnabled(False)
                self.Flow_istage_name_lbl.setEnabled(False)
                self.Flow_istage_name_box.setEnabled(False)
                self.Flow_istage_infect_lbl.setEnabled(False)
                self.Flow_istage_infect_edit.setEnabled(False)
                self.Flow_add_istage_btn.setEnabled(False)
                self.Flow_istage_lst.setEnabled(False)
                self.Flow_del_istage_btn.setEnabled(False)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

    def set_text(self):
        section = self.parent_w.user_settings.language.upper()
        for widget in self.findChildren(QtWidgets.QWidget):
            if isinstance(widget, (QtWidgets.QLabel, QtWidgets.QPushButton, QtWidgets.QCheckBox)):
                # if self.parent_w.lang_parser.has_option(section, widget.objectName()):
                widget.setText(self.parent_w.lang_parser.get(section, widget.objectName(),
                                                             fallback=widget.objectName()))

        self.Flow_lbl.setText(self.Flow_lbl.text().format(str(self.number + 1)))
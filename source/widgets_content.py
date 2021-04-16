from source.math_module import (DiseaseStage, Flow, ExternalFlow, Factor)
from os import path
from source.global_func import input_to_num, read_result_file, separate_path
import csv
import traceback
import logging
from source.message import ErrorMessage


logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class StageContent:
    def __init__(self, name, parent_w, start_num="0"):
        self.name = name
        self.start_num = start_num
        self.parent_w = parent_w

        logger.debug("Init StageContent")

    def get_stage(self, st_i):
        start_num = None
        info = []
        check = True
        DS = None
        try:
            start_num = input_to_num(self.start_num)
            if self.name == "":
                info.append(["Empty_stage_name", st_i, ""])
                check = False
                logger.warning("Empty stage name: {}".format(st_i))
            if start_num < 0:
                info.append(["Negative_start_num", st_i, ""])
                check = False
                logger.warning("Negative start num: {}".format(st_i))
            if isinstance(start_num, float):
                info.append(["Float_start_num", st_i, ""])
                check = False
                logger.warning("Float start num: {}".format(st_i))

        except ValueError:
            info.append(["Incorrect_entered_value", st_i, "Stage"])
            check = False
            logger.warning("Incorrect entered value stage {}".format(st_i))
        except Exception as e:
            msg = traceback.format_exc() + "Last element: {1} No.{0}"
            logger.error(msg.format(st_i, "Stage"))
            emsg = ErrorMessage(message=msg.format(st_i, "Stage"), parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)
        if check:
            DS = DiseaseStage(self.name, start_num)

        return [DS, check, info]


class FlowContent:
    def __init__(self, list_factor, parent_w, source="", sfactor="1", dfactor="",
                 dynamic=False, dic_target={}, induction=False, dic_ind={}):
        self.source = source
        self.sfactor = sfactor
        self.dfactor = dfactor
        self.dynamic = dynamic
        self.dic_target = dict(dic_target)
        self.induction = induction
        self.dic_ind = dict(dic_ind)
        self.list_factor = list_factor
        self.parent_w = parent_w

    def get_flow(self, fl_i):
        dic_target = {}
        dic_ind = {}
        factor = ""
        info = []
        check = True
        Fl = None
        try:
            sum_tar = 0
            if len(self.dic_target) == 0:
                info.append(["Empty_flow_target", fl_i, ""])
                logger.warning("Empty flow target: {}".format(fl_i))
                check = False
            else:
                for tar in self.dic_target:
                    try:
                        dic_target[tar] = input_to_num(self.dic_target[tar])
                        sum_tar += dic_target[tar]
                    except ValueError:
                        info.append(["Incorrect_flow_target", fl_i, tar])
                        logger.warning("Incorrect flow target: {0}, {1}".format(fl_i, tar))
                        check = False

                if sum_tar != 1:
                    info.append(["Sum_target_flow", fl_i, ""])
                    logger.warning("Sum target flow {}".format(fl_i))
                    check = False

            if self.induction:
                if len(self.dic_ind) == 0:
                    info.append(["Empty_flow_inducing", fl_i, ""])
                    logger.warning("Empty flow inducing {}".format(fl_i))
                    check = False
                else:
                    for st in self.dic_ind:
                        try:
                            dic_ind[st] = input_to_num(self.dic_ind[st])
                        except ValueError:
                            info.append(["Incorrect_ind_stage", fl_i, st])
                            logger.warning("Incorrect ind stage: {0}, {1}".format(fl_i, st))
                            check = False

            if self.dynamic:
                if self.dfactor == "":
                    info.append(["Empty_flow_dfactor", fl_i, ""])
                    logger.warning("Empty flow dfactor {}".format(fl_i))
                    check = False
                elif self.dfactor in [factor.name for factor in self.list_factor]:
                    i = 0
                    while self.list_factor[i].name != self.dfactor:
                        i += 1
                    factor, check_add, info_add = self.list_factor[i].get_factor()
                    if not check_add:
                        info += info_add
                        check = False
                else:
                    info.append(["Not_exist_dfactor_flow", fl_i, self.dfactor])
                    logger.warning("Not exist dfactor flow: {0}, {1}".format(fl_i, self.dfactor))
                    check = False

            else:
                if self.sfactor == "":
                    info.append(["Empty_flow_sfactor", fl_i, ""])
                    logger.warning("Empty flow sfactor {}".format(fl_i))
                    check = False
                else:
                    try:
                        factor = Factor(input_to_num(self.sfactor))
                        if factor.factor < 0:
                            info.append(["Negative_flow_sfactor", fl_i, ""])
                            logger.warning("Negative flow sfactor {}".format(fl_i))
                            check = False
                        elif factor.factor >= 1:
                            info.append(["Large_flow_sfactor", fl_i, ""])
                            logger.warning("Large flow sfactor {}".format(fl_i))
                            check = False
                    except ValueError:
                        info.append(["Incorrect_flow_sfactor", fl_i, ""])
                        logger.warning("Incorrect flow sfactor {}".format(fl_i))
                        check = False

        except Exception as e:
            msg = traceback.format_exc() + "Last element: {0} No.{1}"
            logger.error(msg.format("Flow", fl_i))
            emsg = ErrorMessage(message=msg.format("Flow", fl_i), parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

        if check:
            Fl = Flow(self.source, dic_target, factor, self.induction, dic_ind)

        return [Fl, check, info]


class OWFlowContent:
    def __init__(self, list_factor, parent_w, stage="", sfactor="1", dfactor="",
                 dynamic=False, direction=True, relativity="stage"):
        self.stage = stage
        self.sfactor = sfactor
        self.dfactor = dfactor
        self.dynamic = dynamic
        self.direction = direction
        self.relativity = relativity
        self.list_factor = list_factor
        self.parent_w = parent_w

    def get_ow_flow(self, owf_i):
        info = []
        check = True
        factor = ""
        Owfl = None
        try:
            if self.dynamic:
                if self.dfactor == "":
                    info.append(["Empty_owflow_dfactor", owf_i, ""])
                    logger.warning("Empty owflow dfactor {}".format(owf_i))
                    check = False
                elif self.dfactor in [factor.name for factor in self.list_factor]:
                    i = 0
                    while self.list_factor[i].name != self.dfactor:
                        i += 1

                    factor, check_add, info_add = self.list_factor[i].get_factor()
                    if not check_add:
                        info += info_add
                        check = False
                else:
                    info.append(["Not_exist_dfactor_owflow", owf_i, self.dfactor])
                    logger.warning("Not exist dfactor owflow {}".format(owf_i))
                    check = False
            else:
                if self.sfactor == "":
                    info.append(["Empty_owflow_sfactor", owf_i, ""])
                    logger.warning("Empty owflow sfactor {}".format(owf_i))
                    check = False
                else:
                    try:
                        factor = Factor(input_to_num(self.sfactor))
                        if factor.factor < 0:
                            info.append(["Negative_owflow_sfactor", owf_i, ""])
                            logger.warning("Negative owflow sfactor {}".format(owf_i))
                            check = False
                    except ValueError:
                        info.append(["Incorrect_owflow_sfactor", owf_i, ""])
                        logger.warning("Incorrect owflow sfactor {}".format(owf_i))
                        check = False

        except Exception as e:
            msg = traceback.format_exc() + "Last element: {0} No.{1}"
            logger.error(msg.format("OW_flow", owf_i))
            emsg = ErrorMessage(message=msg.format("OW_flow", owf_i), parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

        if check:
            Owfl = ExternalFlow(self.stage, factor, self.direction, self.relativity)

        return [Owfl, check, info]


class DFactorContent:
    def __init__(self, name, parent_w, dic_values={}):
        self.name = name
        self.parent_w = parent_w
        self.dic_values = dict(dic_values)

    def get_factor(self):
        value = []
        new_value = [[], []]
        info = []
        check = True
        Df = None

        for step in self.dic_values:
            value.append([step, self.dic_values[step]])

        try:
            for i in range(len(value)):
                step = input_to_num(value[i][0])
                step_val = input_to_num(value[i][1])
                if isinstance(step, float):
                    info.append(["Float_dfactor_step", self.name, ""])
                    logger.warning("Float dfactor step {}".format(self.name))
                    check = False
                if step_val < 0:
                    info.append(["Negative_dfactor_value", self.name, ""])
                    logger.warning("Negative dfactor value {}".format(self.name))
                    check = False

                value[i][0] = step
                value[i][1] = step_val

            if len(value) == 1:
                info.append(["Short_dfactor", self.name, ""])
                logger.warning("Short dfactor {}".format(self.name))
                check = False

            # добавление третьего значения
            elif len(value) == 2:
                if abs(value[1][0] - value[0][0]) > 1:
                    # добавить среднее
                    middle_step = int((value[1][0] + value[0][0]) / 2)
                    middle_val = ((value[1][1] + value[0][1]) / 2)
                    value.append([middle_step, middle_val])
                else:
                    # добавить идентичное справа
                    value.sort(key=lambda el: el[0])
                    value.append([value[1][0] + 1, value[1][1]])

            value.sort(key=lambda el: el[0])

            for el in value:
                new_value[0].append(el[0])
                new_value[1].append(el[1])

        except ValueError:
            info.append(["Incorrect_dfactor", self.name, ""])
            logger.warning("Incorrect dfactor".format(self.name))
            check = False

        except Exception as e:
            msg = traceback.format_exc() + "Last element: dfactor {0}"
            logger.error(msg.format(self.name))
            emsg = ErrorMessage(message=msg.format(self.name), parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

        if check:
            Df = Factor(new_value, dynamic=True)

        return [Df, check, info]


class Result:
    def __init__(self, filename, parent_w, delimiter=";", floating_point=",",
                 f_path="", show=False, groups=[], result_dic=None,
                 model_name="", file_model="", description="", model=None, info=""):
        self.delimiter = delimiter
        self.floating_point = floating_point
        self.show = show
        self.groups = groups
        self.model_name = model_name
        self.file_model = file_model
        self.description = description
        self.model = model
        self.info = info
        self.result_flows = None
        self.parent_w = parent_w
        self.correct = True

        if f_path == "":
            path_name = separate_path(filename)
            self.file_result = path_name[1]
            self.f_path = path_name[0]
        else:
            self.file_result = filename
            self.f_path = f_path

        if info == "":
            self.add_info()
        else:
            self.info = info

        if result_dic is not None:
            self.result_dic = result_dic
        elif model is not None:
            self.result_dic = model.result_model
            self.result_flows = model.result_flows
        else:
            self.read_result_dic()

    def write_result_flows(self):
        filename_flows = self.f_path + self.file_result[:-4] + "_flows.csv"
        file = open(filename_flows, "w", encoding="utf-8-sig", newline="")

        writer = csv.writer(file, delimiter=self.delimiter)
        writer.writerow(self.result_flows)

        for fl in self.result_flows:
            logger.debug("result_flows[{0}][:5]: {1}, len: {2}".format(fl, self.result_flows[fl][:5],
                                                                       len(self.result_flows[fl])))

        for step in range(len(self.result_flows["step"])):
            row = [str(self.result_flows[fl][step]).replace(".", self.floating_point)
                   for fl in self.result_flows]
            writer.writerow(row)
        file.close()

    def write_result(self):
        if self.result_flows is not None:
            self.write_result_flows()

        filename = self.f_path + self.file_result

        file = open(filename, "w", encoding="utf-8-sig", newline="")

        writer = csv.writer(file, delimiter=self.delimiter)
        writer.writerow(self.result_dic)

        for step in range(len(self.result_dic["step"])):
            row = [str(self.result_dic[st][step]).replace(".", self.floating_point)
                   for st in self.result_dic]
            writer.writerow(row)
        file.close()

    def write_info(self):
        filename = self.f_path + self.file_result
        with open(filename[:-4] + "_info.txt", "w", encoding="utf-8-sig") as file:
            file.write(self.info)

    def read_result_dic(self):
        try:
            with open(self.f_path + self.file_result, "r", encoding="utf-8-sig") as file:
                self.result_dic = {}
                reader = csv.reader(file, delimiter=self.delimiter)
                result_lst = []
                len_count = 0
                for row in reader:
                    result_lst.append(row)
                    len_count += 1
                if "step" in result_lst[0]:
                    for i in range(len(result_lst[0])):
                        self.result_dic[result_lst[0][i]] = []
                        for j in range(1, len_count):
                            self.result_dic[result_lst[0][i]].append(
                                float(result_lst[j][i].replace(self.floating_point, ".")))
                else:
                    raise ValueError
        except (ValueError, IndexError):
            logger.warning("Incorrect file result")
            filename = self.f_path + self.file_result
            info = ["Incorrect_file_result", filename, ""]
            msg = self.parent_w.get_message_text(info)
            self.parent_w.show_message(msg, "Error_title")
            self.correct = False

    def add_info(self):
        filename = self.f_path + self.file_result
        if path.exists(filename[:-4] + "_info.txt"):
            with open(filename[:-4] + "_info.txt", "r", encoding="utf-8-sig") as file:
                self.info = file.read()
        elif self.model is not None:
            self.create_info(self.model)
            if self.groups:
                self.add_group_info()

    def create_info(self, model):
        info = "Result filename: " + self.f_path + self.file_result + "\n"
        info += "Model filename: " + self.file_model + "\n"
        info += "Model name: " + self.model_name + "\n"
        info += "Description: " + self.description + "\n"
        info += "\nStages:\n"
        for st in model.stages:
            info += "{0} ({1}); ".format(st.name, str(st.num))
        info += "\nFlows:\n"
        for fl_i in range(len(model.flows)):
            info += "{} flow:\n".format(fl_i + 1)
            if model.flows[fl_i].factor.dynamic:
                factor = "dynamic"
            else:
                factor = model.flows[fl_i].factor.factor
            fstring = "{0} --({1})-".format(model.flows[fl_i].source, factor)
            for t in model.flows[fl_i].target:
                fstring += "-> ({0}%){1} ".format(int(model.flows[fl_i].target[t] * 100), t)
            fstring += "\n"
            if model.flows[fl_i].induction:
                fstring += "inducing by:"
                for i in model.flows[fl_i].inducing_stages:
                    fstring += " ({0}) {1};".format(model.flows[fl_i].inducing_stages[i], i)
                fstring += "\n"
            info += fstring
        if model.one_way_flows:
            info += "External flows:\n"
            for owf in model.one_way_flows:
                if owf.factor.dynamic:
                    factor = "dynamic"
                else:
                    factor = owf.factor.factor

                if owf.direction == 1:
                    dir = "--({0} | {1})-->"
                else:
                    dir = "<--({0} | {1})--"
                dir = dir.format(factor, owf.relativity)
                fstring = "{0} {1}\n".format(owf.stage, dir)
                info += fstring

        self.info = info

    def create_group_result(self):
        group_result_dic = {"step": []}
        for gr in self.groups:
            group_result_dic[gr.name] = []

        for step in self.result_dic["step"]:
            group_result_dic["step"].append(int(step))
            for gr in self.groups:
                value = 0
                for st in gr.stage_lst:
                    value += self.result_dic[st][int(step)]
                group_result_dic[gr.name].append(value)

        return group_result_dic

    def add_group_info(self, suffix):
        self.info += "Groups: " + self.f_path + self.file_result[:-4] + suffix + "\n"
        for gr in self.groups:
            self.info += gr.name + ": "
            for st in gr.stage_lst:
                self.info += st + "; "
            self.info += "\n"
        self.write_info()

    def add_group_info_old(self):
        self.info += "Groups:\n"
        for gr in self.groups:
            self.info += gr.name + ": "
            for st in gr.stage_lst:
                self.info += st + "; "
            self.info += "\n"

        self.write_info()

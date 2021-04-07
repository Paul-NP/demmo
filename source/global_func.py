import csv
from os import path
import logging

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


def get_info_model(result_name, name, filename, description, model):
    info = result_name + "\n"
    info += "Model filename: " + filename + "\n"
    info += "Model name: " + name + "\n"
    info += "Description: " + description + "\n"
    info += "Stages:\n"
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
        info += "Unidirectional flows:\n"
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
    return info


def add_group_info(groups):
    info = "\nGroups:\n"
    for gr in groups:
        info += gr.name + ": "
        for st in gr.stage_lst:
            info += st + "; "
        info += "\n"
    return info


def input_to_num(string):
    if isinstance(string, str):
        rez_string = string.strip()
        rez_string = rez_string.replace(",", ".")
        if "." in rez_string:
            return float(rez_string)
        else:
            return int(rez_string)


def read_result_file(filename, delimiter=",", floating_point=","):
    with open(filename, "r", encoding="utf-8-sig") as file:
        result_dic = {}

        reader = csv.reader(file, delimiter=delimiter)
        result_lst = []
        len_count = 0
        for row in reader:
            result_lst.append(row)
            len_count += 1
        for i in range(len(result_lst[0])):
            result_dic[result_lst[0][i]] = []
            for j in range(1, len_count):
                result_dic[result_lst[0][i]].append(float(result_lst[j][i].replace(floating_point, ".")))

        return result_dic


def separate_path(file_path):
    filename = path.basename(file_path)
    f_path = file_path[:-len(filename)]
    return [f_path, filename]

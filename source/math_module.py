from os import path
import numpy as np
from scipy import interpolate
import csv
import logging
from random import random
import json

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


def get_filename():
    file_id = 1
    file_mask = "result/Test_result_{}.csv"
    filename = file_mask.format(str(file_id))
    while path.exists(filename):
        file_id += 1
        filename = file_mask.format(str(file_id))
    return filename


class DiseaseStage:
    def __init__(self, name, num):
        self.name = name
        self.num = num

        logger.debug("Init DiseaseStage")

    def __repr__(self):
        return "DiseaseStage: {0} ({1})".format(self.name, self.num)

    def get_to_file(self):
        return {"name": self.name, "start_num": str(self.num)}


class Flow:
    def __init__(self, source, target, factor, induction=False, inducing_stages={}):
        """
        :param source: string, name of source stage
        :param target: dictionary, {target: probability}
        :param factor: Factor
        :param induction: bool
        :param inducing_stages: dictionary, {name: infectiousness}
        """
        self.source = source
        self.target = target
        self.factor = factor
        self.induction = induction
        if induction:
            self.inducing_stages = inducing_stages

        logger.debug("Init Flow")

    def get_to_file(self):
        to_file_dic = {"source": self.source, "dfactor": "", "induction": self.induction}
        if self.factor.dynamic:
            to_file_dic["sfactor"] = ""
            to_file_dic["dynamic"] = True
        else:
            to_file_dic["sfactor"] = str(self.factor.factor)
            to_file_dic["dynamic"] = False
        dit_target = {}
        for t in self.target:
            dit_target[t] = str(self.target[t])
        to_file_dic["dic_target"] = dit_target
        dic_ind = {}
        if self.induction:
            for i_s in self.inducing_stages:
                dic_ind[i_s] = str(self.inducing_stages[i_s])
        to_file_dic["dic_ind"] = dic_ind

        return to_file_dic

    def get_target_propab(self, model_state, population_size, step, divided_n):
        flow = self.factor.get_factor(step)
        if self.induction:
            ind_flow = 0
            for i_stage in self.inducing_stages:
                ind_flow += self.inducing_stages[i_stage] * model_state[i_stage]
            flow *= ind_flow
            if divided_n:
                flow /= population_size
        target_propab = {}
        for t in self.target:
            target_propab[t] = self.target[t] * flow
        return target_propab

    def get_flow(self, model_state, population_size, step, divided_n):
        """
        Calculate the flow value given the state of the model
        :param model_state: dictionary
        :return: int
        """
        flow = model_state[self.source]
        if self.induction:
            ind_flow = 0
            for i_stage in self.inducing_stages:
                ind_flow += self.inducing_stages[i_stage] * model_state[i_stage]
            flow *= ind_flow
            if divided_n:
                flow /= population_size
        flow *= self.factor.get_factor(step)
        return flow

    def get_change(self, model_state, population_size, step, divided_n):
        """
        Returns the change value given the state of the model
        :param model_state: dictionary, {name: num}
        :return: dictionary, {stage: flow}
        """

        flow = self.get_flow(model_state, population_size, step, divided_n)
        changes = {self.source: -flow}
        for t in self.target:
            changes[t] = flow * self.target[t]
        return [changes, flow]

    def __repr__(self):
        present = "Flow: ({f}) {s} -> ".format(f=str(self.factor), s=self.source)
        for t in self.target:
            #present += t + ", "
            present += "{0} ({1}), ".format(t, self.target[t])
        if self.induction:
            present += "inducing by: "
            for ist in self.inducing_stages:
                present += ist + ", "
            present = present[:-2] + "."
        else:
            present += "not inducing."

        return present


class ExternalFlow:
    def __init__(self, stage, factor, direction, relativity):
        """
        :param stage: string, name stage
        :param factor: float, coefficient of this flow
        :param direction: bool, True for input flow, False for output flow
        """
        self.stage = stage
        self.factor = factor
        self.relativity = relativity
        self.direction = 1 if direction else -1

        logger.debug("Init ExternalFlow")

    def get_to_file(self):
        # не сделал
        return {}

    def get_change(self, model_state, population_size, step):
        """
        :param model_state: dictionary, {name: num}
        :return: int, one way flow for current stage
        """
        flow = self.factor.get_factor(step) * self.direction
        if self.relativity == "stage":
            flow *= model_state[self.stage]
        elif self.relativity == "common":
            flow *= population_size

        if flow + model_state[self.stage] < 0:
            return "to_zero"
        else:
            return flow

    def __repr__(self):
        present = "Ex_flow: stage: {0}, d: {1}, f: {2}".format(self.stage, str(self.factor), str(self.direction))
        return present


class EpidemicModel:
    def __init__(self, stages, flows, one_way_flows=[], settings="default", stop_mode="a"):
        """
        :param settings dictionary, {check_period: int, braking_dis: int, threshold: float}
        :param stages: list(DiseaseStage)
        :param flows: list(Flow)
        :param one_way_flows: list(ExternalFlow)
        """
        self.stages = stages
        self.flows = flows
        self.one_way_flows = one_way_flows
        self.model_state = {}
        self.model_run = True
        self.braking_rule = True
        self.result_model = {}
        self.result_flows = {}
        self.step = 0
        self.population = None
        # default settings
        self.stop_mode = "a"
        self.check_period = 100
        self.braking_dist = 20
        self.threshold = 0.0001
        self.limit_step = 1000
        self.max_step = 10000
        self.divided_n = True
        # modeling method: math or imitation
        self.method = "math"

        if settings != "default":
            self.stop_mode = settings["stop_mode"]
            self.check_period = settings["check_period"]
            self.braking_dist = settings["braking_dist"]
            self.threshold = settings["threshold"]
            self.limit_step = settings["limit_step"]
            self.max_step = settings["max_step"]
            self.divided_n = settings["divided_n"]
            if "method" in settings:
                self.method = settings["method"]

        for st in stages:
            self.model_state[st.name] = st.num
        self.population_size = sum(self.model_state[st] for st in self.model_state)

        logger.debug("Init EpidemicModel")

    def check_stop(self, new_state):
        """
        Decides to stop modeling at the current step
        :param step: int
        :param new_state: dictionary, model_state after change from all flows
        :return: bool
        """
        if self.stop_mode == "a":
            if self.step == self.max_step:
                return False
            elif self.step > self.check_period:
                if self.step % self.check_period < self.braking_dist:
                    change = all(abs(self.model_state[st] - new_state[st]) / self.population_size < self.threshold
                                 for st in self.model_state)

                    self.braking_rule *= change
                    return True
                elif self.step % self.check_period == self.braking_dist:
                    if self.braking_rule:
                        return False
                    else:
                        self.braking_rule = True
                        return True

                else:
                    return True
            else:
                return True
        elif self.stop_mode == "m":
            if self.step == self.limit_step:
                return False
            else:
                return True

    def model_step(self):
        """
        Change model state after one step
        :return: None
        """
        new_state = dict(self.model_state)
        self.population_size = sum(self.model_state[st] for st in self.model_state)
        for fl in self.flows:
            change, fl_value = fl.get_change(self.model_state, self.population_size, self.step, self.divided_n)
            self.result_flows[str(fl)].append(fl_value)
            for st in change:
                new_state[st] += change[st]
        for o_w_fl in self.one_way_flows:
            change = o_w_fl.get_change(self.model_state, self.population_size, self.step)
            if change == "to_zero":
                new_state[o_w_fl.stage] = 0
            else:
                new_state[o_w_fl.stage] += change
        # self.model_state = new_state
        return new_state

    def start_model(self):
        """
        Starts simulation before the stop rule occurs
        :param output_file: file to write result of modeling
        :return:
        """
        # запись заголовков в словарь
        self.result_model["step"] = []
        self.result_flows["step"] = []
        for st in self.model_state:
            self.result_model[st] = []

        for fl in self.flows:
            self.result_flows[str(fl)] = []

        if self.method == "math":
            self.run_math_model()
        elif self.method == "imitation":
            self.run_imit_model()

    def run_imit_model(self):
        self.step = 0
        # создание и заполнение массива индивидов
        self.population = np.zeros(self.population_size, dtype=int)
        self.stage_id = {}
        pop_index = 0
        for st_i in range(len(self.stages)):
            self.stage_id[self.stages[st_i].name] = st_i
            for i in range(pop_index, pop_index + self.stages[st_i].num):
                pop_index = i
                self.population[pop_index] = st_i
            pop_index += 1

        while self.model_run:
            new_state = self.imitation_step()
            self.model_run = self.check_stop(new_state)

            # заполнение словаря
            self.result_model["step"].append(self.step)
            self.result_flows["step"].append(self.step)
            for st in self.model_state:
                self.result_model[st].append(self.model_state[st])

            self.model_state = new_state
            self.step += 1

    def imitation_step(self):
        new_state = dict(self.model_state)
        for st in new_state:
            new_state[st] = 0

        self.population_size = sum(self.model_state[st] for st in self.model_state)

        transition_propab = {}
        for st in self.stages:
            transition_propab[st.name] = {}
            for fl in self.flows:
                if fl.source == st.name:
                    propabs = fl.get_target_propab(self.model_state, self.population_size, self.step, self.divided_n)
                    transition_propab[st.name].update(propabs)

        print(transition_propab)

        for ind_i in self.population:
            change = False
            #print("I am ind[{0}], I in {1}-{2}".format(ind_i, self.population[ind_i],
            #                                           self.stages[self.population[ind_i]].name))
            for target in transition_propab[self.stages[self.population[ind_i]].name]:

                if random() < transition_propab[self.stages[self.population[ind_i]].name][target] and not change:
                    self.population[ind_i] = self.stage_id[target]
                    change = True

            #print("After I am ind[{0}], I in {1}-{2}".format(ind_i, self.population[ind_i],
            #                                           self.stages[self.population[ind_i]].name))

            new_state[self.stages[self.population[ind_i]].name] += 1
        print(new_state)
        return new_state

    def run_math_model(self):
        self.step = 0
        while self.model_run:
            new_state = self.model_step()
            self.model_run = self.check_stop(new_state)

            # заполнение словаря
            self.result_model["step"].append(self.step)
            self.result_flows["step"].append(self.step)
            for st in self.model_state:
                self.result_model[st].append(self.model_state[st])

            self.model_state = new_state
            self.step += 1

        #print(self.result_flows)

    def write_result_file(self, filename, delimiter=",", floating_point=","):
        file = open(filename, "w", encoding="utf-8-sig", newline="")

        writer = csv.writer(file, delimiter=delimiter)
        writer.writerow(self.result_model)

        for step in range(len(self.result_model["step"])):
            row = [str(self.result_model[st][step]).replace(".", floating_point) for st in self.result_model]
            writer.writerow(row)

        file.close()

    def get_settings(self):
        settings_dic = {"check_period": str(self.check_period), "braking_dist": str(self.braking_dist),
                        "threshold": str(self.threshold), "limit_step": str(self.limit_step),
                        "max_step": str(self.max_step), "stop_mode": str(self.stop_mode),
                        "divided_n": str(self.divided_n)}
        return settings_dic

    def create_model_file(self, model_name: str, description: str = ""):
        common_dic = {"Model_name": model_name, "Description": description,
                      "Stages": [], "Flows": [], "Ow_flows": [], "Dfactors": [],
                      "Settings": self.get_settings(), "Associated result files": []}

        for st in self.stages:
            common_dic["Stages"].append(st.get_to_file())

        for fl in self.flows:
            common_dic["Flows"].append(fl.get_to_file())

        for ow_fl in self.one_way_flows:
            common_dic["Ow_flows"].append(ow_fl.get_to_file())

        with open(model_name + "_model.ecm", "w", encoding="utf-8-sig") as file:
            json.dump(common_dic, file, indent=4)

    def __repr__(self):
        present = "EpidemicModel:\nStages:\n"
        for s in self.stages:
            present += str(s) + "\n"
        present += "Flows:\n"
        for fl in self.flows:
            present += str(fl) + "\n"
        if self.one_way_flows:
            present += "Owflows:\n"
            for owfl in self.one_way_flows:
                present += str(owfl) + "\n"

        return present


class Factor:
    def __init__(self, value, dynamic=False):
        self.dynamic = dynamic
        if self.dynamic:
            x_values = value[0]
            y_values = value[1]
            self.factor = DynamicFactor(x_values, y_values)
        else:
            self.factor = value

        logger.debug("Init Factor")

    def get_to_file(self):
        # не сделал
        return {}

    def get_factor(self, x):
        if self.dynamic:
            return self.factor.get_factor(x)
        else:
            return self.factor

    def __repr__(self):
        if self.dynamic:
            return "dynamic"
        else:
            return str(self.factor)


class DynamicFactor:
    def __init__(self, x_values, y_values):
        keys_x = np.array(x_values, dtype=int)
        keys_y = np.array(y_values)
        self.offset = x_values[0]
        len_range = keys_x[-1] - keys_x[0] + 1
        self.values = np.zeros(len_range)
        func = interpolate.interp1d(keys_x, keys_y, kind="linear")
        for i in range(len_range):
            self.values[i] = func(i + self.offset)

        logger.debug("Init DynamicFactor")

    def get_factor(self, x):
        if x < self.offset:
            return self.values[0]
        elif x > len(self.values) - 1 + self.offset:
            return self.values[-1]
        else:
            return self.values[x - self.offset]

    def get_values_range(self, left, right):
        values = [[], []]
        for i in range(left, right + 1):
            values[0].append(i)
            values[1].append(self.get_factor(i))
        return values

    @staticmethod
    def take_file(filename, head=False, delimiter=","):
        file = open(filename, "r", encoding="utf-8-sig")
        if head:
            file.readline()
        reader = csv.reader(file, delimiter=delimiter)
        x = []
        y = []
        for row in reader:
            x.append(int(row[0]))
            y.append(float(row[1].replace(",", ".")))
        x = np.array(x, dtype=int)
        y = np.array(y, dtype=float)
        file.close()
        return x, y


if __name__ == "__main__":
    from settings import Settings
    S = DiseaseStage("susceptible", 100)
    I = DiseaseStage("infectious", 2)
    R = DiseaseStage("recovered", 0)
    stages = [S, I, R]

    #x, y = DynamicFactor.take_file("test_csv.csv", delimiter=",")
    #SI_f_value = [x, y]

    #SI_f = Factor(SI_f_value, dynamic=True)
    SI_f = Factor(0.002)
    IR_f = Factor(0.01)
    # IS_f = Factor(0.01)
    SI = Flow("susceptible", {"infectious": 1}, SI_f, induction=True, inducing_stages={"infectious": 1})
    IR = Flow("infectious", {"recovered": 1}, IR_f)
    # IR = Flow("infectious", {"recovered": 1}, IR_f)
    flows = [SI, IR]

    #inpSf = Factor(0.0001)
    #otpIf = Factor(0.01)
    # ExternalFlow()
    #inpS = ExternalFlow("susceptible", inpSf, True)
    #otpI = ExternalFlow("infectious", otpIf, False)
    #owflows = [inpS, otpI]
    owflows = []

    settings = dict(vars(Settings()))
    settings["divided_n"] = False
    settings["method"] = "imitation"

    Model = EpidemicModel(stages, flows, owflows, stop_mode="m", settings=settings)
    filename = "test_imitation.csv"

    Model.start_model()
    Model.write_result_file(filename, delimiter=";", floating_point=".")

    input("end")

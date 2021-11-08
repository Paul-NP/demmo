from itertools import product
from source.math_module import Flow, DiseaseStage, EpidemicModel, Factor
from source.group_widget import GroupContent
from source.widgets_content import Result


def get_strains_model(factors: list, start_num: list, total_num: int, model_type: str = "SIR"):
    if not model_type.upper() in ("SIR", "SEIR", "SIRD", "SIRS", "SIRDS"):
        raise ValueError("Unknown model type")
    if not isinstance(factors, list):
        raise ValueError("Invalid argument factors")
    elif len(factors) < 1:
        raise ValueError("Short list factors")

    num_strains = len(factors)

    # добавление всех вариантов имён стадий здоровых
    stage_names = list(map(lambda x: "".join(x), product(["S", "R"], repeat=num_strains)))

    # добавление всех вариантов имён стадий болеющих
    for i in range(num_strains):
        raw_names = list(map(lambda x: "".join(x), product(["S", "R"], repeat=num_strains - 1)))
        names = []
        if model_type in ("SIR", "SIRD", "SIRS", "SIRDS"):
            for rn in raw_names:
                names.append(rn[:i] + "I" + rn[i:])
        elif model_type == "SEIR":
            for rn in raw_names:
                names.append(rn[:i] + "I" + rn[i:])
                names.append(rn[:i] + "E" + rn[i:])
        stage_names += names

    # добавление имени стадии смерти
    if model_type in ("SIRD", "SIRDS"):
        stage_names.append("D"*num_strains)

    # добавление всех стадий с количествами
    stages = []
    for name in stage_names:
        if "I" in name and "R" not in name and "E" not in name:
            stages.append(DiseaseStage(name, start_num[name.index("I")]))
        elif name != "S" * num_strains:
            stages.append(DiseaseStage(name, 0))
        else:
            stages.append(DiseaseStage(name, total_num - sum(start_num)))
    # добавление потоков
    flows = []
    if model_type == "SIR":
        for name in stage_names:
            if "I" in name:
                flows.append(Flow(name, {name.replace("I", "R"): 1}, Factor(factors[name.index("I")][1]), False))
            else:
                for i in range(len(name)):
                    if name[i] == "S":
                        inducing = {}
                        for i_st in stage_names:
                            if i_st[i] == "I":
                                inducing[i_st] = 1
                        flows.append(
                            Flow(name, {name[:i] + "I" + name[i + 1:]: 1}, Factor(factors[i][0]), True, inducing))

    elif model_type == "SEIR":
        for name in stage_names:
            if "I" in name:
                flows.append(Flow(name, {name.replace("I", "R"): 1}, Factor(factors[name.index("I")][2]), False))
                flows.append(Flow(name.replace("I", "E"), {name: 1}, Factor(factors[name.index("I")][1]), False))
            elif "E" not in name:
                for i in range(len(name)):
                    if name[i] == "S":
                        inducing = {}
                        for i_st in stage_names:
                            if i_st[i] == "I":
                                inducing[i_st] = 1
                        flows.append(Flow(name, {name[:i] + "E" + name[i + 1:]: 1}, Factor(factors[i][0]), True, inducing))

    elif model_type == "SIRD":
        for name in stage_names:
            if "I" in name:
                flows.append(Flow(name, {name.replace("I", "R"): 1 - factors[name.index("I")][2],
                                         "D"*num_strains: factors[name.index("I")][2]},
                                  Factor(factors[name.index("I")][1]), False))
            else:
                for i in range(len(name)):
                    if name[i] == "S":
                        inducing = {}
                        for i_st in stage_names:
                            if i_st[i] == "I":
                                inducing[i_st] = 1
                        flows.append(
                            Flow(name, {name[:i] + "I" + name[i + 1:]: 1}, Factor(factors[i][0]), True, inducing))

    elif model_type == "SIRS":
        for name in stage_names:
            if "I" in name:
                flows.append(Flow(name, {name.replace("I", "R"): 1}, Factor(factors[name.index("I")][1]), False))
            else:
                for i in range(len(name)):
                    if name[i] == "S":
                        inducing = {}
                        for i_st in stage_names:
                            if i_st[i] == "I":
                                inducing[i_st] = 1
                        flows.append(Flow(name, {name[:i] + "I" + name[i + 1:]: 1}, Factor(factors[i][0]), True, inducing))
            if "R" in name and "I" not in name:
                # предполагаю, что потеря иммунетета не может произойти во время любого штамма
                for i in range(len(name)):
                    if name[i] == "R":
                        new_name = name[:i] + "S" + name[i+1:]
                        flows.append(Flow(name, {new_name: 1}, Factor(factors[i][2]), False))

    elif model_type == "SIRDS":
        for name in stage_names:
            if "I" in name:
                flows.append(Flow(name, {name.replace("I", "R"): 1 - factors[name.index("I")][2],
                                         "D" * num_strains: factors[name.index("I")][2]},
                                  Factor(factors[name.index("I")][1]), False))
            else:
                for i in range(len(name)):
                    if name[i] == "S":
                        inducing = {}
                        for i_st in stage_names:
                            if i_st[i] == "I":
                                inducing[i_st] = 1
                        flows.append(Flow(name, {name[:i] + "I" + name[i + 1:]: 1}, Factor(factors[i][0]), True, inducing))
            if "R" in name and "I" not in name:
                # предполагаю, что потеря иммунетета не может произойти во время любого штамма
                for i in range(len(name)):
                    if name[i] == "R":
                        new_name = name[:i] + "S" + name[i+1:]
                        flows.append(Flow(name, {new_name: 1}, Factor(factors[i][3]), False))

    # вывод получившихся стадий и потоков
    print("Stages:\n", stages)
    print("Flows:")
    for f in flows:
        print(f)

    return EpidemicModel(stages, flows)


def get_groups(num_strains: int, model_type: str = "SIR"):
    # добавление всех вариантов имён стадий здоровых
    stage_names = list(map(lambda x: "".join(x), product(["S", "R"], repeat=num_strains)))

    # добавление всех вариантов имён стадий болеющих
    for i in range(num_strains):
        raw_names = list(map(lambda x: "".join(x), product(["S", "R"], repeat=num_strains - 1)))
        names = []
        if model_type in ("SIR", "SIRD", "SIRS", "SIRDS"):
            for rn in raw_names:
                names.append(rn[:i] + "I" + rn[i:])
        elif model_type == "SEIR":
            for rn in raw_names:
                names.append(rn[:i] + "I" + rn[i:])
                names.append(rn[:i] + "E" + rn[i:])
        stage_names += names

    # добавление имени стадии смерти
    if model_type in ("SIRD", "SIRDS"):
        stage_names.append("D"*num_strains)

    groups_dic = {}
    for i in range(num_strains):
        groups_dic["I{}".format(i+1)] = []
        for name in stage_names:
            if name[i] == "I":
                groups_dic["I{}".format(i + 1)].append(name)

    groups_dic["health"] = []
    for name in stage_names:
        if "I" not in name:
            groups_dic["health"].append(name)
    if model_type in ("SIRD", "SIRDS"):
        groups_dic["D"] = ["D"*num_strains]

    groups = []
    for gd in groups_dic:
        groups.append(GroupContent(gd))
        groups[-1].stage_lst = groups_dic[gd]

    return groups


def main():
    strains_model = get_strains_model([(0.2, 0.1, 0.015, 0.003), (0.5, 0.1, 0.02, 0.003)], [1, 1], 1000, "SIRDS")
    strains_model.stop_mode = "m"
    strains_model.limit_step = 2000
    strains_model.create_model_file("SIRDS")
    strains_model.start_model()
    filename = "SIRDS_two_strains"
    print("created model")
    groups = get_groups(2, "SIRDS")
    print("created groups")
    result = Result(filename + ".csv", None, model=strains_model, groups=groups)
    print("created Result")
    result.write_result()
    print("writed result")
    group_result_dic = result.create_group_result()
    group_result = Result(filename + "_gr.csv", None, result_dic=group_result_dic)
    group_result.write_result()


if __name__ == "__main__":
    main()


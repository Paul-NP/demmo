import csv
import math

from import_modules import EpidemicModel, DynamicFactor, Factor, DiseaseStage, Flow


def own_set(sequence) -> tuple:
    result = []
    for item in sequence:
        if not item in result:
            result.append(item)

    return tuple(result)


def find_point_come_back(model_type: str):
    if "R" in model_type:
        return model_type.index("R")
    else:
        return model_type.index("I")


def get_area_model(name_areas, start_nums, factors_areas, model_factors,
                   model_type="SIR", death_rate: float = 0.0) -> EpidemicModel:
    stages = []
    flows = []

    infect_direct = None
    come_back = model_type[-1] == "S"
    seq_len = len(model_type) - 1 if come_back else len(model_type)
    point_come_back = 0
    if come_back:
        point_come_back = find_point_come_back(model_type)

    for area_i in range(len(name_areas)):
        area_stages = []
        area_flows = []

        size_area = sum(start_nums[area_i])

        for st_i in range(seq_len):
            stage_name = f"{name_areas[area_i]}_{model_type[st_i]}"
            stage_num = start_nums[area_i][st_i]
            stage = DiseaseStage(stage_name, stage_num)
            area_stages.append(stage)

        inducing_stages = {f"{name_areas[j]}_I": factors_areas[area_i][j] for j in range(len(name_areas))}

        infect_flow = Flow(area_stages[0].name, {area_stages[1].name: 1}, model_factors[0], True, inducing_stages)
        area_flows.append(infect_flow)
        shift = 0
        for st_i in range(2, seq_len):
            if area_stages[st_i].name == f"{name_areas[area_i]}_D":
                prev_key = list(area_flows[-1].target.keys())[0]
                area_flows[-1].target = {prev_key: 1 - death_rate, f"{name_areas[area_i]}_D": death_rate}
                shift = 1
            else:
                flow = Flow(area_stages[st_i - 1].name, {area_stages[st_i].name: 1}, model_factors[st_i - 1 - shift],
                            induction=False)
                area_flows.append(flow)

        if come_back:
            flow = Flow(area_stages[point_come_back].name, {area_stages[0].name: 1}, model_factors[-1], induction=False)
            area_flows.append(flow)

        stages.extend(area_stages)
        flows.extend(area_flows)

    model = EpidemicModel(stages, flows)
    return model


def get_factor_from_file(filename, val_correction=1.0, time_correction=1.0, floating_point=".", delimiter=","):
    x_values = []
    y_values = []
    with open(filename, "r", encoding="utf-8-sig") as file:
        csv_reader = csv.reader(file, delimiter=delimiter)
        for row in csv_reader:
            first = int(row[0])
            if floating_point != ".":
                second = float(row[1].replace(floating_point, "."))
            else:
                second = float(row[1])
            x_values.append(math.ceil(first * time_correction))
            y_values.append(second * val_correction)
    print(filename, x_values, y_values)
    return Factor((x_values, y_values), dynamic=True)


def experiment_1(filename):
    cf = 1 / 102000  # city_factor
    vf = 1.17 / 12000  # vahta_factor
    time_correct = 1

    beta = 0.12
    gama = 0.1

    hf = get_factor_from_file("fh.csv", val_correction=cf, time_correction=time_correct, delimiter=";")
    wf = get_factor_from_file("fw.csv", val_correction=vf, time_correction=time_correct, delimiter=";")

    # c1, w1, c2, w2, wp

    start_nums = [[99990, 10, 0, 0], [2000, 0, 0, 0], [100000, 0, 0, 0], [2000, 0, 0, 0], [10000, 0, 0, 0]]
    c1_af = [cf, hf, 0, 0, 0]
    w1_af = [hf, wf, 0, wf, wf]
    c2_af = [0, 0, cf, hf, 0]
    w2_af = [0, wf, hf, wf, wf]
    wp_af = [0, wf, 0, wf, vf]

    area_factors = [c1_af, w1_af, c2_af, w2_af, wp_af]
    epid_factors = [Factor(beta), Factor(gama)]
    vahta_model = get_area_model(["c1", "w1", "c2", "w2", "wp"],
                                 start_nums, area_factors, epid_factors, "SIRD", death_rate=0.2)
    vahta_model.stop_mode = "m"
    vahta_model.limit_step = 1100
    vahta_model.divided_n = False

    vahta_model.start_model()

    vahta_model.write_result_file(filename, delimiter=";")


def experiment_2(filename):
    cf = 1 / 102000  # city_factor
    vf = 1.17 / 12000  # vahta_factor
    time_correct = 1

    beta = 0.12
    gama = 0.1

    hf = get_factor_from_file("fh.csv", val_correction=cf, time_correction=time_correct, delimiter=";")
    wf = get_factor_from_file("fw.csv", val_correction=vf, time_correction=time_correct, delimiter=";")

    # c1, w1, c2, w2, wp

    start_nums = [[99990, 10, 0, 0], [2000, 0, 0, 0], [100000, 0, 0, 0], [2000, 0, 0, 0], [10000, 0, 0, 0]]

    c1_af = [cf, hf, 0, 0, 0]
    w1_af = [hf, wf, 0, 0, wf]
    c2_af = [0, 0, cf, wf, 0]
    w2_af = [0, 0, wf, hf, hf]
    wp_af = [0, wf, 0, hf, vf]

    area_factors = [c1_af, w1_af, c2_af, w2_af, wp_af]
    epid_factors = [Factor(beta), Factor(gama)]
    vahta_model = get_area_model(["c1", "w1", "c2", "w2", "wp"],
                                 start_nums, area_factors, epid_factors, "SIRD", death_rate=0.2)
    vahta_model.stop_mode = "m"
    vahta_model.limit_step = 1100
    vahta_model.divided_n = False

    vahta_model.start_model()

    vahta_model.write_result_file(filename, delimiter=";")


def experiment_3(filename):
    all_pep = 224000
    cf = 1 / (102000 / all_pep)  # city_factor
    vf = 1.17 / (14000 / all_pep)  # vahta_factor
    time_correct = 1

    beta = 0.12
    gama = 0.1

    hf = get_factor_from_file("fh.csv", val_correction=cf, time_correction=time_correct, delimiter=";")
    wf = get_factor_from_file("fw.csv", val_correction=vf, time_correction=time_correct, delimiter=";")

    # c1, w1, c2, w2, wp

    start_nums = [[99990/all_pep, 10/all_pep, 0, 0], [2000/all_pep, 0, 0, 0], [100000/all_pep, 0, 0, 0],
                  [2000/all_pep, 0, 0, 0], [10000/all_pep, 0, 0, 0]]

    c1_af = [cf, hf, 0, 0, 0]
    w1_af = [hf, wf, 0, 0, wf]
    c2_af = [0, 0, cf, wf, 0]
    w2_af = [0, 0, wf, hf, hf]
    wp_af = [0, wf, 0, hf, vf]

    area_factors = [c1_af, w1_af, c2_af, w2_af, wp_af]
    epid_factors = [Factor(beta), Factor(gama)]
    vahta_model = get_area_model(["c1", "w1", "c2", "w2", "wp"],
                                 start_nums, area_factors, epid_factors, "SIRD", death_rate=0.2)
    vahta_model.stop_mode = "m"
    vahta_model.limit_step = 1100
    vahta_model.divided_n = False

    vahta_model.start_model()

    vahta_model.write_result_file(filename, delimiter=";")

if __name__ == '__main__':
    # experiment_1("results/vahta_result1.csv")
    # experiment_2("results/vahta_result2.csv")
    experiment_3("results/vahta_result3.csv")




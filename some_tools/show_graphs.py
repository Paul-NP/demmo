import csv
from matplotlib import pyplot as plt


def my_float(line: str, floating_point=","):
    return float(line.replace(floating_point, "."))


def show_result(filename: str, delimiter: str = ";", show_column: tuple = "all"):
    with open(filename, "r", encoding="utf-8-sig") as file:
        csv_reader = csv.reader(file, delimiter=delimiter)
        head = next(csv_reader)
        if show_column == "all":
            column = head[1:]
        else:
            column = show_column

        table = {name: [] for name in head[1:]}
        x = []
        for row in csv_reader:
            x.append(int(row[0]))
            for name, val in zip(table, row[1:]):
                table[name].append(my_float(val))

        for name in show_column:
            plt.plot(x, table[name], label=name)
        print("ready")
        plt.legend()
        plt.show()


# show_result("results/vahta_result1.csv", show_column=("w1_I", "w2_I", "wp_I"))

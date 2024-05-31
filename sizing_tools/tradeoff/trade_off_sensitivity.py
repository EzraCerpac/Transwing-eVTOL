import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utility.plotting import show, save

input_grades = np.array([[4, 3, 3, 4, 5, 3], [2.9, 5.1, 3, 3.1, 3, 3.9],
                         [4, 3, 2, 4, 5, 3], [2, 3, 4, 2, 4, 2]])

random_grades = np.random.choice([1, 2, 3, 4, 5], size=(4, 6))

input_weights = np.array([0.1, 0.3, 0.15, 0.2, 0.1, 0.15]).T


class WeightSensitivity():

    def __init__(self, grades: np.ndarray, weights: np.ndarray) -> None:
        self.grades = grades
        self.start_weights = np.array([0.1, 0.3, 0.15, 0.2, 0.1, 0.15]).T
        self.weights = weights
        self.win_count = np.zeros(4)
        self.combinations = set()
        self.weights_df = pd.DataFrame([self.final_grades],
                                       columns=[
                                           'Winged Rotorcraft',
                                           'Rotating Wing', 'Folding Wing',
                                           'VSQP'
                                       ])

    @property
    def final_grades(self):
        return np.dot(self.grades, self.weights)

    @property
    def winner(self):
        return np.argmax(self.final_grades)

    def random_weigth_switch(self):
        i_from = np.random.randint(0, 6)
        i_to = i_from
        while i_to == i_from:
            i_to = np.random.randint(0, 6)
        boundary = 0.05
        lower_start = self.start_weights[i_from] - boundary
        higher_start = self.start_weights[i_to] + boundary
        if lower_start < self.weights[i_from] and self.weights[
                i_to] < higher_start:
            self.weights[i_from] -= 0.01
            self.weights[i_to] += 0.01

    def loop(self):
        count = 0
        data = []
        for i in range(500000):
            self.random_weigth_switch()
            w = str(self.weights)
            if not w in self.combinations:
                count += 1
                self.combinations.add(str(self.weights))
                self.win_count[self.winner] += 1
                data.append(self.final_grades)
        self.weights_df = pd.DataFrame(data,
                                       columns=[
                                           'Winged Rotorcraft',
                                           'Rotating Wing', 'Folding Wing',
                                           'VSQP'
                                       ])

    @show
    @save
    def plot_sensitivity(self) -> tuple[plt.Figure, plt.Axes]:
        # plt.rcParams["figure.figsize"] = [12, 8]
        # plt.rcParams["figure.autolayout"] = True
        fig, ax = plt.subplots(figsize=(7, 5))
        ax = self.weights_df[[
            'Winged Rotorcraft', 'Rotating Wing', 'Folding Wing', 'VSQP'
        ]].plot(
            kind='kde',
            ax=ax,
            xlabel='Grades',
            ylabel='Density',
        )
        # plt.axhline(0, color='black')
        plt.ylim(bottom=0.01)
        plt.xlabel('Scores')
        plt.legend(loc='upper left')
        return fig, ax


if __name__ == '__main__':
    w = WeightSensitivity(input_grades, input_weights)
    w.loop()
    print(w.start_weights)
    print(w.final_grades)
    print(w.win_count)
    print(len(w.combinations))
    w.plot_sensitivity()

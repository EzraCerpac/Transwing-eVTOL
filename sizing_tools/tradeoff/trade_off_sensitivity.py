import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


input_grades = np.array([[4, 3, 3, 4, 5, 3],
                         [2.9, 5.1, 3, 3.1, 3, 3.9],
                         [4, 3, 2, 4, 5, 3],
                         [2, 3, 4, 2, 4, 2]])

random_grades = np.random.choice([1, 2, 3, 4, 5], size=(4, 6))

input_weights = np.array([0.1,
                            0.3,
                            0.15,
                            0.2,
                            0.1,
                            0.15]).T

class WeightSensitivity():
    def __init__(self,grades,weights) -> None:
        self.grades = grades
        self.start_weights = np.array([0.1,
                            0.3,
                            0.15,
                            0.2,
                            0.1,
                            0.15]).T
        self.weights = weights
        self.win_count = np.zeros(4)
        self.combinations = set()
        self.weights_df = pd.DataFrame([self.final_grades],columns=['Winged Hovercraft','Rotating Wing','Folding Wing','Variable Skew Quadplane'])
        
    @property
    def final_grades(self):
        return sum((self.grades*self.weights).T)
    
    @property
    def winner(self):
        return np.argmax(self.final_grades)
    
    def random_weigth_switch(self):
        i_from = np.random.randint(0,6)
        i_to = i_from
        while i_to == i_from:
            i_to = np.random.randint(0,6)
        boundary = 0.05
        lower_start = self.start_weights[i_from] - boundary
        higher_start = self.start_weights[i_to] + boundary
        if lower_start < self.weights[i_from] and self.weights[i_to] < higher_start:
            self.weights[i_from] -= 0.01
            self.weights[i_to] += 0.01
        
        
    def loop(self):
        count = 0
        for i in range(500000):
            self.random_weigth_switch()
            w = str(self.weights)
            if not w in self.combinations:
                count += 1
                self.combinations.add(str(self.weights))
                self.win_count[self.winner] += 1
                newdata = pd.DataFrame([self.final_grades], columns=['Winged Hovercraft','Rotating Wing','Folding Wing','Variable Skew Quadplane'])
                self.weights_df = pd.concat([self.weights_df, newdata])

    def boxplot(self):
        # plt.rcParams["figure.figsize"] = [12, 8]
        # plt.rcParams["figure.autolayout"] = True
        ax = self.weights_df[['Winged Hovercraft','Rotating Wing','Folding Wing','Variable Skew Quadplane']].plot(kind='kde', title='Grade distribution')
        ax = plt.axhline(0, color='black')
        # Display the plot
        plt.savefig('sensitivity.pdf')
        plt.show()





if __name__ == '__main__':
    w = WeightSensitivity(input_grades, input_weights)
    w.loop()
    print(w.start_weights)
    print(w.final_grades)
    print(w.win_count)
    print(len(w.combinations))
    w.boxplot()

    

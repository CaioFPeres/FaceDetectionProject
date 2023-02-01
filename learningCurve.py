import numpy as np
import matplotlib.pyplot as plt



if __name__ == "__main__":

    train = np.array([])
    test = np.array([])

    dir1 = "C:\\Users\\Caio Peres\\source\\repos\\dlib-19.24\\examples\\build\\Release\\metrics.csv"
    dir2 = "C:\\Users\\Caio Peres\\Desktop\\testfaces\\celebrity_only\\metrics.csv"

    with open(dir1, "r") as f:
        for line in f:
            vTrain, vTest = line.split(sep=";")
            train = np.append(train, float(vTrain))
            test = np.append(test, float(vTest))


    fig, ax = plt.subplots()

    ax.plot(train, color = 'green', label = 'Train')
    ax.plot(test, color = 'red', label = 'Test')
    ax.legend(loc = 'upper right')
    plt.show()
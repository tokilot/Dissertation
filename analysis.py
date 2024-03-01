import pandas as pd
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from sklearn import metrics

events = {"IN": "101101", "OUT": "011110", }
result = {"confusion": [], "accuracy": 0, "precise": 0, "recall": 0}


def Cleaning(data):
    normal = ["00", "01", "11", "10", "IN", "OUT"]
    errors = [i for i in data.iloc[:, 1].value_counts().index.to_numpy() if i not in normal]
    error_indexs = []
    for error in errors:
        index = data[data.iloc[:, 1] == error].index
        error_indexs.append(index)
    return error_indexs


def Missing(data):
    start = data.iloc[0, 0]
    result = data.iloc[:, 1].value_counts()
    length = result["00"] + result["01"] + result["10"] + result["11"]
    data.iloc[0:length, 0] = pd.date_range(start, periods=length, freq='S')
    data.iloc[0:length, 0] = data.iloc[0:length, 0].apply(
        lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S'))
    return data


def Seperate(data):
    """seperate sensors data and observations"""
    clean = Cleaning(data)
    if len(clean) != 0:
        print(clean)
        raise Exception
    data = Missing(data)
    df1 = data.query("(Return!='IN'& Return!='OUT')")
    df2 = data.query("(Return=='IN'| Return=='OUT')")
    df = pd.merge(df1, df2, how='left', on='Time')
    df.columns = ["Time", "Return", "Obser"]
    return df


def Frequency(data, fre):
    """Get data in different frequence from raw data"""
    df = copy.deepcopy(data)
    index = df[df["Obser"].isnull() == False].index
    for i in index:
        for j in range(1, fre):
            df["Obser"].loc[i + j] = df["Obser"].loc[i]
    return df[::fre]


def Format(data):
    """Translate the data to result that can be compared in confusion matrix"""
    df = copy.deepcopy(data)
    df["Obser"].fillna("NO", inplace=True)
    for i in range(1, len(df) - 1):
        event = df["Return"].loc[i - 1] + df["Return"].loc[i] + df["Return"].loc[i + 1]
        if event == events["IN"]:
            df.loc[i, "Return"] = "IN"
        elif event == events["OUT"]:
            df.loc[i, "Return"] = "OUT"
    df["Return"].replace(["00", "10", "01", "11"], ["NO", "NO", "NO", "NO"], inplace=True)
    return df


def Accuracy(data):
    data = Format(data)
    data.to_csv("data.csv")
    print(data["Obser"].value_counts())
    y_true = np.array(data["Obser"])
    y_pred = np.array(data["Return"])
    result["confusion"] = metrics.confusion_matrix(y_true, y_pred)
    result["accuracy"] = metrics.accuracy_score(y_true, y_pred)
    result["precise"] = metrics.precision_score(y_true, y_pred, average='macro')
    result["recall"] = metrics.recall_score(y_true, y_pred, average='macro')
    result["F1-score"] = metrics.f1_score(y_true, y_pred, average='macro')
    return result


def Plot(data):
    data = Format(data)

    def Cut(x):
        x = x[11:-3]
        return x

    data["Time"] = data["Time"].map(Cut)
    df0 = data[data["Obser"] == "IN"]
    df0["Compare"] = np.where(df0["Obser"] == df0["Return"], 0, 1)
    df1 = data[data["Obser"] == "OUT"]
    df1["Compare"] = np.where(df1["Obser"] == df1["Return"], 0, 1)
    df2 = data[data["Obser"] == "NO"]
    df2["Compare"] = np.where(df2["Obser"] == df2["Return"], 0, 1)

    fig, ax = plt.subplots(3, 1, figsize=(8, 10), layout='constrained')
    ax[0].plot(df0["Time"], df0["Compare"], "C0", label="Event:IN")
    ax[0].set_position([0.15, 0.7, 0.8, 0.25])
    ax[1].plot(df1["Time"], df1["Compare"], "C1", label="Event:OUT")
    ax[1].set_position([0.15, 0.4, 0.8, 0.25])
    ax[2].plot(df2["Time"], df2["Compare"], "C5", label="Event:NO")
    ax[2].set_position([0.15, 0.1, 0.8, 0.25])

    for i in [0, 1, 2]:
        ax[i].xaxis.set_major_locator(ticker.AutoLocator())
        ax[i].set_yticks([1, 0], ["Different", "Same"],fontsize=12)
        ax[i].legend(loc='upper right',fontsize=10)
    fig.suptitle("Module Recognition and Occupant Events",fontsize=20)
    fig.text(0.03, 0.5, 'Result', va='center', rotation='vertical', fontsize=20)
    fig.text(0.5, 0.03, 'Time', va='center', ha='center', fontsize=20)
    plt.show()


filename = "collecting_data_new_20240208.csv"
order = input("Type the Order:")
if order == "1":
    raw_data = pd.read_csv(filename, names=["Time", "Return"], skiprows=2, dtype='str')
    data = Seperate(raw_data)
    data.to_csv("collecting_data_new.csv", index=False)
elif order == "2":
    data = pd.read_csv(filename, dtype='str')
    # Plot(data)
print(Accuracy(data))

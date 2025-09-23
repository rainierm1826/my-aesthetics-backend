import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def linear_regression_model(data, y_values, group_by=None):
    if not data:
        return []

    for row in data:
        row["type"] = "actual"

    df = pd.DataFrame(data)

    if group_by == "year":
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[y_values].values
        model = LinearRegression().fit(X, y)

        future_X = np.arange(len(df), len(df) + 2).reshape(-1, 1) 
        future_pred = model.predict(future_X)

        future_years = list(range(int(df["year"].iloc[-1]) + 1, int(df["year"].iloc[-1]) + 2))
        for year, pred in zip(future_years, future_pred):
            data.append({"year": str(year), y_values: int(pred), "type": "predicted"})

    elif group_by == "month":
        X = df["month_num"].values.reshape(-1, 1)
        y = df[y_values].values
        model = LinearRegression().fit(X, y)

        future_X = np.arange(df["month_num"].max() + 1, df["month_num"].max() + 4).reshape(-1, 1)
        future_pred = model.predict(future_X)

        month_names = ["January","February","March","April","May","June",
                        "July","August","September","October","November","December"]
        for m, pred in zip(future_X.flatten(), future_pred):
            month_index = int((m - 1)) % 12
            data.append({"month": month_names[month_index], y_values: int(pred), "type": "predicted"})

    elif group_by == "weekday":
        X = df["dow_num"].values.reshape(-1, 1)
        y = df[y_values].values
        model = LinearRegression().fit(X, y)

        future_X = np.arange(df["dow_num"].max() + 1, df["dow_num"].max() + 4).reshape(-1, 1)
        future_pred = model.predict(future_X)

        weekdays = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
        for d, pred in zip(future_X.flatten(), future_pred):
            dow_index = int(d) % 7
            data.append({"weekday": weekdays[dow_index], y_values: int(pred), "type": "predicted"})

    return data

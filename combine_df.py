import os
import pandas as pd
import json
import datetime as dt


def make_date_id_map():
    paths = sorted(
        [os.path.join("data", "individual", x) for x in os.listdir("./data/individual") if x.endswith(".csv")]
    )
    dates = [x.split("-")[0].split("/")[-1] for x in paths]
    ids = [x.split("-")[1].split(".")[0] for x in paths]
    return {d: id for d, id in zip(dates, ids)}


def make_all_csv(save_to="./data/all.csv"):
    paths = sorted(
        [
            os.path.join("data", "individual", x) 
            for x in os.listdir("./data/individual") if x.endswith(".csv")
        ]
    )
    dates = [x.split("-")[0].split("/")[-1] for x in paths]
    ids = [x.split("-")[1].split(".")[0] for x in paths]
    id_date = [[x, y] for x, y in zip(ids, dates)]
    id_date_df = pd.DataFrame(id_date, columns=pd.Series(["submission_id", "date"]))
    dfs = [
        pd.read_csv(path, index_col=0, na_values=[], keep_default_na=False)
        for path in paths
    ]
    df = pd.concat(dfs)

    df_with_dates = pd.merge(
        df, id_date_df, "left", left_on="submission_id", right_on="submission_id"
    )
    if save_to:
        df_with_dates.to_csv(save_to)
    return df_with_dates


def get_all_csv(path="./data/all.csv"):
    if not os.path.isfile(path):
        raise Exception("all_csv not found")
    else:
        return pd.read_csv(path, index_col=0, na_values=[], keep_default_na=False)


def get_date_to_id_map(path="data/date_id_key.json"):
    with open(path, "r") as f:
        return json.load(f)


def combine_dfs(start_date: str, end_date: str):
    with open("data/date_id_key.json", "r") as f:
        date_id_map = json.load(f)
            
    date_id_df = pd.DataFrame(
        [[k, v] for k, v in date_id_map.items()], 
        columns=pd.Series(["date", "submission_id"])
    )

    dfs = []
    current = dt.datetime.strptime(start_date, "%Y_%m_%d")
    before = True
    while before:
        current_date = current.strftime("%Y_%m_%d")
        current_path = f"./data/individual/{current_date}-{date_id_map[current_date]}.csv"
        if os.path.isfile(current_path):
            df = pd.read_csv(
                current_path, index_col=0, na_values=[], keep_default_na=False
            )
            dfs.append(
                pd.merge(df, date_id_df, left_on="submission_id", right_on="submission_id")
            )
        current = current + dt.timedelta(days=1)
        if current > dt.datetime.strptime(end_date, "%Y_%m_%d"):
            before = False

    return pd.concat(dfs).reset_index(drop=True)


combine_dfs("2024_01_01", "2024_01_09")

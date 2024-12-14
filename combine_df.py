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
        [os.path.join("data", "individual", x) for x in os.listdir("./data/individual") if x.endswith(".csv")]
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


def get_date_to_id_map(path="data/date_id_key.json"):
    with open(path, "w") as f:
        return json.load(f)


def combine_dfs(start_date: str, end_date: str):
    """
    still need to finish this.
    """
    with open("data/date_id_key.json", "r") as f:
        date_id_map = json.load(f)

    start_id = date_id_map[start_date] 

    df_names = [f"{start_date}-{start_id}.csv"]
    current = dt.datetime.strptime(start_date, "%Y_%m_%d")
    before = True
    while before:
        current = current + dt.timedelta(days=1)
        current_str = dt.datetime.strftime(current, "%Y_%m_%d")
        df_names.append(
            f"{current_str}-{date_id_map[current_str]}"
        )
        if current == dt.datetime.strptime(end_date, "%Y_%m_%d"):
            before = False

    return df_names

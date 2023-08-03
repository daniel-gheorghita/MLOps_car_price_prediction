#!/usr/bin/env python
# coding: utf-8

# In[18]:


import pandas as pd
import os
import glob
from matplotlib import pyplot as plt
import numpy as np
from time import sleep, time
from pprint import pprint
from prefect import flow, task


# In[19]:


EXTERNAL_DATA_PATH = "./data/yearly"
AVAILABLE_DATA_PATH = "./data/available"


# In[22]:


def get_year_from_filename(filepath):
    head, tail = os.path.split(filepath)
    return int(tail.split(".")[0])


@task()
def get_new_dataset(input_folder, latest_year_available=1900, stream=True):
    """
    Check if there is new data available and <<download>>.
    If stream is true, only take the oldest <<new files>> available (e.g., if data for 1995 and 1996 is available,
    take only the file for 1995).
    """
    assert os.path.exists(
        input_folder
    ), f"Input location {input_folder} does not exist."
    files_list = glob.glob(os.path.join(input_folder, "*.csv"))
    print(f"Found {len(files_list)} data files.")
    valid_files = [
        file
        for file in files_list
        if get_year_from_filename(file) > latest_year_available
    ]
    valid_files.sort()
    print(f"Found {len(valid_files)} data files newer than {latest_year_available}.")
    if len(valid_files) == 0:
        print("No new data available.")
        return None
    if stream:
        valid_files = valid_files[0]
        print(f"Loading only one file: {valid_files}")
    df = pd.concat(map(pd.read_csv, [valid_files]))
    print("Loaded new data.")
    return df


@task()
def get_latest_available_data_year(input_folder):
    assert os.path.exists(
        input_folder
    ), f"Input location {input_folder} does not exist."
    files_list = glob.glob(os.path.join(input_folder, "*.csv"))
    if len(files_list) == 0:
        return 1900
    else:
        files_list.sort()
        return get_year_from_filename(files_list[-1])


@task()
def store_data(df, location):
    for year in df["year"].value_counts().index:
        df[df["year"] == year].to_csv(
            os.path.join(location, f"{year}.csv"), index=False
        )


@flow(name="main-data-flow")
def main_data_flow(available_data_path, external_data_path):
    # Check the available dataset
    latest_available_data = get_latest_available_data_year(available_data_path)

    # Update dataset
    df_new = get_new_dataset(
        external_data_path, latest_year_available=latest_available_data
    )

    if df_new is None:
        print("No new data.")
    else:
        store_data(df_new, location=available_data_path)
        print("Stored new data.")


# In[23]:


if __name__ == "__main__":
    main_data_flow(
        available_data_path=AVAILABLE_DATA_PATH, external_data_path=EXTERNAL_DATA_PATH
    )


# In[ ]:

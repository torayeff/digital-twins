import numpy as np
import pandas as pd
import sqlite3

def calc_kWh(measurements, dstep):
    """
    Args:
        measurements: power measurements in kWh
        dstep: delta time step in seconds

    Returns:
        Power in kWh
    """
    # assuming that step in milliseconds
    p = np.sum(measurements)
    p = p * dstep / 3600
    return p


def get_ec(df, sampling_rate):
    """Gets energy consumption.

    Args:
        df (pandas.DataFrame): Energy consumption dataframe.
        sampling_rate (int): The sampling rate in milliseconds.

    Returns:
        float: Energy consumption in kWh.
    """
    df = df.set_index("time_point")
    df = df.resample(f"{sampling_rate}ms").mean().ffill()

    ec = calc_kWh(df["ins_pwr"], dstep=sampling_rate / 1000)
    return ec

def get_ec_from_db(db_file, sampling_rate):
    con = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT time_point, ins_pwr FROM energy_consumption;", con, parse_dates=["time_point"])
    ec = get_ec(df, sampling_rate)
    return ec
"""
Date            Ver No.     Author      History
01/20/2018      V0.1        Scott Yang  First version
01/22/2018      V0.2        Scott Yang  Adding file path argv and restructure functions

"""

# ! python3.6
import pandas as pd
from pandas import ExcelWriter
import os
import sys
import glob

table = {}
PM = "M8006C268"

# Data frame arrangement
arrange = ["Time", "Cell ID", "UE ID", "CRNTI", "VoLTE", "Error", "PM"]
err_list = []

def parse_data(data_frame, ErrType, table):
    for index, row in data_frame.iterrows():
        table["UE ID"] = row[" Emil UE ID"]
        table["CRNTI"] = row[" CRNTI"]
        table["Cell ID"] = row[" LCR ID"]
        table["VoLTE"] = row[" VoLTE"]
        table["PM"] = row[" PM Counters"]
        table["Time"] = row[" eNB Start Time"]

        if ErrType == "rlc":
            table["Error"] = row[" Outgoing HO Cause"]
        else:
            table["Error"] = row[" RLF Ind List"]
        # Need to use dict.copy(),otherwise are just adding references to the same dictionary over and over again:
        err_list.append(table.copy())

def write_file(data, filetype, write_path):
    output = data[arrange]
    writer = ExcelWriter(write_path + "\\" + filetype + ".xlsx")
    output.to_excel(writer)
    try:
        writer.save()
    except PermissionError:
        print("Oops! Please check the final.xlsx is close")

def emil_parser():
    number_arg = len(sys.argv) - 1
    # set path
    if number_arg == 0:
        # path for input csv file
        current_path = os.getcwd() + "//*.csv"
        # path for output .xlsx files
        write_path = os.getcwd()
    else:
        #path for input csv file
        current_path = sys.argv[1] + "//*.csv"
        #path for output .xlsx files
        write_path = sys.argv[1]

    for file in glob.glob(current_path):
        print("Processing files:" + file)
        # low_memory=False to resolve the error from pandas reading
        df = pd.read_csv(file, sep=';', low_memory=False)

        # Select all call with Outgoing HO Cause == " Intra Cell: MaxRlcRetrans"
        print("List of MaxRlcRetrans...")
        rlcdf = df[df[' Outgoing HO Cause'] == " Intra Cell: MaxRlcRetrans"]
        parse_data(rlcdf, "rlc", table)

        # Select all call with Outgoing HO Cause == " CqiRlf"
        print("List of CqiRLF...")
        cqirlfdf = df[df[' RLF Ind List'].str.contains(" CqiRlf_ON")]
        parse_data(cqirlfdf, "cqirlf", table)

        # Select all call with Outgoing HO Cause == " PuschRlf"
        print("List of PuschRLF...")
        puschrlfdf = df[df[' RLF Ind List'].str.contains(" PuschRlf_ON")]
        parse_data(puschrlfdf, "puschrlf", table)

    # Prepare to output to excel file
    output = pd.DataFrame(err_list)
    write_file(output, "All_Data", write_path)

    # filter only conatains with the specidfic PM affects KPI
    kpidf = output[output['PM'].str.contains(PM)]
    write_file(kpidf, "KPI_ONLY", write_path)


if __name__ == "__main__":
    emil_parser()
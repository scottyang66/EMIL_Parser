"""
Date            Ver No.     Author      History
01/20/2018      V0.1        Scott Yang  First version

"""


#! python3.6

import pandas as pd
from pandas import ExcelWriter
import os
import glob

table = {}
PM = "M8006C268"

#Data frame arrangemnet
arrange = ["Time","Cell ID","UE ID","CRNTI","VoLTE","Error","PM"]

#set path
current_path = os.getcwd()
path = current_path + "//*.csv"
err_list=[]

def parse_data(data_frame, ErrType):
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
        #Need to use dict.copy(),otherwise are just adding references to the same dictionary over and over again:
        err_list.append(table.copy())

def write_file(data, filetype):
    output = data[arrange]
    writer = ExcelWriter(current_path + "\\" + filetype + ".xlsx")
    output.to_excel(writer)
    try:
        writer.save()
    except PermissionError:
        print("Oops! Please check the final.xlsx is close")


for file in glob.glob(path):
    print("Processing files:" + file)
    #low_memory=False to resolve the error from pandas reading
    df = pd.read_csv(file,sep=';', low_memory=False)

    #Select all call with Outgoing HO Cause == " Intra Cell: MaxRlcRetrans"
    print("List of MaxRlcRetrans...")
    rlcdf = df[df[' Outgoing HO Cause'] == " Intra Cell: MaxRlcRetrans"]
    parse_data(rlcdf,"rlc")

    #Select all call with Outgoing HO Cause == " CqiRlf"
    print("List of CqiRLF...")
    cqirlfdf = df[df[' RLF Ind List'].str.contains(" CqiRlf_ON")]
    parse_data(cqirlfdf,"cqirlf")
    
    #Select all call with Outgoing HO Cause == " PuschRlf"
    print("List of PuschRLF...")
    puschrlfdf = df[df[' RLF Ind List'].str.contains(" PuschRlf_ON")]
    parse_data(puschrlfdf,"puschrlf")

#Prepare to output to excel file
output = pd.DataFrame(err_list)
write_file(output,"All_Data")

#filter only conatains with the specidfic PM affects KPI 
kpidf = output[output['PM'].str.contains(PM)]
write_file(kpidf,"KPI_ONLY")
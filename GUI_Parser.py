"""
Date            Ver No.     Author      History
01/23/2018      V0.1        Scott Yang  First version

"""
# ! python3.6
import pandas as pd
from pandas import ExcelWriter
import os
import sys
import glob
from tkinter import filedialog
from tkinter import *
from threading import Thread

table = {}
PM = "M8006C268"

# Data frame arrangement
arrange = ["Time", "Cell ID", "UE ID", "CRNTI", "VoLTE", "Error","Failure Phase","S1 Rel Cause", "PM"]
err_list = []

def browse_button():
    global filename
    filename = filedialog.askdirectory() #get the .csv folder location
    select_path.insert(END, filename)

def result_button():
    output = filedialog.askopenfile(filetypes=(("Template files","*.xlsx"),("All files", "*.*")))
    # Using "Thread" module the GUI thread will not get stuck waiting for the external process to finish.
    t = Thread(target = lambda: os.system(output.name))
    t.start()

def parse_data(data_frame, ErrType, table): #Data parser funcation for different error causes
    for index, row in data_frame.iterrows():
        table["UE ID"] = row[" Emil UE ID"]
        table["CRNTI"] = row[" CRNTI"]
        table["Cell ID"] = row[" LCR ID"]
        table["VoLTE"] = row[" VoLTE"]
        table["PM"] = row[" PM Counters"]
        table["Time"] = row[" eNB Start Time"]
        table["Failure Phase"] = row[" Failure Phase"]
        table["S1 Rel Cause"] = row[" S1 Rel Cause"]

        if ErrType == "rlc":
            table["Error"] = row[" Outgoing HO Cause"]
        else:
            table["Error"] = row[" RLF Ind List"]
        # Need to use dict.copy(),otherwise are just adding references to the same dictionary over and over again:
        err_list.append(table.copy())

def write_file(data, filetype, write_path): #This funcation is to save the ouptut results in .xlsx files
    output = data[arrange]
    writer = ExcelWriter(write_path + "\\" + filetype + ".xlsx")
    output.to_excel(writer)
    try:
        writer.save()
    except PermissionError:
        print("Oops! Please check the final.xlsx is close")
        status.insert(END, "Oops! Please make sure the output .xlsx are close..." + '\n')

def emil_parser():  #This is starter funcation after "Run" is clicked
    print("Start Parsing")
    status.insert(END,"Start parsing..." + '\n')
    current_path = filename + "//*.csv" #file name is getting from the "browse_button" tk funcation
    write_path = filename   #path for output .xlsx files

    print(write_path)
    status.insert(END, write_path + '\n')

    for file in glob.glob(current_path):
        print("Processing files:" + file)
        status.insert(END, file + '\n')
        # low_memory=False to resolve the error from pandas reading
        df = pd.read_csv(file, sep=';', low_memory=False)

        # Select all call with Outgoing HO Cause == " Intra Cell: MaxRlcRetrans"
        print("List of MaxRlcRetrans...")
        status.insert(END, "List of MaxRlcRetrans..." + '\n')
        rlcdf = df[df[' Outgoing HO Cause'] == " Intra Cell: MaxRlcRetrans"]
        parse_data(rlcdf, "rlc", table)

        # Select all call with Outgoing HO Cause == " CqiRlf"
        print("List of CqiRLF...")
        status.insert(END, "List of CqiRLF..." + '\n')
        cqirlfdf = df[df[' RLF Ind List'].str.contains(" CqiRlf_ON")]
        parse_data(cqirlfdf, "cqirlf", table)

        # Select all call with Outgoing HO Cause == " PuschRlf"
        print("List of PuschRLF...")
        status.insert(END, "List of PuschRLF..." + '\n')
        puschrlfdf = df[df[' RLF Ind List'].str.contains(" PuschRlf_ON")]
        parse_data(puschrlfdf, "puschrlf", table)

    # Prepare to output to excel file
    output = pd.DataFrame(err_list)
    write_file(output, "All_Data", write_path)

    # filter only conatains with the specidfic PM affects KPI
    kpidf = output[output['PM'].str.contains(PM)]
    write_file(kpidf, "KPI_ONLY", write_path)

    status.insert(END, "DONE!!!" + '\n')

#### Tk GUI section ######
window = Tk()
window.title("Nokia EMIL CSV Parser")
window.geometry("370x370")


#Button for folder locator
b1=Button(window,text="Browse EMIL CSV", command=browse_button)
b1.grid(row=0,column=0, sticky=W)

#Label for Load location
lable=Label(window,text="Load Location:  ")
lable.grid(row=1,column=0, sticky=W)

#Print folder path
select_path=Text(window,height=1,width=30)
select_path.grid(row=1,column=0, sticky=E)

#Run button
b1=Button(window,text="Run", command=emil_parser)
b1.grid(row=3,column=0, sticky=W)

#Status
status=Text(window,height=15,width=45)
status.grid(row=4,column=0)

#Button for result locator
b1=Button(window,text="Results Folder", command=result_button)
b1.grid(row=21,column=0, sticky=W)


window.mainloop()
#### End of Tk GUI section ######


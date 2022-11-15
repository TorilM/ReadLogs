#!/usr/bin/env python
# coding: utf-8

# 

# In[31]:


#Denna är det som fungerar med en askfileopen

import re
import shutil
import csv
import pandas as pd
from struct import unpack_from
import os   
import datetime
datetime.datetime.strptime
from zipfile import ZipFile
#import numpy as np
#import sys
from datetime import datetime
import tkinter 
from tkinter.filedialog import askopenfilename
from tkinter import filedialog 
from tkinter import messagebox
import time
timestr = time.strftime("%Y%m%d-%H%M")
import pytz
timezone = pytz.timezone('Europe/Stockholm')



def filename(astring):
        return astring[:14]
def tid(a):
    return (a[15:25]+" "+a[26:28]+":"+a[28:30]+":"+a[30:33]    )
def rens(x):
    x='W'+x[5]+x[17]   
    return x   


traceindex = ["deviceSerial",
              "timestamp",
              "dataTypeId",
              "traceChannel",
              "traceCode",
              "presentation",
              "deviceType",
              "isArray",
              "messageLength",
              "traceData"
              ]
dataTypeId = {
    1: "TU8",
    2: "TU16",
    3: "TU32",
    4: "TU64",
    5: "TS8",
    6: "TS16",
    7: "TS32",
    8: "TS64",
    9: "TD32",
    10: "TD64",
    11: "TBool",
    20: "TBlob",
    21: "TStringA",
    22: "TStringW",
    0x0C06: "TraceSensorStartUp"
}
dataTypeId = {
    1: "TU8",
    2: "TU16",
    3: "TU32",
    4: "TU64",
    5: "TS8",
    6: "TS16",
    7: "TS32",
    8: "TS64",
    9: "TD32",
    10: "TD64",
    11: "TBool",
    20: "TBlob",
    21: "TStringA",
    22: "TStringW",
    0x0C06: "TraceSensorStartUp"
}
deviceType = {
    3: "PCS",
    5: "EDM",
    16: "IM",
    17: "Tilt",
    18: "Deflection",
    19: "Deflection_Loader",
    20: "Diagnostic_Manager",
    21: "Tracker",
    22: "Tracker_Loader",
    23: "CCB_Camera",
    24: "Plumet_Camera",
    25: "IM_Debug_Implementation",
    26: "Coordinate_Transform_Implementation",
    100: "test",
    255: "Supervisor"
}

exclude = ["procTrackerCommunication.cpp(","ignoring it", "GetCapabilitiesV2 not OK response status:13","HandleXnpMessage received XNP packet with wrong counter"]
trigger = []
trace_messages = []

def trimble_datetime2pandas_datetime(trimble_datetime):
    '''
    Convert from the datetime storage format of tmble instruments to that of
    pandas
    '''
    if trimble_datetime > 365*24*3600*10e7 and trimble_datetime < 2**63:
        return pd.to_datetime(
            (trimble_datetime-11_644_470_000*10_000_000)*100,
            unit='ns')#Hannes original , utc=True
    else:
        return pd.to_datetime("1970-01-01")

def read_trace_file(trace_file_path):
    '''
    Takes a trace file path and yields trace messages
    stored in pandas Series. Currently limited to trace messages
    containing strings.
    '''
    with open(trace_file_path, mode='rb',decode="Latin-1") as trace_file:
        if(len(trace_file.read(0x40)) == 0x40):  # skip xnp-fileheader
            while(True):
                trace_bytes = trace_file.read(28)
                if(len(trace_bytes) != 28):
                    break
                trace = list(unpack_from('<LQHHHHBB', trace_bytes, 0))
                if trace[2] not in [21, 22]:
                    trace_body_length = unpack_from(
                        '<L', trace_file.read(4), 0)[0]
                    trace_file.read(trace_body_length)
                    continue

                trace[1] = trimble_datetime2pandas_datetime(trace[1])
                trace[6] = deviceType[trace[6]]

                trace.append(unpack_from('<LL', trace_file.read(8), 0)[1])
                trace.append(trace_file.read(trace[8]).decode('ascii'), errors='ignore')
                yield pd.Series(data=trace)


def read_trace(trace_file):
    '''
    Takes a binary stream and yields trace messages
    stored in pandas Series. Currently limited to trace messages
    containing strings
    '''
    if(len(trace_file.read(0x40)) == 0x40):  # skip xnp-fileheader
        while(True):
            trace_bytes = trace_file.read(28)
            if(len(trace_bytes) != 28):
                break
            trace = list(unpack_from('<LQHHHHBB', trace_bytes, 0))
            if trace[2] not in [21, 22]:
                trace_body_length = unpack_from(
                    '<L', trace_file.read(4), 0)[0]
                trace_file.read(trace_body_length)
                continue

            trace[1] = trimble_datetime2pandas_datetime(trace[1])
           # trace[1] = trace[1].apply(lambda x: x.replace(microsecond = 0))#tar bort tusendels sekund
            trace[6] = deviceType[trace[6]]
            time=trace[1]
            trace[1]=str(time)[:19]   #förenklar tidsutläsningen med att ta bort mikrosekunder

            trace.append(unpack_from('<LL', trace_file.read(8), 0)[1])
            trace.append(trace_file.read(trace[8]).decode('ascii', errors='ignore'))
            yield pd.Series(data=trace)  #yield pd.Series(data=trace, index=traceindex)


    
                           
ID = "Production number"   
service="service log entries as text:"
slut="TRACE LOGS"
s="TRIMBLE-NONE-IMC"
#ServiceLogs="service log entries as text:"
gml="TRIMBLE-SX10"
path=r'C:\\'
 #initialpath där sökning efter filen börjar
if os.path.exists(r'C:\ProgramData\Trimble\Trimble Data\System Files'): 
    path=r'C:\ProgramData\Trimble\Trimble Data\System Files'
    
capture=False
root = tkinter.Tk()
os.chdir(path)
file = tkinter.filedialog.askopenfilename(
        parent=root, initialdir=path,
        title='Välj vilken tracefil du vill öppna',
        filetypes=[('Tracelog', '.zip')]
        )
root.destroy()
root.mainloop() 

directory = os.path.split(file)[0]
filename=os.path.split(file)[1]

list_of_files = os.listdir(directory) 

if (filename.endswith(".zip")): 
            if s in filename:
                pos=filename.find(s)
                IMCnr=filename[pos+16:pos+22]
                #print('IMCnr', IMCnr) 
                filstart=("TRIMBLE-NONE-IMC" + IMCnr)
            elif gml in filename:
                pos=filename.find(gml)
                IMCnr=filename[pos+13:pos+21]
                filstart=("TRIMBLE-SX10-" + IMCnr)
else: 
    print('Du har inte valt en Tracelogs.zip-fil.')
    raise SystemExit
      

tracepath   =directory + "/" + "TraceLogs" 
servicepath =directory + "/" + 'ServiceLogs'
os.chdir(directory) 

PASSWORD=bytes(filstart, encoding= 'utf-8')

with ZipFile(filename,'r') as zip:  
    zip.setpassword(PASSWORD)
    zip.extractall(directory)
    zip.close()
os.chdir(directory)        
print (os.getcwd(), filstart +"_InstrumentLogReport.txt")    

with open (filstart +"_InstrumentLogReport.txt") as fil:
            #oldfile=fil
            lines=fil.readlines()
            print ('Service-16',lines[16])
            string=str(lines[16])
            Instrumentnummer=string[-6:-1]
            #minräknare=0
            #linje=next(f)
            print(Instrumentnummer)
fil.close()             
with open (filstart +"_InstrumentLogReport.txt") as fm:            
            for line in fm:
                if service in line:
                    with open (r'C:\ProgramData\Trimble\Trimble Data\System Files\mellan.csv',"w",newline="")as utfil:
                        writer=csv.writer(utfil)
                        writer.writerows([line] for line in fm)
                    utfil.close()
fm.close()   

combo_file = r'C:\ProgramData\Trimble\Trimble Data\System Files\Combo1.csv'

with open(r'C:\ProgramData\Trimble\Trimble Data\System Files\mellan.csv') as fp:
    line = fp.readline()

    while "TRACE LOGS" not in line:
        line=re.sub('"','',line) 
        line=re.sub("    +", ",", line.strip(),6)
        line=re.sub('["+]','',line) 
        listan = line.split (",")
        with open (combo_file,"a",newline="") as out_file:
            writer = csv.writer(out_file)
            writer.writerows([listan])
        out_file.close() 
        line = fp.readline()
fp.close()              
#shutil.move (filstart +"_InstrumentLogReport.txt",Instrumentnummer +"_"+timestr+ "-Service.txt")

with open(Instrumentnummer + ".csv", 'w',newline='') as csvfile:

                            writer = csv.writer(csvfile)
                            minaval=[['tid','device','fel']]
                            writer.writerow(minaval)
csvfile.close()  
                          


                    
for  file in os.listdir(tracepath):   #får bara gå i den subdirectory vi har spec:ad!             
                            if (file.endswith("LS.trace")):  #om det är en tracefil vi skall läsa                        
                                trace_file=tracepath + "/" + file
                                #print(trace_file)  
                                with open(trace_file, 'rb') as f:                                                   
                                    for trace_message in read_trace(f):                                   
                                        row=[trace_message[1], trace_message[6],trace_message[9]]                                  
                                        if not any (s in trace_message[9]  for s in exclude): 
                                            with open(Instrumentnummer + ".csv","a") as csvfile:
                                                
                                                writer = csv.writer(csvfile)
                                                writer.writerow(row)                                                                                                                        
                                            csvfile.close()
                                f.close()                                   

trace=pd.read_csv(Instrumentnummer+".csv", header=0, skiprows=[0])
trace=trace.rename(columns={'tid':'Tid'})
trace.columns=['tid','device','fel']
trace['tid']=pd.to_datetime(trace.tid)
trace=trace.sort_values(by='tid', ascending=False)
trace.to_csv((Instrumentnummer +"_"+ timestr+ "-Trace.csv"), index=None, mode='a')

combo=pd.read_csv('Combo1.csv', encoding='utf-8', names=['tid','type','FW','device','fel'], index_col=False )
#print(combo.iloc[1,0])
#print(combo.head(3))
combo=combo.append(trace, sort=True)
#print(combo.head(2))
combo['tid']=pd.to_datetime(combo.tid)
combo=combo.sort_values(by='tid', ascending=False)
combo = combo[['tid', 'device', 'fel', 'FW', 'type']]
combo.to_csv((Instrumentnummer +"_"+ timestr+ "-Combo.csv"), index=None, mode='w')
    
#shutil.move (filstart +"_InstrumentLogReport.txt",Instrumentnummer +"_"+timestr+ "-Service.txt")
shutil.rmtree(directory+'\TraceLogs') 
shutil.rmtree(directory+'\ServiceLogs') 

try:
    os.remove(path+'\Combo1.csv')
    os.remove('mellan.csv')
    os.remove(Instrumentnummer+'.csv')
except OSError:
    pass
shutil.move (filstart +"_InstrumentLogReport.txt",Instrumentnummer +"_"+timestr+ "-Service.txt")
#print('oldfile',oldfile)                     
#os.remove(os.path.join(path,oldfile))
root = tkinter.Tk()
messagebox.showinfo("Klart!", ("Trace och service log för instrumentnummer" , Instrumentnummer," finns nu i mappen ",directory))
#print('klart, Trace och service log för instrumentnummer ', Instrumentnummer,' finns nu i mappen ',directory)
root.destroy()
root.mainloop()  
#combo.head(5)


# In[ ]:





# In[ ]:





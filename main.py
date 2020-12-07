import socket
import json
from tkinter.ttk import *
from tkinter import *
import psycopg2
import threading
import platform
pc = platform.node()

camera = ""
getIP = ""
if pc == "AW10264":
    camera = "1E0AZ0NJGQ17"
    getIP = "172.15.41.45:16810"
elif pc == "AW10263":
    camera = "1205Z091Q786"
    getIP = "172.15.40.174:16810"
elif pc == "AW10266":
    camera = "1C1FZ08SKH66"
    getIP = "172.15.41.41:16810"
elif pc == "AW10273":
    camera = "1C19Z0NJGJ17"
    getIP = "172.15.40.246:16810"
elif pc == "DL10149" or pc == "DL10200":
    camera = "0A12Z08SKG66"
    getIP = "172.15.40.154:16810"

print(camera)
x = 0
badgeID = ""
employee = ''
badgeFlag = True
class UDPConnection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.buffersize = 4080
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def connect(self):
        self.client.bind((self.ip, self.port))
        print("connected")
    def close(self):
        self.client.close()
def getTemp(recordID, getIP):
    import requests

    getStr = 'http://'+getIP+'/query?ScanID='+str(recordID)
    r = requests.get(getStr)
    json = r.json()
    results = json["Results"][0]['BodyTemp']
    temp = round(((float(results) * (9.0 / 5.0)) + 32), 2)
    return temp

def listener():
    while True:
        global getIP
        udp = UDPConnection("0.0.0.0", 16811)
        udp.connect()
        global badgeFlag
        print("badge Flag: ", badgeFlag)
        client = udp.client
        print("Threading Opened")
        rec = client.recv(10208)
        recStr = rec.decode("utf-8")
        # data = json.loads(recStr)
        # print(data.get("Message"))
        # print("did it reach here?")
        json_acceptable_string = recStr.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        cameraID = d["CameraID"]
        print(cameraID)
        udp.close()
        print("socket closed")
        if cameraID == camera:
            print(d)
            message = d["Message"]

            ip = d["IPAddress"]
            result = d["Disposition"]
            if result == 1:
                disposition = True
            else:
                disposition = False
            recordID = d["RecordID"]
            t_stamp = d["TimeStamp"]
            temp = getTemp(recordID, getIP)
            # global badgeID
            # badge = badgeID
            # global employee
            # emp = employee


            window = frameDisplay(message, cameraID, ip, disposition, recordID, t_stamp)
            window.mainloop()

            # print("socket closed")
class frameDisplay(Frame):
    def __init__(self, message, cameraID, ip, disposition, recordID, t_stamp):
        self.root = Tk()
        self.root.lift()
        self.root.attributes('-topmost',  True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.message = message
        self.cameraID = cameraID
        self.ip = ip
        self.disposition = disposition
        self.recordID = recordID
        self.t_stamp = t_stamp
        self.root.attributes('-fullscreen',True)
        super().__init__()
        self.initUI()

    def initUI(self):
        self.pack()
        global getIP
        q1 = Label(self, relief = "flat", text = "Have you had any of the following symptoms?", fg = "#ff0000")
        symptoms = Label(self, text =
                              "\n- Congestion/Runny Nose"
                              "\n- Nausea/Vomiting"
                              "\n- Chills/Tremors"
                              "\n- Muscle Pain"
                              "\n- Loss of Taste/Smell"
                              "\n- Fever"
                              "\n- Cough"
                              "\n- Sore Throat"
                              "\n- Shortness of Breath"
                              "\n- Diarrhea"
                              "\n- Headache")
        symptoms.grid(column = 0, columnspan = 2,row = 5, padx = 0, pady =0)
        symptoms.config(font=("Arial", 15, "bold"))
        q1.grid(column = 0, columnspan = 2,row = 4, padx = 0, pady = 0)

        q1.config(font = ("Arial", 22 , "bold", "underline"))
        q2 = Label(self,text = "Have you had contact with someone who has tested positive for COVID-19?\n", fg = "#ff0000")
        q2.config(font = ("Arial", 22, "bold", "underline"))
        q2.grid(column = 0, columnspan = 2, row = 3, padx = 0, pady = 0)
        # q1.pack()
        q3 = Label(self,text = "Have you travelled domestically or internationally in the last 14 days?", fg = "#ff0000")
        q3.config(font = ("Arial", 22, "bold", "underline"))
        q3.grid(column = 0, columnspan = 2, row = 2, padx = 10, pady = 20)
        badgeWarning = Label(self, bg = "#ff0000", fg = "#ffffff", bd = 2, borderwidth = 3, text =
                                                      "By scanning your badge, you are answering NO to all 3 questions above."
                                                    "\nIf you respond YES to any of these questions you are required to see Inalfa HR/Safety before entering the building.")
        badgeWarning.config(font = ("Arial", 17, "bold"))
        badgeWarning.grid(row = 0, column = 0, columnspan = 2, padx = 0, pady = 0)

        closeButton = Button(self, text= "Close", command = self.root.destroy)
        closeButton.grid(column = 1, row = 6, padx = 0)
        closeButton.config(font=("Arial", 24, "bold"))
        temp = getTemp(self.recordID, getIP)
        print("temp:",temp)
        if temp > 99.5:
            tempTextColor = "#e60000"
        else:
            tempTextColor = "#009933"
        tempLabelText = "Temperature: " + str(temp) +" F"
        tempLabel = Label(self, text = tempLabelText, fg = tempTextColor, bd = 2, )
        tempLabel.config(font=("Arial", 22, "bold"))
        tempLabel.grid(column = 0, row = 6, padx = 0, pady = 0)
        contractLabel = Label(self, text = "Contractors/Visitors (or employees without a badge) must \nmanually record "
                                           "their temperature and information with safety/HR"
                                           "\nPress <Spacebar> or the close button to close ID-Scanning app after viewing temperature", bg = "#ffff00")
        contractLabel.config(font = ("Arial", 18, "bold"))
        contractLabel.grid(column = 0, columnspan = 2,row = 7, padx = 0, pady = 0)
        entry = Entry(self)
        entry.config(font=('Arial', 1))
        entry.grid(column = 0, row = 8)
        entry.focus_set()
        entry.focus_force()
        entry.bind("<Return>", (lambda event: func(entry.get(),self, self.message, self.cameraID, self.ip, self.disposition, self.recordID, self.t_stamp, temp)))
        entry.bind("<space>", (lambda event: self.root.destroy()))
        # self.root.after(10000, self.root.destroy())

        # sleep(0.5)
        # entry.bind("<Return>", (lambda event: self.quit()))

        def func(name,self, message, cameraID, ip, disposition, recordID, t_stamp, temp):
            print("getting employee data")
            connection = psycopg2.connect(user="postgres", password="postgres", host="ignition", port="5432",
                                          dbname="postgres")
            cursor = connection.cursor()
            employee_query = """SELECT name FROM employee_information WHERE badge_num = %s"""
            args = (name,)
            cursor.execute(employee_query, args)
            employee = cursor.fetchone()
            if employee is None:
               employee = "No Employee with Badge Number Found"

            badgeName(name, employee)
            insertdata(message, cameraID, ip, disposition, recordID, t_stamp,temp)
            off(self)
        def off(self):
            self.root.destroy()
def insertdata(message, cameraID, ip, disposition, recordID, t_stamp, temp):
    try:
        global badgeID
        global employee
        print("trying to add data")
        connection = psycopg2.connect(user="postgres", password="postgres", host="ignition", port="5432",
                                      dbname="postgres")
        cursor = connection.cursor()
        exists_query = """SELECT * FROM scanner_data WHERE recordID = %s"""
        args = (recordID,)
        cursor.execute(exists_query, args)
        exists = cursor.fetchone()
        print(exists)
        global badgeFlag
        badgeFlag = True
        print("badge flag should be true")
        print("badgeflag3:", badgeFlag)
        if exists is None:
            insert_query = """ INSERT INTO scanner_data(message, cameraid, ip, pass, recordid, t_stamp, badgeid, employee_name, temperature) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            records_to_insert = (message, cameraID, ip, disposition, recordID, t_stamp, badgeID, employee, temp)
            cursor.execute(insert_query, records_to_insert)
            connection.commit()
            count = cursor.rowcount
            print(count, "record inserted")



        else:
            print("entry already exist")
    finally:
        if (connection):
            cursor.close()
        connection.close()
        print("connection terminated")
def socketThreading():
    udp = UDPConnection("0.0.0.0", 16811)
    udp.connect()
    t1 = threading.Thread(target=listener, args=(udp,))
    t1.start()
    print("socket open")

# def dataEntered(x):
#     window = frameDisplay()
#     window.mainloop()
#     x = x+1
def badgeName(name, emp):
    global badgeID
    global employee
    employee = emp
    badgeID = name

    print (badgeID)
    print(employee)
if x == 0:
    # window = frameDisplay()
    # window.mainloop()
    t1 = threading.Thread(target=listener, args=())
    t1.start()

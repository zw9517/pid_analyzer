from tkinter.ttk import *
from tkinter import *
import tkinter as tk
from time import strftime
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import sleep  # Allows us to call the sleep function to slow down our loop
#import RPi.GPIO as GPIO  # Allows us to call our GPIO pins and names it just GPIO
import v

"""
GPIO.setmode(GPIO.BCM)  # Set's GPIO pins to BCM GPIO numbering
INPUT_PIN = 4  # Sets our input pin, in this example I'm connecting our button to pin 4. Pin 0 is the SDA pin so I avoid using it for sensors/buttons
GPIO.setup(INPUT_PIN, GPIO.IN)  # Set our input pin to be an input
"""


Data2 = {'Time': [0,1,2,3,4,5,6,7],
         'PPD Concentration': [43,65,34,45,65,54,66,74]}

df2 = DataFrame(Data2, columns=['Time', 'PPD Concentration'])
df2 = df2[['Time', 'PPD Concentration']].groupby('Time').sum()

#NamedTuple Method = {analysisTime, baselineStartTime, baselineLength, ovenTemp, segmentLength, known_only}
method_factory = {300, 1, 4, 20.00, 5, 0}
#NamedTuple Comp#={compNum, compName, active, reference, compRT, compWindow, responseFactor, calStandard, calibrationFactor }
comp1 = {1, "CH4", 1, 1, 16, 2, 1.00, 100.00, 2.20};
comp2 = {2, "CO", 1, 0, 24, 2, 1.00, 100.00, 1.60};
comp3 = {3, "C2H2", 1, 0, 35, 2, 1.00, 100.00, 0.10};
comp4 = {4, "O2", 1, 0, 55, 2, 1.00, 100.00, 2.40};
comp5 = {5, "H2", 1, 0, 67, 2, 1.00, 100.00, 1.00};
comp6 = {6, "NO", 1, 0, 78, 2, 1.00, 100.00, 1.84};

#NamedTuple Peak#={peakNum, gasName, peakTime, height, concen, calFactor, active known}
peak1 = {1, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak2 = {2, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak3 = {3, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak4 = {4, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak5 = {5, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak6 = {6, "unknown", 0, 0, 0.0, 0.0, 1, 1};

# !/usr/bin/env python



#NamedTuple Data#={date_now, time_now, run_number, peak_number, comp_name, conc, ret_time, site}
data_current = {"00/00/00", "00:00:00", 0, 0, " ? ", -1, 0, 1};

def create_window():
    window = tk.Toplevel(root)
    return window


class PID_analyzer:
    def __init__(self, master):
        self.master = master
        master.title("PID Analyzer")

        self.total = v.tempValue
        self.entered_number = 0

        self.total_label_text = IntVar()
        self.total_label_text.set(self.total)
        self.total_label = Label(master, textvariable=self.total_label_text,font=('calibri', 30, 'bold'),
            background = 'white',
            foreground = 'black')

        self.label = Label(master, text="PPD: ", font=('calibri', 30, 'bold'),
            background = 'white',
            foreground = 'black')

        self.timelabel = Label(master, text="Time is",font=('calibri', 20 ),
            background = 'white',
            foreground = 'black')
        self.lbl = Label(root,font=('calibri', 20 ),
            background = 'white',
            foreground = 'black')


        vcmd = master.register(self.validate) # we have to wrap the command
        self.entry = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.savevalue = Button(master, text="Save", command=lambda: self.savesth())
        self.add_button = Button(master, text="+", command=lambda: self.update("add"))
        self.subtract_button = Button(master, text="-", command=lambda: self.update("subtract"))
        self.reset_button = Button(master, text="Reset", command=lambda: self.update("reset"))
        self.generate_graph = Button(master, text="Generate", command=lambda: self.show_graph())
        self.combobox = Combobox(root)
        self.combobox['values']=('CH4','CO','C2H2','O2','H2','NO')
        self.combobox.current(1)

        # LAYOUT
        self.timelabel.grid(row=0, column=0)
        self.lbl.grid(row=0, column=1)
        self.time()
        self.label.grid(row=1, column=0, sticky=W)
        self.total_label.grid(row=1, column=1)
        self.entry.grid(row=2, column=0, columnspan=3, sticky=W+E)
        self.add_button.grid(row=3, column=0)
        self.subtract_button.grid(row=3, column=1)
        self.reset_button.grid(row=3, column=2, sticky=W+E)
        self.generate_graph.grid(row=4,column=0)
        self.combobox.grid(row=4,column=1)
        self.savevalue.grid(row=5,column=2)

    def time(self):
        string = strftime('%H:%M:%S %p')
        self.lbl.config(text=string)
        self.lbl.after(1000, self.time)

    def validate(self, new_text):
        if not new_text:
            self.entered_number = 0
            return True

        try:
            self.entered_number = int(new_text)
            return True
        except ValueError:
            return False


    def show_graph(self):
        figure2 = plt.Figure(figsize=(5, 3), dpi=100)
        ax2 = figure2.add_subplot(111)
        line2 = FigureCanvasTkAgg(figure2, create_window())
        line2.get_tk_widget().grid(row=5,column=0)
        df2.plot(kind='line', legend=True, ax=ax2, color='r', marker='o', fontsize=10)
        ax2.set_title('Time Vs. PPD Concentration')

    def update(self, method):
        if method == "add":
            self.total += self.entered_number
        elif method == "subtract":
            self.total -= self.entered_number
        else: # reset
            self.total = 0

        self.total_label_text.set(self.total)
        self.entry.delete(0, END)

    def makeMea(self):
        """
        while True:
           if (GPIO.input(INPUT_PIN) == True): # Physically read the pin now
                    print('3.3')
           else:
                    print('0')
           sleep(1);
        """

    def savesth(self):
        top=Toplevel()
        l1=Label(top,text="file name")
        l1.pack(side = LEFT)
        e1=Entry(top,bd=5)
        e1.pack(side=LEFT)
        frame = Frame(top)
        frame.pack()
        top.mainloop()

        x = np.linspace(0,1,201)
        y = np.random.random(201)
        header = "X-Column, Y-Column\n"
        header += "This is a second line"
        f=open(e1,'wb')
        np.savetxt(f,[],header=header)
        for i in range(201):
            data = np.column_stack((x[i],y[i]))
            np.savetxt(f,data)
        f.close()

"""
    def m_setup(self):
        #initialize
        if(!setupFinished) return
"""

root = Tk()
root.title("welcome to PID")
root.geometry('325x170')
my_gui = PID_analyzer(root)
root.mainloop()
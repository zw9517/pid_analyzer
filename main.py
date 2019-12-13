from tkinter.ttk import *
from tkinter import *
import tkinter as tk
import time
from time import strftime, sleep
from datetime import datetime
import numpy as np
import os
from random import uniform
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import socket
import ssl
from pandas.plotting import register_matplotlib_converters

# import RPi.GPIO as GPIO  # Allows us to call our GPIO pins and names it just GPIO
# import v

"""
GPIO.setmode(GPIO.BCM)  # Set's GPIO pins to BCM GPIO numbering
INPUT_PIN = 4  # Sets our input pin, in this example I'm connecting our button to pin 4. Pin 0 is the SDA pin so I avoid using it for sensors/buttons
GPIO.setup(INPUT_PIN, GPIO.IN)  # Set our input pin to be an input
"""

"""
Data2 = {'Time': [0,1,2,3,4,5,6,7],
         'PPD Concentration': [43,65,34,45,65,54,66,74]}

df2 = DataFrame(Data2, columns=['Time', 'PPD Concentration'])
df2 = df2[['Time', 'PPD Concentration']].groupby('Time').sum()
"""

# NamedTuple Method = {analysisTime, baselineStartTime, baselineLength, ovenTemp, segmentLength, known_only}
method_factory = {300, 1, 4, 20.00, 5, 0}
# NamedTuple Comp#={compNum, compName, active, reference, compRT, compWindow, responseFactor, calStandard, calibrationFactor }
comp1 = {1, "CH4", 1, 1, 16, 2, 1.00, 100.00, 2.20};
comp2 = {2, "CO", 1, 0, 24, 2, 1.00, 100.00, 1.60};
comp3 = {3, "C2H2", 1, 0, 35, 2, 1.00, 100.00, 0.10};
comp4 = {4, "O2", 1, 0, 55, 2, 1.00, 100.00, 2.40};
comp5 = {5, "H2", 1, 0, 67, 2, 1.00, 100.00, 1.00};
comp6 = {6, "NO", 1, 0, 78, 2, 1.00, 100.00, 1.84};

# NamedTuple Peak#={peakNum, gasName, peakTime, height, concen, calFactor, active known}
peak1 = {1, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak2 = {2, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak3 = {3, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak4 = {4, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak5 = {5, "unknown", 0, 0, 0.0, 0.0, 1, 1};
peak6 = {6, "unknown", 0, 0, 0.0, 0.0, 1, 1};

# !/usr/bin/env python

dummy = []
timeser = []
dummy_index =[]
# NamedTuple Data#={date_now, time_now, run_number, peak_number, comp_name, conc, ret_time, site}
data_current = {"00/00/00", "00:00:00", 0, 0, " ? ", -1, 0, 1};


def create_window():
    window = tk.Toplevel(root)
    return window


class PID_analyzer:
    def __init__(self, master):
        self.master = master
        master.title("PID Analyzer")

        self.total = 24.0
        self.entered_number = 0
        large_textsize = 30
        medium_textsize = 20

        self.total_label_text = IntVar()
        self.total_label_text.set(self.total)
        self.total_label = Label(master, textvariable=self.total_label_text, font=('calibri', 30, 'bold'),
                                 background='black',
                                 foreground='white')

        self.label = Label(master, text="PPD: ", font=('calibri', large_textsize, 'bold'),
                           background='black',
                           foreground='white')

        self.timelabel = Label(master, text="Time is", font=('calibri', medium_textsize),
                               background='black',
                               foreground='white')
        self.lbl = Label(root, font=('calibri', medium_textsize),
                         background='black',
                         foreground='white')

        vcmd = master.register(self.validate)  # we have to wrap the command
        self.entry = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.savevalue = Button(master, text="Save", command=lambda: self.savesth())
        self.add_button = Button(master, text="+", command=lambda: self.update("add"))
        self.startmeasure = Button(master, text="measure", command=lambda: self.measure())
        self.subtract_button = Button(master, text="-", command=lambda: self.update("subtract"))
        self.reset_button = Button(master, text="Reset", command=lambda: self.update("reset"))
        self.awsupload = Button(master, text="Upload", command=lambda: self.awsupload(dummy))
        self.generate_graph = Button(master, text="Generate", command=lambda: self.show_graph(dummy, timeser))
        self.combobox = Combobox(root)
        self.combobox['values'] = ('CH4', 'CO', 'C2H2', 'O2', 'H2', 'NO')
        self.combobox.current(1)

        # LAYOUT
        self.timelabel.grid(row=0, column=0)
        self.lbl.grid(row=0, column=1)
        self.time()
        self.label.grid(row=1, column=0, sticky=W)
        self.total_label.grid(row=1, column=1)
        self.startmeasure.grid(row=1, column=2)

        self.entry.grid(row=2, column=0, columnspan=3, sticky=W + E)

        self.add_button.grid(row=3, column=0)
        self.subtract_button.grid(row=3, column=1)
        self.reset_button.grid(row=3, column=2, sticky=W + E)
        self.generate_graph.grid(row=4, column=0)
        self.combobox.grid(row=4, column=1)
        self.savevalue.grid(row=5, column=1)
        self.awsupload.grid(row=5, column=2)

    def time(self):
        string = strftime('%H:%M:%S %p')
        self.lbl.config(text=string)
        self.lbl.after(1000, self.time)

    def calibrate(self):
        print("use certain gas")
        time.sleep(5)  # run a countdown
        sensorinput = 1
        calfactor1 = sensorinput
        time.sleep(5)  # run a countdown
        sensorinput = 2
        calfactor2 = sensorinput
        # use calfactors to calibrate the system

    def measure(self):
        """
        while True:
           if (GPIO.input(INPUT_PIN) == True): # Physically read the pin now
                    print('3.3')
           else:
                    print('0')
           sleep(1);
        """
        # take sensor measurement and write to a csv file.

        file = open("data_log.csv", "a")
        i = 0
        if os.stat("data_log.csv").st_size == 0:
            file.write("Time,Sensor1,Sensor2,Sensor3,Sensor4,Sensor5\n")
        while i < 10:
            i = i + 1
            now = datetime.now()
            timereading = uniform(20.0, 25.0)
            file.write(str(now) + "," + str(timereading) + "," + str(timereading) + "," + str(i - 10) + "," + str(
                i + 5) + "," + str(
                i * i) + "\n")
            file.flush()
            dummy.append(timereading)
            timeser.append(now)
            sleep(0.1)
        return dummy, timeser



    def validate(self, new_text):
        if not new_text:
            self.entered_number = 0
            return True

        try:
            self.entered_number = int(new_text)
            return True
        except ValueError:
            return False

    def show_graph(self, dummy, timeser):
        """
        figure2 = plt.Figure(figsize=(5, 3), dpi=100)
        ax2 = figure2.add_subplot(111)
        line2 = FigureCanvasTkAgg(figure2, create_window())
        line2.get_tk_widget().grid(row=5,column=0)
        df2.plot(kind='line', legend=True, ax=ax2, color='r', marker='o', fontsize=10)
        ax2.set_title('Time Vs. PPD Concentration')
        """

        # t = np.arange(0.0, 2.0, 0.01)
        # s = 1 + np.sin(2 * np.pi * t)
        # print(type(t))
        # print(type(dummy))
        #
        # fig, ax = plt.subplots()
        # ax.plot(timeser, dummy)
        # fig.savefig("test.png")
        # plt.show()

        ax = plt.subplot(111)

        dummy_ind = range(0, len(dummy))
        line, = plt.plot(dummy_ind, dummy, lw=2)
        b = max(dummy)
        a = dummy.index(b)
        plt.annotate('local max is at %d and %d'%(a, b), xy=(a, b), xytext=(a+1, b+1),
                     arrowprops=dict(facecolor='black', shrink=0.05),
                     )

        plt.ylim(20,30)
        plt.show()


        # ax = plt.subplot(111)
        #
        #
        #
        # dummy_ind = range(0, len(dummy))
        # line, = plt.plot(dummy_ind, dummy, lw=2)
        #
        # max_dummy = min(dummy)
        # max_index = dummy.index(max_dummy)
        #
        # print(max_dummy, dummy_ind[max_index])
        #
        # plt.annotate('local max', xy=(max_dummy, dummy_ind[max_index]), xytext=(max_dummy, dummy_ind[max_index]),
        #              arrowprops=dict(facecolor='black'),)
        #
        # plt.ylim(0, 50)
        #
        # plt.show()

    def update(self, method):
        if method == "add":
            self.total += self.entered_number
        elif method == "subtract":
            self.total -= self.entered_number
        else:  # reset
            self.total = 0

        self.total_label_text.set(self.total)
        self.entry.delete(0, END)

    def savesth(self):
        top = Toplevel()
        l1 = Label(top, text="file name")
        l1.pack(side=LEFT)
        e1 = Entry(top, bd=5)
        e1.pack(side=LEFT)
        frame = Frame(top)
        frame.pack()
        top.mainloop()

        x = np.linspace(0, 1, 201)
        y = np.random.random(201)
        header = "X-Column, Y-Column\n"
        header += "This is a second line"
        f = open(e1, 'wb')
        np.savetxt(f, [], header=header)
        for i in range(201):
            data = np.column_stack((x[i], y[i]))
            np.savetxt(f, data)
        f.close()


root = Tk()
root.title("welcome to PID")
root.configure(background="black")
root.geometry('400x300')
my_gui = PID_analyzer(root)
root.mainloop()

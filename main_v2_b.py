import numpy as np
import time
import matplotlib
import matplotlib.figure as figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from random import uniform
import datetime as dt
import os
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import pylab

#import paho.mqtt.client as paho
import ssl
#import Adafruit_ADS1x15

#adc = Adafruit_ADS1x15.ADS1115()

GAIN = 1


# def on_connect(client, userdata, flags, rc):  # func for making connection
#     global connflag
#     print("Connected to AWS")
#     connflag = True
#     print("Connection returned result: " + str(rc))
# def on_message(client, userdata, msg):  # Func for Sending msg
#     print(msg.topic + " " + str(msg.payload))
# connflag = False
# mqttc = paho.Client()  # mqttc object
# mqttc.on_connect = on_connect  # assign on_connect func
# mqttc.on_message = on_message  # assign on_message func
# awshost = "a1hvrmjbeiu1pl-ats.iot.us-east-2.amazonaws.com"
# awsport = 8883
# cliendId = "pid01"
# thingName = "pid01"
# caPath = "root-CA.crt"
# certPath = "pid01.cert.pem"
# keyPath = "pid01.private.key"
# mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2,
#               ciphers=None)  # pass parameters
# mqttc.connect(awshost, awsport, keepalive=60)  # connect to aws server
# mqttc.loop_start()
# if connflag == True:
#     print("connected")
# else:
#     print("waiting for connection")
# Parameters
update_interval = 10  # Time (ms) between polling/animation updates
max_elements = 40  # Maximum number of elements to store in plot lists
root = None
dfont = None
frame = None
canvas = None
ax1 = None
temp_plot_visible = None
dtime = []
# Global variable to remember various states
fullscreen = False
temp_plot_visible = True
light_plot_visible = True


class Demo1:
    def __init__(self, master):
        xs = []
        sensor1_array = []
        global temp_c
        temp_c = tk.DoubleVar()
        global aveg
        aveg = tk.DoubleVar()
        self.max_temp_c = tk.DoubleVar()
        self.sensor1_array = sensor1_array
        self.xs = xs
        self.max_count = 0
        self.max_temp = 0
        self.state = tk.BooleanVar()
        self.state.set(False)
        self.dfont = tkFont.Font(size=-20)
        self.nfont = tkFont.Font(size=-36)
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.configure(background = 'black')
        self.start = time.monotonic()
        for w in self.frame.winfo_children():
            w.grid(padx=5, pady=5)
        # Layout
        self.textc = '#4cf55a'
        self.choices = {'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5'}
        self.choice = tk.StringVar()
        self.choice.set('Sensor1')
        self.label_disp = tk.Label(self.frame, textvariable=self.choice, font=self.dfont, fg=self.textc,bg='black').grid(row=0, column=1)
        self.label_temp = tk.Label(self.frame, textvariable=temp_c, font=self.nfont, fg=self.textc, bg='black',).grid(row=0, column=2)
        self.label_aveg = tk.Label(self.frame, textvariable=aveg, font=self.nfont, fg=self.textc, bg='black',).grid(row=0, column=4)
        self.label_unit = tk.Label(self.frame, text='unit', font=self.dfont, fg=self.textc, bg='black').grid(row=0, column=3)
        self.peak = tk.Text(self.frame, height =5, width =40, font=tkFont.Font(size=-15), fg=self.textc, bg='black')
        self.peak.grid(row=5, column=0, columnspan=5)
        self.button_calibrate = tk.Button(self.frame, text='Calibrate', font=self.dfont, fg=self.textc, bg='black', width=8,
                                          command=self.new_window).grid(row=6, column=0)
        self.button_pause = tk.Button(self.frame, text='Pause', font=self.dfont, fg=self.textc, bg='black', width=8,
                                      command=lambda: self.dpause()).grid(row=6, column=1)
        self.button_resume = tk.Button(self.frame, text='Resume', font=self.dfont,fg=self.textc, bg='black', width=8,
                                       command=lambda: self.dstart()).grid(row=6, column=2)
        self.button_makeplot = tk.Button(self.frame, text='Make plot', font=self.dfont, fg=self.textc, bg='black', width=8,
                                         command=lambda: self.make_plot()).grid(row=6, column=3)
        self.button_save = tk.Button(self.frame, text='Save', font=self.dfont, fg=self.textc, bg='black', width=8,
                                     command=lambda: self.dsave()).grid(row=6, column=4)

        self.frame.pack(fill=tk.BOTH, expand=1)
        # make figure animation
        self.fig = figure.Figure(figsize=(5, 3))
        self.fig.subplots_adjust(left=0.1, right=0.9)
        self.ax1 = self.fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_plot = self.canvas.get_tk_widget()
        self.canvas_plot.grid(row=1, column=0, rowspan=3, columnspan=5, sticky=tk.W + tk.E + tk.N + tk.S)
        self.fargs = (ax1, xs, sensor1_array, temp_c)
        self.ani = animation.FuncAnimation(self.fig, self.animate, fargs=self.fargs, interval=update_interval)

    def run(self):
        print("run")

    def dpause(self):
        self.ani.event_source.stop()

    def dstart(self):
        self.ani.event_source.start()

    def upload(self):
        from subprocess import Popen
        Popen(["python", "aws_publish.py"])
        pass

    def dsave(self):
        self.file = open("data_log.csv", "a")
        if os.stat("data_log.csv").st_size == 0:
            self.file.write("Time,Sensor1\n")
        i = 0
        while i < len(self.sensor1_array):
            self.file.write(str(self.xs[i]) + ","
                            + str(self.sensor1_array[i]) + "\n")
            i = i + 1
            self.file.flush()
        print("saved")

    def new_window(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Calibrate(self.newWindow)

    def make_plot(self):
        ax = plt.subplot(111)
        line, = plt.plot(self.xs, self.sensor1_array, "-o", lw=2, color='tab:green')
        max_data = max(self.sensor1_array)
        max_time_index = self.sensor1_array.index(max_data)
        max_time = mdates.num2date(self.xs[max_time_index])
        formatter = matplotlib.ticker.FuncFormatter(lambda s, x: time.strftime('%M:%S', time.gmtime(s)))
        ax.xaxis.set_major_formatter(formatter)
        ax.annotate('local max', xy=(max_time, max_data), xytext=(0, max_data + 1),
                    arrowprops=dict(facecolor='black', shrink=0.05), )
        ax.set_title('The reading vs. time')
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Reading()')
        ax.grid(True)
        plt.show()

    def animate(self, i, ax1, xs, temps, temp_c):
        try:
            #new_temp = adc.read_adc(0, gain=GAIN)
            new_temp = round(uniform(20.0, 25.0), 2)
        except:
            pass
        #        if new_temp > self.max_temp_c.get():
        #            self.max_temp_c.set(new_temp)
        #        print(self.max_temp_c.get())
        temp_c.set(new_temp)
        now = time.monotonic()-self.start
        xs.append(now)
        temps.append(new_temp)
        xs = xs[-max_elements:]
        temps = temps[-max_elements:]
        if new_temp > 30:
            if new_temp > self.max_temp and self.max_count<20:
                self.max_temp = new_temp
                self.max_count = self.max_count-1
            elif self.max_count>20:
                print(self.max_temp)
                self.max_count = 0
            elif temp_c < self.max_temp:
                self.max_count=self.max_count+1
        self.ax1.clear()
        self.ax1.grid()
        self.ax1.set_ylabel('Sensor1 Data', color='green')
        self.ax1.tick_params(axis='y', labelcolor='green')
        self.ax1.set_facecolor('black')
        self.ax1.fill_between(xs, temps, 0, linewidth=2, color='green', alpha=0.5)
        formatter = matplotlib.ticker.FuncFormatter(lambda s, x: time.strftime('%M:%S', time.gmtime(s)))
        self.ax1.xaxis.set_major_formatter(formatter)
        self.ax1.collections[0].set_visible(temp_plot_visible)
        # AWS
        # mqttc.publish("PID value", new_temp, qos=1)        # topic: temperature # Publishing Temperature values
        # print("msg sent: pid " + "%.2f" % new_temp ) # Print sent temperature msg on console


class Calibrate:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        master.geometry("500x400")
        self.frame.configure(bg='white')
        self.dfont = tkFont.Font(size=-20)
        self.nfont = tkFont.Font(size=-36)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.calib_temp1 = tk.DoubleVar()
        self.calib_temp2 = tk.DoubleVar()
        self.calib_factor1 = tk.DoubleVar()
        self.calib_factor2 = tk.DoubleVar()
        self.calib_temp1.set(0.00)
        self.calib_temp2.set(0.00)

        self.label_name = tk.Label(self.frame, text="The reading is ", font=self.dfont, bg='white').grid(row=0,
                                                                                                         column=0)
        self.label_data = tk.Label(self.frame, textvariable=temp_c, font=self.nfont, bg='white').grid(row=0, column=1,
                                                                                                      columnspan=5)
        self.label_calib1 = tk.Label(self.frame, textvariable=self.calib_temp1, font=self.dfont, bg='white').grid(row=1,
                                                                                                                  column=1)
        self.label_calib2 = tk.Label(self.frame, textvariable=self.calib_temp2, font=self.dfont, bg='white').grid(row=2,
                                                                                                                  column=1)
        self.button_data1 = tk.Button(self.frame, text="data point 1", font=self.dfont,
                                      command=lambda: self.setdata(1)).grid(row=1, column=0)
        self.button_data2 = tk.Button(self.frame, text="data point 2", font=self.dfont,
                                      command=lambda: self.setdata(2)).grid(row=2, column=0)
        self.confirmButton = tk.Button(self.frame, text='Confirm', font=self.dfont, width=15,
                                       command=self.confirm).grid(row=3, column=0)
        self.quitButton = tk.Button(self.frame, text='Quit', font=self.dfont, width=15,
                                    command=self.close_windows).grid(row=3, column=1)
        self.frame.pack()

    def setdata(self, i):
        if i == 1:
            self.calib_temp1.set(temp_c.get())
        else:
            if i == 2:
                self.calib_temp2.set(temp_c.get())

    def confirm(self):
        self.calib_factor1.set(self.calib_temp1)
        self.calib_factor2.set(self.calib_temp2)
        self.master.destroy()

    def close_windows(self):
        self.master.destroy()


def main():
    root = tk.Tk()
    app = Demo1(root)
    root.title("PID Analyzer")
    root.geometry('500x500')
    root.mainloop()


if __name__ == '__main__':
    main()



import numpy as np
import time
from scipy import integrate
from scipy import optimize
import scipy as scipy
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
import paho.mqtt.client as paho
import ssl
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115()

GAIN = 1


def on_connect(client, userdata, flags, rc):  # func for making connection
    global connflag
    print("Connected to AWS")
    connflag = True
    print("Connection returned result: " + str(rc))


def on_message(client, userdata, msg):  # Func for Sending msg
    print(msg.topic + " " + str(msg.payload))


connflag = False
mqttc = paho.Client()  # mqttc object
mqttc.on_connect = on_connect  # assign on_connect func
mqttc.on_message = on_message  # assign on_message func
awshost = "a1hvrmjbeiu1pl-ats.iot.us-east-2.amazonaws.com"
awsport = 8883
cliendId = "pid01"
thingName = "pid01"
caPath = "root-CA.crt"
certPath = "pid01.cert.pem"
keyPath = "pid01.private.key"
mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2,
              ciphers=None)  # pass parameters
mqttc.connect(awshost, awsport, keepalive=60)  # connect to aws server
mqttc.loop_start()
if connflag == True:
    print("connected")
else:
    print("waiting for connection")
# Parameters
update_interval = 10  # Time (ms) between polling/animation updates
max_elements = 400  # Maximum number of elements to store in plot lists
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
        self.temparray = []
        self.maxdata_arr = []
        self.maxtime_arr = []
        self.max_temp_c = tk.DoubleVar()
        self.sensor1_array = sensor1_array
        self.xs = xs
        self.sum = 0
        self.fall_count = 0
        self.max_temp = 0
        self.rise_count = 0
        self.max_time = 0
        self.noise = 0
        self.state = tk.BooleanVar()
        self.state.set(False)
        self.dfont = tkFont.Font(size=-20)
        self.nfont = tkFont.Font(size=-36)
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.configure(background='black')
        self.start = time.monotonic()
        for w in self.frame.winfo_children():
            w.grid(padx=5, pady=5)
        # Layout
        self.textc = '#4cf55a'
        self.choices = {'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5'}
        self.choice = tk.StringVar()
        self.choice.set('Sensor1')
        self.label_disp = tk.Label(self.frame, textvariable=self.choice, font=self.dfont, fg=self.textc,
                                   bg='black').grid(row=0, column=1)
        self.label_temp = tk.Label(self.frame, textvariable=temp_c, font=self.nfont, fg=self.textc, bg='black', ).grid(
            row=0, column=2)
        self.label_aveg = tk.Label(self.frame, textvariable=aveg, font=self.nfont, fg=self.textc, bg='black', ).grid(
            row=0, column=4)
        self.label_unit = tk.Label(self.frame, text='unit', font=self.dfont, fg=self.textc, bg='black').grid(row=0,
                                                                                                             column=3)
        self.peak = tk.Text(self.frame, height=5, width=40, font=tkFont.Font(size=-15), fg=self.textc, bg='black')
        self.peak.grid(row=5, column=0, columnspan=5)
        self.button_calibrate = tk.Button(self.frame, text='Calibrate', font=self.dfont, fg=self.textc, bg='black',
                                          width=8,
                                          command=self.new_window).grid(row=6, column=0)
        self.button_pause = tk.Button(self.frame, text='Pause', font=self.dfont, fg=self.textc, bg='black', width=8,
                                      command=lambda: self.dpause()).grid(row=6, column=1)
        self.button_resume = tk.Button(self.frame, text='Resume', font=self.dfont, fg=self.textc, bg='black', width=8,
                                       command=lambda: self.dstart()).grid(row=6, column=2)
        self.button_makeplot = tk.Button(self.frame, text='Make plot', font=self.dfont, fg=self.textc, bg='black',
                                         width=8,
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

    def _1gaussian(self, x, amp1, cen1, sigma1):
        return amp1 * (1 / (sigma1 * (np.sqrt(2 * np.pi)))) * (np.exp((-1.0 / 2.0) * (((T - cen1) / sigma1) ** 2)))

    def _2gaussian(self, x, amp1, cen1, sigma1, amp2, cen2, sigma2):
        return amp1 * (1 / (sigma1 * (np.sqrt(2 * np.pi)))) * (np.exp((-1.0 / 2.0) * (((T - cen1) / sigma1) ** 2))) + \
               amp2 * (1 / (sigma2 * (np.sqrt(2 * np.pi)))) * (np.exp((-1.0 / 2.0) * (((T - cen2) / sigma2) ** 2)))

    def _1Lorentzian(self, x, amp, cen, wid):
        return amp * wid ** 2 / ((x - cen) ** 2 + wid ** 2)

    def _2Lorentzian(self, x, amp1, cen1, wid1, amp2, cen2, wid2):
        return (amp1 * wid1 ** 2 / ((x - cen1) ** 2 + wid1 ** 2)) + \
               (amp2 * wid2 ** 2 / ((x - cen2) ** 2 + wid2 ** 2))

    def _3Lorentzian(self, x, amp1, cen1, wid1, amp2, cen2, wid2, amp3, cen3, wid3):
        return (amp1 * wid1 ** 2 / ((x - cen1) ** 2 + wid1 ** 2)) + \
               (amp2 * wid2 ** 2 / ((x - cen2) ** 2 + wid2 ** 2)) + \
               (amp3 * wid3 ** 2 / ((x - cen3) ** 2 + wid3 ** 2))

    def _4Lorentzian(self, x, amp1, cen1, wid1, amp2, cen2, wid2, amp3, cen3, wid3):
        return (amp1 * wid1 ** 2 / ((x - cen1) ** 2 + wid1 ** 2)) + \
               (amp2 * wid2 ** 2 / ((x - cen2) ** 2 + wid2 ** 2)) + \
               (amp3 * wid3 ** 2 / ((x - cen3) ** 2 + wid3 ** 2)) + \
               (amp4 * wid4 ** 2 / ((x - cen4) ** 2 + wid4 ** 2))

    def make_plot(self):
        ax = plt.subplot(111)
        raw = self.sensor1_array
        disp_data = [i - self.noise for i in raw]
        # Dislay the data
        line, = plt.plot(self.xs, disp_data, "ro", lw=2, color='tab:red')
        formatter = matplotlib.ticker.FuncFormatter(lambda s, x: time.strftime('%M:%S', time.gmtime(s)))
        ax.xaxis.set_major_formatter(formatter)
        ax.set_title('The reading vs. time')
        ax.set_xlabel('Time mm/ss')
        ax.set_ylabel('Reading()')
        ax.grid(True)

        # Peak Seperation
        if len(self.maxdata_arr) == 2:
            self.popt_lorentz, self.pcov_lorentz = scipy.optimize.curve_fit(self._2Lorentzian, self.xs, disp_data,
                                                                            p0=[self.maxdata_arr[0],
                                                                                self.maxtime_arr[0], 5,
                                                                                self.maxdata_arr[1],
                                                                                self.maxtime_arr[1], 5])

        self.perr_lorentz = np.sqrt(np.diag(self.pcov_lorentz))

        pars_1 = self.popt_lorentz[0:3]
        pars_2 = self.popt_lorentz[3:6]
        lorentz_peak_1 = self._1Lorentzian(self.xs, *pars_1)
        lorentz_peak_2 = self._1Lorentzian(self.xs, *pars_2)

        line, = plt.plot(self.xs, self._2Lorentzian(self.xs, *self.popt_lorentz), "k--")

        # peak 1
        plt.plot(self.xs, lorentz_peak_1, "g")
        plt.fill_between(self.xs, lorentz_peak_1.min(), lorentz_peak_1, facecolor="green", alpha=0.5)

        # peak 2
        plt.plot(self.xs, lorentz_peak_2, "y")
        plt.fill_between(self.xs, lorentz_peak_2.min(), lorentz_peak_2, facecolor="yellow", alpha=0.5)

        i_simp_1 = integrate.simps(lorentz_peak_1, self.xs)
        i_simp_2 = integrate.simps(lorentz_peak_2, self.xs)

        isimp = []
        isimp.append(i_simp_1)
        isimp.append(i_simp_2)
        # annotation
        for i in range(len(self.maxdata_arr)):
            ax.annotate('The Max is %d. \n The retention time is %d s. \n The area is %d.'
                        % (self.maxdata_arr[i], self.maxtime_arr[i], isimp[i]),
                        xy=(self.maxtime_arr[i] + 0.5, self.maxdata_arr[i] / 1.5),
                        xytext=(self.maxtime_arr[i] + 2.5, self.maxdata_arr[i] / 1.5 + 5),
                        arrowprops=dict(facecolor='black', shrink=0.05), )

        plt.show()

    def animate(self, i, ax1, xs, temps, temp_c):
        try:
            new_reading = adc.read_adc(0, gain=GAIN)
            # new_temp = round(uniform(20.0, 25.0), 2)
        except:
            pass
        if len(self.temparray) < 5:
            self.temparray.append(new_reading)
        else:
            self.temparray.pop(0)
            self.temparray.append(new_reading)
        new_temp = np.mean(self.temparray)
        temp_c.set('%.2f' % new_temp)
        now = time.monotonic() - self.start
        xs.append(now)
        temps.append(new_temp)

        # Integration
        # self.integrsimp = integrate.simps(temps,xs)
        # self.integrtrap = np.trapz(temps,xs)
        # self.sum = self.sum + new_temp*0.2
        xs = xs[-max_elements:]
        temps = temps[-max_elements:]
        if len(temps) == 1:
            self.peak.insert(tk.END, "Wait for calibration... \n")

        if len(temps) == 30:
            self.noise = np.mean(temps)
            self.peak.insert(tk.END, "Noise is %d. Ready to measure.\n" % (self.noise))
        if new_temp > 20:
            if new_temp > self.max_temp:
                self.max_temp = new_temp
                self.fall_count -= 1
                self.max_time = now
                self.rise_count += 1
            elif new_temp < self.max_temp and self.fall_count > 10:
                self.max_temp = 0
                self.fall_count = 0
            elif self.fall_count > 7 and self.rise_count > 4:
                self.fall_count = 0
                self.rise_count = 0
                self.maxdata_arr.append(self.max_temp)
                self.maxtime_arr.append(self.max_time)
                self.peak.insert(tk.END, "Found max at %d @ %d s.\n" % (self.max_temp, self.max_time))
                self.max_temp = 0
            elif temp_c.get() < self.max_temp:
                self.fall_count += 1
                if self.rise_count > 0 and self.rise_count < 5:
                    self.rise_count -= 1

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
    root.geometry('700x500')
    root.mainloop()


if __name__ == '__main__':
    main()



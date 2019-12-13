import datetime as dt
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *

import tkinter.font as tkFont
from random import uniform
import matplotlib.figure as figure
import matplotlib.animation as animation
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

###############################################################################
# Parameters and global variables

# Parameters
update_interval = 60  # Time (ms) between polling/animation updates
max_elements = 1440  # Maximum number of elements to store in plot lists

# Declare global variables
root = None
dfont = None
frame = None
canvas = None
ax1 = None
temp_plot_visible = None

dummy = []
dtime = []
# Global variable to remember various states
fullscreen = False
temp_plot_visible = True
light_plot_visible = True


###############################################################################
# Functions

# Toggle fullscreen
def toggle_fullscreen(event=None):
    global root
    global fullscreen

    # Toggle between fullscreen and windowed modes
    fullscreen = not fullscreen
    root.attributes('-fullscreen', fullscreen)
    resize(None)


# Return to windowed mode
def end_fullscreen(event=None):
    global root
    global fullscreen

    # Turn off fullscreen mode
    fullscreen = False
    root.attributes('-fullscreen', False)
    resize(None)


# Automatically resize font size based on window size
def resize(event=None):
    global dfont
    global frame

    # Resize font based on frame height (minimum size of 12)
    # Use negative number for "pixels" instead of "points"
    new_size = -max(12, int((frame.winfo_height() / 20)))
    dfont.configure(size=new_size)


# Toggle the temperature plot
def toggle_temp():
    global canvas
    global ax1
    global temp_plot_visible

    # Toggle plot and axis ticks/label
    temp_plot_visible = not temp_plot_visible
    ax1.collections[0].set_visible(temp_plot_visible)
    ax1.get_yaxis().set_visible(temp_plot_visible)
    canvas.draw()


# Toggle the light plot
def toggle_light():
    global canvas
    global ax2
    global light_plot_visible

    # Toggle plot and axis ticks/label
    light_plot_visible = not light_plot_visible
    ax2.get_lines()[0].set_visible(light_plot_visible)
    ax2.get_yaxis().set_visible(light_plot_visible)
    canvas.draw()


# save the data to csv
def dsave():
    file = open("data_log.csv", "a")
    if os.stat("data_log.csv").st_size == 0:
        file.write("Time,Sensor1,Sensor2\n")
    i = 0
    while i < len(temps):
        file.write(str(xs[i]) + ","
                   + str(temps[i]) + ","
                   + str(lights[i]) + "\n")
        i = i + 1
        file.flush()


def dpause():
    pass


def run():
    print(gas_select.get())
    var.set(gas_select.get())


# This function is called periodically from FuncAnimation
def animate(i, ax1, ax2, xs, temps, lights, temp_c, lux):
    # Update data to display temperature and light values
    try:
        new_temp = round(uniform(20.0, 25.0), 2)
        new_lux = round(uniform(0.0, 5.0), 1)
    except:
        pass

    # Update our labels
    temp_c.set(new_temp)
    lux.set(new_lux)

    # Append timestamp to x-axis list
    timestamp = mdates.date2num(dt.datetime.now())
    xs.append(timestamp)

    # Append sensor data to lists for plotting
    temps.append(new_temp)
    lights.append(new_lux)

    # Limit lists to a set number of elements
    xs = xs[-max_elements:]
    temps = temps[-max_elements:]
    lights = lights[-max_elements:]

    # Clear, format, and plot light values first (behind)
    color = 'tab:red'
    ax1.clear()
    ax1.grid()
    ax1.set_ylabel('Temperature (C)', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.fill_between(xs, temps, 0, linewidth=2, color=color, alpha=0.3)

    # Clear, format, and plot temperature values (in front)
    color = 'tab:blue'
    ax2.clear()
    ax2.set_ylabel('Light (lux)', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.plot(xs, lights, linewidth=2, color=color)

    # Format timestamps to be more readable
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()

    # Make sure plots stay visible or invisible as desired
    ax1.collections[0].set_visible(temp_plot_visible)
    ax2.get_lines()[0].set_visible(light_plot_visible)


# Dummy function prevents segfault
def _destroy(event):
    pass


###############################################################################
# Main script

# Create the main window
root = tk.Tk()
root.title("Sensor Dashboard")

# Create the main container
frame = tk.Frame(root)
frame.configure(bg='white')

# Lay out the main container (expand to fit window)
frame.pack(fill=tk.BOTH, expand=1)

# Create figure for plotting
fig = figure.Figure(figsize=(2, 2))
fig.subplots_adjust(left=0.1, right=0.8)
ax1 = fig.add_subplot(1, 1, 1)

# Instantiate a new set of axes that shares the same x-axis
ax2 = ax1.twinx()

# Empty x and y lists for storing data to plot later
xs = []
temps = []
lights = []

# Variables for holding temperature and light data
temp_c = tk.DoubleVar()
lux = tk.DoubleVar()

# Create dynamic font for text
dfont = tkFont.Font(size=-24)

# Create a Tk Canvas widget out of our figure
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas_plot = canvas.get_tk_widget()

# Create other supporting widgets
gas_select = ttk.Combobox(frame,
                          values=["Sensor1",
                                  "Sensor2",
                                  "Sensor3",
                                  "Sensor4"],
                          font=dfont)
gas_select.current(0)
var = tk.StringVar()
varr = var.set(gas_select.get())
label_temp = tk.Label(frame, textvariable=var, font=dfont, bg='white')
label_celsius = tk.Label(frame, textvariable=temp_c, font=dfont, bg='white')
label_unitc = tk.Label(frame, text="C", font=dfont, bg='white')
label_light = tk.Label(frame, text="Light:", font=dfont, bg='white')
label_lux = tk.Label(frame, textvariable=lux, font=dfont, bg='white')
label_unitlux = tk.Label(frame, text="lux", font=dfont, bg='white')
button_temp = tk.Button(frame,
                        text="Toggle Temperature",
                        font=dfont,
                        command=toggle_temp)
button_light = tk.Button(frame,
                         text="Toggle Light",
                         font=dfont,
                         command=toggle_light)
button_quit = tk.Button(frame,
                        text="Quit",
                        font=dfont,
                        command=root.destroy)
button_save = tk.Button(frame,
                        text="Save",
                        font=dfont,
                        command=dsave)
button_pause = tk.Button(frame,
                         text="Pause",
                         font=dfont,
                         command=dpause)
button_run = tk.Button(frame,
                       text="Run",
                       font=dfont,
                       command=run)

# Lay out widgets in a grid in the frame
canvas_plot.grid(row=0,
                 column=0,
                 rowspan=7,
                 columnspan=4,
                 sticky=tk.W + tk.E + tk.N + tk.S)

gas_select.grid(row=0, column=3, columnspan=1)
button_run.grid(row=0, column=4)
label_temp.grid(row=1, column=4, columnspan=2)
label_celsius.grid(row=2, column=4, sticky=tk.E)
label_unitc.grid(row=2, column=5, sticky=tk.W)
label_light.grid(row=3, column=4, columnspan=2)
label_lux.grid(row=4, column=4, sticky=tk.E)
label_unitlux.grid(row=4, column=5, sticky=tk.W)
button_temp.grid(row=6, column=0, columnspan=2)
button_light.grid(row=6, column=2, columnspan=2)
button_quit.grid(row=6, column=4, columnspan=2)
button_save.grid(row=7, column=0, columnspan=2)
button_pause.grid(row=7, column=2, columnspan=2)

# Add a standard 5 pixel padding to all widgets
for w in frame.winfo_children():
    w.grid(padx=5, pady=10)

# Make it so that the grid cells expand out to fill window
for i in range(0, 5):
    frame.rowconfigure(i, weight=1)
for i in range(0, 5):
    frame.columnconfigure(i, weight=1)

# Bind F11 to toggle fullscreen and ESC to end fullscreen
root.bind('<F11>', toggle_fullscreen)
root.bind('<Escape>', end_fullscreen)

# Have the resize() function be called every time the window is resized
root.bind('<Configure>', resize)

# Call empty _destroy function on exit to prevent segmentation fault
root.bind("<Destroy>", _destroy)

# Initialize our sensors


# Call animate() function periodically
fargs = (ax1, ax2, xs, temps, lights, temp_c, lux)
ani = animation.FuncAnimation(fig,
                              animate,
                              fargs=fargs,
                              interval=update_interval)

# Start in fullscreen mode and run
root.title("welcome to PID")
root.geometry('600x400')
# toggle_fullscreen()
root.mainloop()


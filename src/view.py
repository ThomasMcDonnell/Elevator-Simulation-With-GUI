import matplotlib

matplotlib.use("TkAgg")
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style

import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Progressbar
from tkinter import messagebox

from controller import Controller

import os

LARGE_FONT = "Verdana", 12
style.use("ggplot")

# graph
f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)


def animate(interval):
    db = open("db.txt", "r").read()
    db_arr = db.split('\n')
    x_arr = []
    y_arr = []
    for line in db_arr:
        if len(line) > 1:
            x, y = line.split(',')
            x_arr.append(int(x))
            y_arr.append(float(y))
    a.clear()
    a.plot(x_arr, y_arr)


class SimulationApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)  # call parent constructor
        tk.Tk.wm_title(self, "Elevator Simulation Application")
        self.geometry('2000x1000')
        # set primary frame
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # dict of all application frames
        self.frames = {}
        # frames
        for F in (StartPage, ElevatorSimulationPage, GraphPage):
            frame = F(parent=container, controller=self)
            # append to dict frames
            self.frames[F] = frame

            # set frame positions
            frame.grid(row=0, column=0, sticky="nsew")

        # show frames
        self.show_frame(StartPage)

    def show_frame(self, controller):
        """
        method to raise a frame
        :param controller:
        """
        frame = self.frames[controller]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # call parent constructor
        # set label for frame
        label = tk.Label(self, text=("""Elevator Simulation Apllication
        you use this application at your own risk. I can not promise 
        it wont break your computer nor do I bare any responsibility.
        Thank you and enjoy!"""), font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        # buttons
        button_one = ttk.Button(self, text="Agree",
                                command=lambda: controller.show_frame(ElevatorSimulationPage))
        button_two = ttk.Button(self, text="Disagree",
                                command=quit)
        button_one.pack()
        button_two.pack()


class ElevatorSimulationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # call parent constructor
        # simulation variables
        self.simulation_variables = dict(num_floors=10, num_elevators=1,
                                         seed=12345678, logic=0)
        self.input_text = ["Floors ....", "Elevators ....", "Seed value ...."]
        self.cont = Controller()
        # set label for frame
        label = tk.Label(self, text="Simulation Arguments", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        # buttons
        button_one = ttk.Button(self, text="Graphs",
                                command=lambda: controller.show_frame(GraphPage))

        button_one.pack()

        # inputs
        # floors
        self.num_floors_l = ttk.Label(self, text="""The number of floors you would like. 
        Defaults to 10 if none provided.""")
        self.num_floors_l.pack(pady=5, padx=5)
        self.num_floors = ttk.Entry(self)
        self.num_floors.insert(0, self.input_text[0])
        self.num_floors.bind('<Button-1>', lambda x: self.on_click("self.num_floors.delete(0, '')"))
        self.num_floors.pack(pady=5, padx=5)
        # elevators
        self.num_elevators_l = ttk.Label(self, text="""The number of elevators you would like. 
        Defaults to 1 if none provided.""")
        self.num_elevators_l.pack(pady=10, padx=10)
        self.num_elevators = ttk.Entry(self)
        self.num_elevators.insert(0, self.input_text[1])
        self.num_elevators.bind('<Button-1>', lambda x: self.on_click("self.num_elevators.delete(0, '')"))
        self.num_elevators.pack(pady=5, padx=5)
        # seed
        self.seed_l = ttk.Label(self, text="""The seed value you wish to run the simulation with. 
        Defaults to 1234567 if none provided.""")
        self.seed_l.pack(pady=10, padx=10)
        self.seed = ttk.Entry(self)
        self.seed.insert(0, self.input_text[2])
        self.seed.bind('<Button-1>', lambda x: self.on_click("self.seed.delete(0, '')"))
        self.seed.pack(pady=5, padx=5)
        # system logic
        self.varCk = False
        self.chk = ttk.Checkbutton(self, text="Enhanced Simulation", variable=self.varCk,
                                   command=lambda: self.on_tick())
        self.chk.pack(pady=5, padx=5)
        # submit form
        self.btn_submit = ttk.Button(self, text="submit",
                                     command=self.btn_on_submit)
        self.btn_submit.pack(pady=10, padx=10)

    def btn_on_submit(self):
        """
        This is a little lazy, but given that we are only dealing with integers I think any() is fine
        to determine string compares from list. Beats writing regx!

        set state after error checking and run simulation
        """
        val = self.num_floors.get()
        if not any(val in x for x in self.input_text):
            if ElevatorSimulationPage.check_input(val):
                self.simulation_variables['num_floors'] = val

        val = self.num_elevators.get()
        if not any(val in x for x in self.input_text):
            if ElevatorSimulationPage.check_input(val):
                self.simulation_variables['num_elevators'] = val

        val = self.seed.get()
        if not any(self.seed.get() in x for x in self.input_text):
            if ElevatorSimulationPage.check_input(val):
                self.simulation_variables['seed'] = val

        if self.varCk:
            self.simulation_variables['logic'] = 1

        self.run_simulation()

    def run_simulation(self):
        self.cont.run_simulation(num_floors=self.simulation_variables['num_floors'],
                                 num_elevators=self.simulation_variables['num_elevators'],
                                 seed=self.simulation_variables['seed'],
                                 logic=self.simulation_variables['logic'])
        self.reset_simulation_defaults()
        self.output()

    def output(self):
        with open("trace.txt", "r") as f_:
            output = ttk.Label(self, text=f_.read()).pack(side=tk.LEFT, pady=20, padx=20)
            return output

    @staticmethod
    def check_input(val):
        """
        Checks validity of inputs. Positive integer values return True, all else False with error message.
        :param val:
        :return: boolean
        """
        try:
            num = int(val)
            if num <= 0:
                messagebox.showerror("Non-Int+ Error", "Please enter a positive integer value.")
                return False
        except ValueError:
            messagebox.showerror("Non-Int Error", "Please enter an integer value.")
            return False
        else:
            return True

    def on_click(self, exc):
        """function that gets called whenever entry is clicked"""
        eval(exc)

    def on_tick(self):
        self.varCk = True

    def reset_simulation_defaults(self):
        """Reset the default values for the simulation"""
        self.simulation_variables.clear()
        self.simulation_variables['num_floors'] = 10
        self.simulation_variables['num_elevators'] = 1
        self.simulation_variables['seed'] = 12345678
        self.simulation_variables['logic'] = 0
        self.simulation_variables['is_default'] = True


class GraphPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # call parent constructor
        # set label for frame
        label = tk.Label(self, text="Graph Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        # buttons
        button_one = ttk.Button(self, text="Elevator Simulation",
                                command=lambda: controller.show_frame(ElevatorSimulationPage))
        button_one.pack()

        # embed graph in frame
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # set toolbar
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = SimulationApp()
    ani = animation.FuncAnimation(f, animate, interval=1000)
    app.mainloop()

import sys
import pyautogui
import collections
import tkinter as tk
from tkinter import ttk

COLOUR_PRIMARY = "#2e3f4f"
COLOUR_SECONDARY = "#293846"
COLOUR_LIGHT_BACKGROUND = "#fff"
COLOUR_LIGHT_TEXT = "#eee"
COLOUR_DARK_TEXT = "#8095a8"

def setDpiAwareness():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        print("error")

class Pomodoro(tk.Tk):
    def __init__(self):
        super().__init__()
        setDpiAwareness()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("timer.TFrame",
                        background=COLOUR_LIGHT_BACKGROUND)
        style.configure("background.TFrame", background=COLOUR_PRIMARY)
        style.configure("lightText.TLabel",
                        background=COLOUR_PRIMARY,
                        foreground=COLOUR_LIGHT_TEXT)
        style.configure("timerText.TLabel",
                        background=COLOUR_LIGHT_BACKGROUND,
                        foreground=COLOUR_DARK_TEXT,
                        font="Courier 38")
        style.configure("pomodoroButton.Tbutton",
                        background=COLOUR_SECONDARY,
                        foreground=COLOUR_LIGHT_TEXT)
        style.map("pomodoroButton.TButton",
                  background=[("active", COLOUR_PRIMARY), ("disabled", COLOUR_LIGHT_TEXT)])

        self["background"]=COLOUR_PRIMARY

        self.geometry("{}x{}".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        self.title("Pomodoro Timer")
        self.resizable(True, True)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.pomodoro = tk.StringVar(value="25:00")
        self.longBreak = tk.StringVar(value="10:00")
        self.shortBreak = tk.StringVar(value="05:00")
        self.states = ["Pomodoro", "Short Break", "Pomodoro", "Short Break", "Pomodoro", "Long Break"]
        self.statesQueue = collections.deque(self.states)
        self.frames = {}

        container = ttk.Frame(self)
        container.grid(padx=15, pady=5)

        self.timerFrame = Timer(container, self, lambda:self.showFrame(Settings))
        self.timerFrame.grid(column=0, row=0, padx=15, pady=5)
        settingsFrame = Settings(container, self, lambda:self.resetSettings(Timer))
        settingsFrame.grid(column=0, row=0, padx=15, pady=5)

        self.frames[Timer] = self.timerFrame
        self.frames[Settings] = settingsFrame

        self.showFrame(Timer)
        self.timerFrame.updateTimer()
        #settingsFrame.tkraise()

    def showFrame(self, key):
        frame = self.frames[key]
        frame.tkraise()

    def resetSettings(self, keyForFrame):
        self.showFrame(keyForFrame)
        self.timerFrame.resetTimer()

class Timer(ttk.Frame):
    def __init__(self, parent, root, showFrame):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self["style"]="background.TFrame"

        self.root = root
        self.timerValue = tk.StringVar()
        self.currentState = tk.StringVar()
        self.states = ["Pomodoro", "Short Break", "Pomodoro", "Short Break", "Pomodoro", "Long Break"]

        self.timerRunning = False
        self.jobStatus = None
        self.currentState.set(self.states[0])
        self.states = collections.deque(self.states)

        minutes = self.root.pomodoro.get()
        minutes = int(minutes.split(":")[0])
        #minutes = f"{minutes:02d}"
        self.timerValue.set(f"{minutes:02d}:00")

        stateLabel = ttk.Label(self,
                               textvariable=self.currentState,
                               style="lightText.TLabel")
        stateLabel.grid(column=0, row=0, sticky="EW", padx=(10,0), pady=(10,0))

        settingsButton = ttk.Button(self,
                                    text="Settings",
                                    command=showFrame,
                                    cursor="hand2",
                                    style="pomodoroButton.TButton")
        settingsButton.grid(column=1, row=0, padx=(10,0), pady=(10,0))

        timerFrame = ttk.Frame(self, height=100, style="timerFrame.TFrame")
        timerFrame.grid(column=0, row=1, sticky="NSEW", pady=(10,0), columnspan=3)

        timerLabel = ttk.Label(timerFrame,
                               textvariable=self.timerValue,
                               style="timerText.TLabel")
        timerLabel.place(relx=0.5, rely=0.5, anchor="center")

        buttonFrame = ttk.Frame(self, padding=10, style="background.TFrame")
        buttonFrame.grid(column=0, row=2, sticky="EW", columnspan=2)
        buttonFrame.columnconfigure((0,1,2), weight=1)

        self.playButton = ttk.Button(buttonFrame,
                                     text="Play",
                                     command=self.playTimer,
                                     state="normal",
                                     cursor="hand2",
                                     style = "pomodoroButton.TButton")

        self.playButton.grid(column=0, row=0, sticky="EW")

        self.pauseButton = ttk.Button(buttonFrame,
                                      text="Pause",
                                      command=self.pauseTimer,
                                      state="disabled",
                                      cursor="hand2",
                                      style = "pomodoroButton.TButton")

        self.pauseButton.grid(column=1, row=0, sticky="EW", padx=5)

        self.resetButton = ttk.Button(buttonFrame,
                                      text="Reset",
                                      command=self.resetTimer,
                                      state="normal",
                                      cursor="hand2",
                                      style = "pomodoroButton.TButton")

        self.resetButton.grid(column=2, row=0, sticky="EW")

    def resetTimer(self):
        self.pauseTimer()
        try:
            self.timerValue.set(f"{int(self.root.pomodoro.get()):02d}:00")
        except:
            self.timerValue.set(f"{self.root.pomodoro.get()}")
        self.states = ["Pomodoro", "Short Break", "Pomodoro", "Short Break", "Pomodoro", "Long Break"]
        self.states = collections.deque(self.states)
        self.currentState.set(self.states[0])

    def playTimer(self):
        self.timerRunning = True
        self.updateTimer()
        self.playButton["state"] = "disabled"
        self.pauseButton["state"] = "normal"

    def pauseTimer(self):
        self.timerRunning = False
        self.after_cancel(self.jobStatus)
        self.playButton["state"] = "normal"
        self.pauseButton["state"] = "disabled"

    def updateTimer(self):
        currentTime = self.root.pomodoro.get()

        if currentTime == "00:00":
            self.states.rotate(-1)
            self.currentState.set(self.states[0])
            if self.currentState.get() == "short break":
                self.timerValue.set(f"{self.root.shortBreak}:01")
                currentTime = self.timerValue.get()
            elif self.currentState.get() == "long break":
                self.timerValue.set(f"{self.root.longBreak}:01")
                currentTime = self.timerValue.get()
            elif self.currentState.get()== "pomodoro":
                self.timerValue.set(f"{self.root.pomodoro}:01")
                currentTime = self.timerValue.get()

        if self.timerRunning and currentTime !="00:00":
           minutes, seconds = self.timerValue.get().split(":")

           if int(seconds) > 0:
               seconds =int(seconds)-1
           else:
               seconds = 59
               minutes = int(minutes)-1
               minutes = f"{minutes:02d}"
           self.timerValue.set(f"{minutes}:{seconds:02d}")
           self.jobStatus = self.after(1000, self.updateTimer)

class Settings(ttk.Frame):
    def __init__(self, parent, root, showTimer):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self["style"] = "background.TFrame"

        mainFrame = ttk.Frame(self,
                              padding="30 15 30 15",
                              style="background.TFrame")
        mainFrame.grid(column=0, row=0, sticky="EW", padx=10, pady=10)
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.rowconfigure(1, weight=1)

        pomodoroLabel = ttk.Label(mainFrame,
                                  text="Pomodoro: ",
                                  style="lightText.TLabel")
        pomodoroLabel.grid(column=0, row=0, sticky="W", padx=5, pady=5)

        pomodoroSpinbox = ttk.Spinbox(mainFrame,
                                      from_=0,
                                      to=120,
                                      increment=1,
                                      textvariable=root.pomodoro,
                                      justify="center",
                                      width=10)
        pomodoroSpinbox.grid(column=1, row=0, sticky="EW", padx=5, pady=5)
        pomodoroSpinbox.focus()

        longBreakLabel = ttk.Label(mainFrame,
                                   text="Long Break time: ",
                                   style="lightText.TLabel")
        longBreakLabel.grid(column=0, row=1, sticky="W", padx=5, pady=5)

        longBreakSpinbox = ttk.Spinbox(mainFrame,
                                       from_=1,
                                       to=60,
                                       increment=1,
                                       textvariable=root.longBreak,
                                       justify="center",
                                       width=10)
        longBreakSpinbox.grid(column=1, row=1, padx=5, pady=5)

        shortBreakLabel = ttk.Label(mainFrame,
                                    text="Short Break time: ",
                                    style="lightText.TLabel")
        shortBreakLabel.grid(column=0, row=2, padx=5, pady=5)

        shortBreakSpinbox = ttk.Spinbox(mainFrame,
                                        from_=1,
                                        to=30,
                                        increment=1,
                                        textvariable=root.shortBreak,
                                        justify="center",
                                        width=10)
        shortBreakSpinbox.grid(column=1, row=2, padx=5, pady=5)

        buttonFrame = ttk.Frame(self, style="background.TFrame")
        buttonFrame.grid(sticky="EW", padx=10)
        buttonFrame.columnconfigure(0, weight=1)

        timerButton = ttk.Button(buttonFrame,
                                 text="Back",
                                 command=showTimer,
                                 cursor="hand2",
                                 style="pomodorButton.TButton")
        timerButton.grid(column=0, row=0, sticky="EW", padx=2, pady =15)


if __name__ == "__main__":
    root = Pomodoro()
    root.mainloop()
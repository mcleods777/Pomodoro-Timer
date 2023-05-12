import tkinter as tk
import tkinter.ttk as ttk
import winsound
import time
import csv
from datetime import datetime, timedelta
import os

class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        self.master.title('Pomodoro Timer')
        self.master.configure(bg='lightgray')

        self.state = False
        self.work_time = 25*60
        self.short_break = 5*60
        self.long_break = 15*60
        self.cycles = 4
        self.cycle_count = 0
        self.task_start_time = None

        self.title_label = tk.Label(master, text="Pomodoro Timer", font=("Helvetica", 24), bg='lightgray')
        self.title_label.pack(pady=10)

        self.current_time = tk.StringVar()
        self.timer_label = tk.Label(master, textvariable=self.current_time, font=("Helvetica", 48), bg='lightgray')
        self.timer_label.pack(pady=20)

        self.current_clock = tk.StringVar()
        self.clock_label = tk.Label(master, textvariable=self.current_clock, font=("Helvetica", 24), bg='lightgray')
        self.clock_label.pack(pady=10)

        self.tasks = self.load_tasks()
        self.task_var = tk.StringVar()
        self.task_dropdown = ttk.Combobox(master, textvariable=self.task_var, values=self.tasks)
        self.task_dropdown.pack()

        self.start_button = tk.Button(master, text='Start', command=self.start_timer, font=("Helvetica", 14), bg='lightgreen')
        self.start_button.pack(pady=10)

        self.reset_button = tk.Button(master, text='Reset', command=self.reset_timer, font=("Helvetica", 14), bg='lightblue')
        self.reset_button.pack()

        self.update_timer()
        self.update_clock()

        if not os.path.isfile('pomodoro_log.csv'):
            with open('pomodoro_log.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Task', 'Start Time', 'End Time', 'Status', 'Time Spent'])

    def load_tasks(self):
        if os.path.isfile('tasks.txt'):
            with open('tasks.txt', 'r') as file:
                tasks = file.read().splitlines()
            return tasks
        else:
            return []

    def save_task(self, task):
        with open('tasks.txt', 'a') as file:
            file.write(task + '\n')

    def update_timer(self):
        self.minutes, self.seconds = divmod(self.work_time, 60)
        self.current_time.set(f"{self.minutes:02d}:{self.seconds:02d}")
        if self.state:
            self.work_time -= 1
            if self.work_time < 0:
                winsound.Beep(440, 1000)  # Beep at 440 Hz for 1000 ms
                self.cycle_count += 1
                self.log_task('completed')
                if self.cycle_count == self.cycles:
                    self.work_time = self.long_break
                    self.cycle_count = 0
                else:
                    self.work_time = self.short_break
        self.master.after(1000, self.update_timer)

    def update_clock(self):
        current_time = time.strftime('%H:%M:%S')
        self.current_clock.set(current_time)
        self.master.after(1000, self.update_clock)

    def start_timer(self):
        if not self.task_start_time:
            self.task_start_time = datetime.now()
        self.state = not self.state
        if self.state:
            self.start_button.config(text='Pause', bg='lightsalmon')
            self.log_task('started')
        else:
            self.start_button.config(text='Resume', bg='lightgreen')
            self.log_task('paused')

    def reset_timer(self):
        self.work_time = 25*60
        self.cycle_count = 0
        self.start_button.config(text='Start', bg='lightgreen')
        self.log_task('reset')
        self.task_start_time = None

    def log_task(self, status):
        current_time = datetime.now()

        if self.task_start_time:
            # Start time is always the start of the 25-minute work period
            start_time = self.task_start_time
        else:
            start_time = current_time

        end_time = current_time  # Default end_time to current_time
    
        time_spent = end_time - start_time
        try:
            with open('pomodoro_log.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.task_var.get(), start_time, end_time, status, time_spent])
        except PermissionError:
            print("Unable to write to CSV file. Please make sure it is not open in another program.")
    
        if status == 'completed' or status == 'reset':
            self.task_start_time = None

root = tk.Tk()
my_timer = PomodoroTimer(root)
root.mainloop()

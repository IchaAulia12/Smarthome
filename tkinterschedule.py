import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import time

class LampSchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lamp Scheduler")
        self.geometry("400x400")
        
        # Lamp selection
        self.lamp_label = tk.Label(self, text="Select Lamp:")
        self.lamp_label.pack(pady=5)
        self.lamp_var = tk.StringVar()
        self.lamp_dropdown = ttk.Combobox(self, textvariable=self.lamp_var)
        self.lamp_dropdown['values'] = ["Lamp 1", "Lamp 2", "Lamp 3"]  # Example values
        self.lamp_dropdown.pack(pady=5)
        
        # Time pickers
        self.on_time_label = tk.Label(self, text="On Time:")
        self.on_time_label.pack(pady=5)
        self.on_time_var = tk.StringVar()
        self.on_time_entry = tk.Entry(self, textvariable=self.on_time_var)
        self.on_time_entry.pack(pady=5)

        self.off_time_label = tk.Label(self, text="Off Time:")
        self.off_time_label.pack(pady=5)
        self.off_time_var = tk.StringVar()
        self.off_time_entry = tk.Entry(self, textvariable=self.off_time_var)
        self.off_time_entry.pack(pady=5)
        
        # Schedule list
        self.schedule_list_label = tk.Label(self, text="Scheduled Times:")
        self.schedule_list_label.pack(pady=5)
        self.schedule_listbox = tk.Listbox(self)
        self.schedule_listbox.pack(pady=5)
        
        # Add/Remove buttons
        self.add_button = tk.Button(self, text="Add Schedule", command=self.add_schedule)
        self.add_button.pack(pady=5)
        self.remove_button = tk.Button(self, text="Remove Selected", command=self.remove_schedule)
        self.remove_button.pack(pady=5)
        
        # Save/Apply button
        self.save_button = tk.Button(self, text="Save and Apply", command=self.save_schedules)
        self.save_button.pack(pady=20)
        
        # Internal schedule storage
        self.schedules = []

    def add_schedule(self):
        lamp = self.lamp_var.get()
        on_time = self.on_time_var.get()
        off_time = self.off_time_var.get()
        if lamp and on_time and off_time:
            schedule = f"{lamp} | On: {on_time} | Off: {off_time}"
            self.schedule_listbox.insert(tk.END, schedule)
            self.schedules.append((lamp, on_time, off_time))
        else:
            messagebox.showwarning("Input Error", "Please select a lamp and set both on and off times.")

    def remove_schedule(self):
        selected_indices = self.schedule_listbox.curselection()
        for index in selected_indices[::-1]:
            self.schedule_listbox.delete(index)
            del self.schedules[index]

    def save_schedules(self):
        # Here you would implement saving schedules to a file or sending them to the backend
        # For this example, we just print the schedules
        for schedule in self.schedules:
            print(schedule)
        messagebox.showinfo("Schedules Saved", "Schedules have been saved and applied.")

if __name__ == "__main__":
    app = LampSchedulerApp()
    app.mainloop()

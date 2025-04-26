import tkinter as tk
import pandas as pd
from tkinter import ttk, messagebox

# Load the steam table CSV
df = pd.read_csv("SteamTable.csv")

# Create the main window
window = tk.Tk()
window.title("Steam Table Calculator")
window.geometry("450x450")
window.resizable(False, False)

# --- Menu Bar ---
menubar = tk.Menu(window)
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=lambda: show_about())
menubar.add_cascade(label="Help", menu=help_menu)
window.config(menu=menubar)

# --- Frames ---
main_frame = tk.Frame(window)
main_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

# --- Input Group ---
input_group = tk.LabelFrame(main_frame, text="Input")
input_group.pack(fill="x", pady=10)

tk.Label(input_group, text="Temperature (°C):").pack(anchor="w")
temp_entry = tk.Entry(input_group, width=20)
temp_entry.pack(anchor="w", pady=2)

tk.Label(input_group, text="Pressure (kPa):").pack(anchor="w")
pressure_entry = tk.Entry(input_group, width=20)
pressure_entry.pack(anchor="w", pady=2)

# --- Output Group ---
output_group = tk.LabelFrame(main_frame, text="Output (Steam Table Properties)")
output_group.pack(fill="x", pady=10)

output_entries = []
output_labels = ["vf (m³/kg)", "vg (m³/kg)", "hf (kJ/kg)", "hg (kJ/kg)"]

for label_text in output_labels:
    row = tk.Frame(output_group)
    row.pack(fill="x", pady=2)
    tk.Label(row, text=label_text, width=20, anchor="w").pack(side="left")
    entry = tk.Entry(row, width=20, state="readonly")
    entry.pack(side="left")
    output_entries.append(entry)

# --- Functions ---
def interpolate_value(x, x_col, y_col):
    lower = df[df[x_col] <= x].tail(1)
    upper = df[df[x_col] >= x].head(1)
    if lower.empty or upper.empty:
        return None
    x0, y0 = lower.iloc[0][x_col], lower.iloc[0][y_col]
    x1, y1 = upper.iloc[0][x_col], upper.iloc[0][y_col]
    if x1 == x0:
        return y0
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

def reset_fields():
    temp_entry.config(state="normal")
    pressure_entry.config(state="normal")
    temp_entry.delete(0, tk.END)
    pressure_entry.delete(0, tk.END)
    for entry in output_entries:
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.config(state="readonly")

def fill_from_temp(event=None):
    temp_val = temp_entry.get().strip()
    if not temp_val:
        return
    try:
        T = float(temp_val)
        if T > 100:
            messagebox.showerror("Error", "Temperature exceeds limit.\n(Only up to 100°C supported)\n\nNote: This is an early-stage version.")
            reset_fields()
            return

        P = interpolate_value(T, "Temp (°C)", "Pressure (kPa)")
        if P is not None:
            pressure_entry.config(state="normal")
            pressure_entry.delete(0, tk.END)
            pressure_entry.insert(0, f"{P:.3f}")
            pressure_entry.config(state="readonly")

            for entry, col in zip(output_entries, ["Specific Volume (m³/kg)", "Specific Volume (m³/kg)", "Specific Enthalpy (kJ/kg)", "Specific Enthalpy (kJ/kg)"]):
                value = interpolate_value(T, "Temp (°C)", col)
                if value is not None:
                    entry.config(state="normal")
                    entry.delete(0, tk.END)
                    entry.insert(0, f"{value:.4f}")
                    entry.config(state="readonly")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input.\n\nNote: This is an early-stage version.\n\nDetails: {str(e)}")

def fill_from_pressure(event=None):
    pressure_val = pressure_entry.get().strip()
    if not pressure_val:
        return
    try:
        P = float(pressure_val)
        if P > 101.42:
            messagebox.showerror("Error", "Pressure exceeds limit.\n(Only up to 101.42 kPa supported)\n\nNote: This is an early-stage version.")
            reset_fields()
            return

        T = interpolate_value(P, "Pressure (kPa)", "Temp (°C)")
        if T is not None:
            temp_entry.config(state="normal")
            temp_entry.delete(0, tk.END)
            temp_entry.insert(0, f"{T:.3f}")
            temp_entry.config(state="readonly")

            for entry, col in zip(output_entries, ["Specific Volume (m³/kg)", "Specific Volume (m³/kg)", "Specific Enthalpy (kJ/kg)", "Specific Enthalpy (kJ/kg)"]):
                value = interpolate_value(P, "Pressure (kPa)", col)
                if value is not None:
                    entry.config(state="normal")
                    entry.delete(0, tk.END)
                    entry.insert(0, f"{value:.4f}")
                    entry.config(state="readonly")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input.\n\nNote: This is an early-stage version.\n\nDetails: {str(e)}")

def toggle_table():
    if tree_frame.winfo_ismapped():
        tree_frame.pack_forget()
        toggle_btn.config(text="Show Table")
        window.geometry("450x450")
    else:
        tree_frame.pack(side="right", fill="both", expand=False, padx=5, pady=10)
        toggle_btn.config(text="Hide Table")
        window.geometry("950x450")

def show_about():
    about = tk.Toplevel(window)
    about.title("About Steam Table Calculator")
    about.geometry("400x250")
    about.resizable(False, False)
    text = tk.Text(about, wrap="word", font=("Arial", 10))
    text.pack(expand=True, fill="both", padx=10, pady=10)
    about_content = (
        "Steam Table Calculator\n\n"
        "This tool helps users find steam table properties\n"
        "(specific volume, enthalpy, etc.) based on\n"
        "input temperature or pressure.\n\n"
        "Note:\n- Early-stage version.\n- Valid up to 100°C and 101.42 kPa."
    )
    text.insert(tk.END, about_content)
    text.config(state="disabled")
    tk.Button(about, text="Close", command=about.destroy).pack(pady=5)

# --- Buttons ---
button_frame = tk.Frame(main_frame)
button_frame.pack(pady=10)

reset_btn = tk.Button(button_frame, text="Reset", width=15, command=reset_fields)
reset_btn.pack(side="left", padx=10)

toggle_btn = tk.Button(button_frame, text="Show Table", width=15, command=toggle_table)
toggle_btn.pack(side="left", padx=10)

# --- Treeview for Table ---
tree_frame = tk.Frame(window)
columns = list(df.columns)
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
for _, row in df.iterrows():
    tree.insert("", "end", values=list(row))
tree.pack(fill="both", expand=True)

# --- Bindings ---
temp_entry.bind("<KeyRelease>", fill_from_temp)
pressure_entry.bind("<KeyRelease>", fill_from_pressure)

# --- Start App ---
window.mainloop()

import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import os

LOOT_FILE = "loot_table.txt"

def update_counter(event=None):
    """Update the label showing how many lines are entered."""
    lines = loot_box.get("1.0", tk.END).strip().split("\n")
    count = len([l for l in lines if l.strip()])  # count non-empty lines
    counter_label.config(text=f"Loot Items: {count}/100")
    if count < 100:
        counter_label.config(fg="red")
    else:
        counter_label.config(fg="green")

def save_loot_table():
    """Save loot table to file automatically when closing."""
    data = loot_box.get("1.0", tk.END).strip()
    with open(LOOT_FILE, "w", encoding="utf-8") as f:
        f.write(data)

def load_loot_table():
    """Load loot table from file if it exists."""
    if os.path.exists(LOOT_FILE):
        with open(LOOT_FILE, "r", encoding="utf-8") as f:
            loot_box.insert(tk.END, f.read())
        update_counter()

def on_close():
    """Save before exit."""
    save_loot_table()
    root.destroy()

def generate_loot():
    """Generate loot using a 15-digit random number split into 2-digit pairs."""
    loot_lines = loot_box.get("1.0", tk.END).strip().split("\n")
    loot_lines = [line for line in loot_lines if line.strip()]  # remove blanks

    if len(loot_lines) < 100:
        messagebox.showerror("Error", f"Please enter at least 100 loot items. You currently have {len(loot_lines)}.")
        return

    rand_number = ''.join(str(random.randint(0, 9)) for _ in range(24))
    pairs = [rand_number[i:i+2] for i in range(0, len(rand_number), 2)]

    indices = []
    for pair in pairs:
        val = int(pair)
        if val == 0:
            val = 1
        elif val > 100:
            val = (val % 100) or 1
        indices.append(val)

    loot_results = [f"{i+1:02d}: {loot_lines[idx-1]}" for i, idx in enumerate(indices)]

    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, f"Random Number: {rand_number}\n\n")
    result_box.insert(tk.END, "\n".join(loot_results))

# --- GUI setup ---
root = tk.Tk()
root.title("Loot Drop Generator")
root.geometry("950x600")

# Left panel (loot list)
frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

header_frame = tk.Frame(frame_left)
header_frame.pack(fill=tk.X)

tk.Label(header_frame, text="Loot Table:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
counter_label = tk.Label(header_frame, text="Loot Items: 0/100", font=("Arial", 10))
counter_label.pack(side=tk.RIGHT)

loot_box = scrolledtext.ScrolledText(frame_left, width=40, height=30, wrap=tk.WORD)
loot_box.pack(fill=tk.BOTH, expand=True)
loot_box.bind("<KeyRelease>", update_counter)

# Right panel (results)
frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

tk.Label(frame_right, text="Generated Loot:", font=("Arial", 12, "bold")).pack(anchor="w")
result_box = scrolledtext.ScrolledText(frame_right, width=40, height=30, wrap=tk.WORD, bg="#f4f4f4")
result_box.pack(fill=tk.BOTH, expand=True)

# Button
generate_btn = tk.Button(root, text="🎲 Generate Loot", command=generate_loot,
                         font=("Arial", 14, "bold"), bg="#3c9", fg="white")
generate_btn.pack(side=tk.BOTTOM, pady=10)

# Load previous loot list (if any)
load_loot_table()

# Auto-save on close
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()

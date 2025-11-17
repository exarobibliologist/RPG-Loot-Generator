import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import os
import re

LOOT_FILE = "loot_table.txt"

def update_counter(event=None):
    """Update the label showing how many lines are entered."""
    lines = loot_box.get("1.0", tk.END).strip().split("\n")
    count = len([l for l in lines if l.strip()])  # count non-empty lines
    
    counter_label.config(text=f"Loot Items: {count}")
    
    # Set color based on whether there's enough input to generate (e.g., at least 1)
    if count == 0:
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

def roll_dynamic_quantity(loot_item):
    """
    Parses a loot item string for dynamic quantities like {XdY} or {Min-Max}
    and replaces them with the actual rolled result.
    """
    
    # 1. Handle Dice Roll Format: {XdY} or {X d Y}
    def dice_replacer(match):
        num_dice = int(match.group(1))
        die_sides = int(match.group(2))
        roll_result = sum(random.randint(1, die_sides) for _ in range(num_dice))
        return str(roll_result)

    # 2. Handle Range Format: {Min-Max}
    def range_replacer(match):
        min_val = int(match.group(1))
        max_val = int(match.group(2))
        if min_val > max_val:
            min_val, max_val = max_val, min_val 
        return str(random.randint(min_val, max_val))

    loot_item = re.sub(r'\{(\d+)\s*[dD]\s*(\d+)\}', dice_replacer, loot_item)
    loot_item = re.sub(r'\{(\d+)\s*-\s*(\d+)\}', range_replacer, loot_item)
    
    return loot_item

def parse_loot_weights(loot_lines):
    """
    Separates the loot lines into a list of items and a corresponding list of weights.
    Format: 'WEIGHT:ITEM' or just 'ITEM' (default weight is 1).
    """
    items = []
    weights = []
    weight_pattern = re.compile(r"^(\d+)\s*:\s*(.*)")
    
    for line in loot_lines:
        match = weight_pattern.match(line)
        if match:
            # Found a line with a weight (e.g., "100: Coins")
            weight = int(match.group(1))
            item = match.group(2).strip()
        else:
            # No weight specified (e.g., "Sword")
            weight = 1
            item = line.strip()
        
        if item: # Only add non-empty items
            items.append(item)
            weights.append(weight)
            
    return items, weights

def generate_loot():
    """Generate loot using weighted randomization and dynamic quantities."""
    
    try:
        num_results_str = count_entry.get().strip()
        if not num_results_str:
            NUM_RESULTS = 1
        else:
            NUM_RESULTS = int(num_results_str)
        if NUM_RESULTS <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid positive number for 'Loot Count'.")
        return

    raw_loot_lines = loot_box.get("1.0", tk.END).strip().split("\n")
    raw_loot_lines = [line for line in raw_loot_lines if line.strip()]  # remove blanks
    
    if not raw_loot_lines:
        messagebox.showerror("Error", "Please enter at least one loot item.")
        return

    # 1. Parse weights and items
    loot_items, loot_weights = parse_loot_weights(raw_loot_lines)
    
    if not loot_items:
         messagebox.showerror("Error", "No valid loot items found.")
         return

    # 2. Select the raw loot items using weights
    # k=NUM_RESULTS is the number of results to select.
    # weights=loot_weights assigns the probability for each item.
    selected_loot = random.choices(
        population=loot_items, 
        weights=loot_weights, 
        k=NUM_RESULTS
    )
    
    # 3. Process each selected item for dynamic quantities
    final_loot = [roll_dynamic_quantity(item) for item in selected_loot]

    loot_results = [f"{i+1:02d}: {item}" for i, item in enumerate(final_loot)]

    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, f"Random Seed: {random.randint(100000, 999999)}\n\n") 
    result_box.insert(tk.END, "\n".join(loot_results))

# --- GUI setup ---
root = tk.Tk()
root.title("Loot Drop Generator v2.1.1")
root.geometry("950x600")

# Left panel (loot list)
frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

header_frame = tk.Frame(frame_left)
header_frame.pack(fill=tk.X)

# Main title and instructions
title_frame = tk.Frame(header_frame)
title_frame.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(title_frame, text="Loot Table:", font=("Arial", 12, "bold")).pack(anchor="w")
# --- MODIFIED: Updated instruction text for weights ---
instruction_text = (
    "Prefix with **WEIGHT:ITEM** (e.g., 100: Coins) for weighting.\n"
    "Use {XdY} (dice) or {Min-Max} (range) for dynamic values."
)
tk.Label(title_frame, text=instruction_text, 
         font=("Arial", 9, "italic"), fg="gray40", justify=tk.LEFT).pack(anchor="w")
# ------------------------------------------------------------------------

counter_label = tk.Label(header_frame, text="Loot Items: 0", font=("Arial", 10))
counter_label.pack(side=tk.RIGHT)

loot_box = scrolledtext.ScrolledText(frame_left, width=40, height=30, wrap=tk.WORD)
loot_box.pack(fill=tk.BOTH, expand=True)
loot_box.bind("<KeyRelease>", update_counter)

# Right panel (results)
frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Loot Count Input Field
count_frame = tk.Frame(frame_right)
count_frame.pack(fill=tk.X, pady=(0, 5))

tk.Label(count_frame, text="Loot Count:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(0, 5))
count_entry = tk.Entry(count_frame, width=5)
count_entry.insert(0, "3") # Set a default value of 3
count_entry.pack(side=tk.LEFT)

tk.Label(frame_right, text="Generated Loot:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5, 0))

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
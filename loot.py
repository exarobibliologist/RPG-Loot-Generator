import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import os
import re

LOOT_FILE = "loot_table.txt"

def apply_striping():
    """Applies alternating background colors (zebra striping) to the loot_box."""
    
    # Define the colors
    COLOR_EVEN = "#FFFFFF" # White
    COLOR_ODD = "#BBBBBB"  # Light Gray
    
    # 1. Clear existing tags
    loot_box.tag_remove("color_even", "1.0", tk.END)
    loot_box.tag_remove("color_odd", "1.0", tk.END)
    
    # 2. Configure the tags
    loot_box.tag_configure("color_even", background=COLOR_EVEN)
    loot_box.tag_configure("color_odd", background=COLOR_ODD)

    # 3. Iterate through lines and apply tags
    line_count = int(loot_box.index('end-1c').split('.')[0])
    visible_line_counter = 0 
    
    for i in range(1, line_count + 1):
        line_start = f"{i}.0"
        # Ensure the tag extends past the line content to fill the background
        line_end = f"{i}.end" + " + 1c" 
        
        # Check if the line is not empty (important for accurate counting)
        line_content = loot_box.get(line_start, f"{i}.end").strip()
        
        if line_content:
            visible_line_counter += 1
            
            # Apply color based on parity of visible lines
            if visible_line_counter % 2 == 0:
                loot_box.tag_add("color_even", line_start, line_end)
            else:
                loot_box.tag_add("color_odd", line_start, line_end)

def apply_result_striping():
    """Applies alternating background colors to the generated results in result_box."""
    
    # Define the colors
    COLOR_EVEN = "#f4f4f4" # Default result background (matches frame bg)
    COLOR_ODD = "#E0E0E0"  # Slightly darker gray for contrast
    
    result_box.tag_remove("result_even", "1.0", tk.END)
    result_box.tag_remove("result_odd", "1.0", tk.END)
    
    # Configure the tags
    result_box.tag_configure("result_even", background=COLOR_EVEN)
    result_box.tag_configure("result_odd", background=COLOR_ODD)
    
    line_count = int(result_box.index('end-1c').split('.')[0])
    
    # Start loop from line 3 to skip the "Random Seed" and blank line
    for i in range(3, line_count + 1): 
        line_start = f"{i}.0"
        line_end = f"{i}.end" + " + 1c"
        
        # (i - 2) maps line 3 to the 1st result (odd count), line 4 to 2nd (even count), etc.
        if (i - 2) % 2 == 0:
            result_box.tag_add("result_even", line_start, line_end)
        else:
            result_box.tag_add("result_odd", line_start, line_end)


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
        
    # Call striping function every time the key is released
    apply_striping() 


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
    
    # 1. Handle Dice Roll Format: {XdY} or {X d Y} - ORIGINAL, RELIABLE REGEX
    def dice_replacer(match):
        num_dice = int(match.group(1))
        die_sides = int(match.group(2))
        roll_result = sum(random.randint(1, die_sides) for _ in range(num_dice))
        return str(roll_result)

    # 2. Handle Range Format: {Min-Max} - ORIGINAL, RELIABLE REGEX
    def range_replacer(match):
        min_val = int(match.group(1))
        max_val = int(match.group(2))
        if min_val > max_val:
            min_val, max_val = max_val, min_val  
        return str(random.randint(min_val, max_val))

    # Revert to the original, stricter regex patterns
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
            weight = int(match.group(1))
            item = match.group(2).strip()
        else:
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
    
    # 4. Apply striping to the results box
    apply_result_striping()

# --- GUI setup ---
root = tk.Tk()
root.title("Loot Drop Generator v2.1.5") 
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
instruction_text = (
    "Prefix with **WEIGHT:ITEM** (e.g., 100: Coins) for weighting.\n"
    "Use {XdY} (dice) or {Min-Max} (range) for dynamic values."
)
tk.Label(title_frame, text=instruction_text, 
          font=("Arial", 9, "italic"), fg="gray40", justify=tk.LEFT).pack(anchor="w")

counter_label = tk.Label(header_frame, text="Loot Items: 0", font=("Arial", 10))
counter_label.pack(side=tk.RIGHT)

loot_box = scrolledtext.ScrolledText(frame_left, width=40, height=30, wrap=tk.WORD)
loot_box.pack(fill=tk.BOTH, expand=True)

# Bind update_counter (which calls apply_striping)
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

# Apply striping immediately after loading the table
apply_striping() 

# Auto-save on close
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
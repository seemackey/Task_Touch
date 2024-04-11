# Touch task
# Chase Mackey 2023

from psychopy import visual, core, event, data, gui
import os
import json
import csv
import serial
port = serial.Serial("COM3",115200) # serial port and baud rate for dell xps laptop

# EXPERIMENT PARAMETERS ADJUST HERE, ADJ REW SIZE AROUND LINE 151
direction_change_interval = 5  # Change direction every 5 trials
required_touch_duration = 0.4  # seconds


# name of data folder
data_folder = "data"

# Create a dialog box to get the participant's name
dlg = gui.Dlg(title="Participant Information")
dlg.addField("Participant Name:")
dlg.show()
participant_name = dlg.data[0] # get the name we put in the GUI

# Create the data folder if it doesn't exist
data_folder_path = os.path.join(os.path.dirname(__file__), data_folder)
if not os.path.exists(data_folder_path):
    os.makedirs(data_folder_path)

# Generate the data file name based on the participant's name
data_file = f"{participant_name}.csv"
data_file_name = f"{participant_name}.csv"
data_file_path = os.path.join(data_folder_path, data_file_name)


if not dlg.OK:
    core.quit()

participant_name = dlg.data[0]

# Load monitor specifications from JSON file
with open("monitor_specifications.json", "r") as json_file:
    monitor_specs = json.load(json_file)

# Extract monitor parameters and MOVEMENT
screen_resolution = monitor_specs["screen_resolution"]
monitor_width = monitor_specs["monitor_width"]
full_screen = monitor_specs["full_screen"]
# Define the box size and movement amount based on monitor width
box_size = monitor_width * 0.4  # % of monitor width
movement_amount = box_size * 0.05  # 5% movement


# Create a PsychoPy window
win = visual.Window(
    size=screen_resolution,
    units="pix",
    fullscr=full_screen,
    monitor="debugging_monitor",
    screen=1,
    waitBlanking=True
)



# Create the green and red squares
greenBox = visual.Rect(
    win=win,
    width=box_size,
    height=box_size,
    pos=(0, 0),
    fillColor='green'
)

redBox = visual.Rect(
    win=win,
    width=box_size,
    height=box_size,
    pos=(0, 0),
    fillColor='red'
)

# Create a list of colors and the number of repetitions for each color
colors_with_reps = [("green", 1000), ("red", 1000)]

# Create a list of trials for each color based on repetitions
color_trials = []
for color, reps in colors_with_reps:
    color_trials.extend([{"color": color}] * reps)

# Create a TrialHandler using the color trials
trials = data.TrialHandler(
    trialList=color_trials,
    nReps=1,  # Since repetitions are already handled in the trial list
    method='sequential'
)

current_box = greenBox  # Start with the green box
correct_touch_count = 0
trial_count = 0

# Create a mouse object
mouse = event.Mouse(win=win)

# function that saves data
def save_data(trial_data_list, data_file_path):
    """Save the trial data to a CSV file."""
    with open(data_file_path, "w", newline='') as f:
        fieldnames = trial_data_list[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(trial_data_list)

# Main experiment loop
# Assuming the setup and initial parts of your script remain unchanged

# Main experiment loop adaptation for hover detection
# Assuming the setup and initial parts of your script remain unchanged

# Main experiment loop
trial_data_list = []  # List to store trial data dictionaries
change_direction_counter = 0

for trial in trials:
    trial_count += 1

    if change_direction_counter >= direction_change_interval:
        movement_amount *= -1  # Change direction
        change_direction_counter = 0  # Reset the counter

    change_direction_counter += 1

    # Calculate off-screen position
    # For simplicity, using a position to the right and above the screen based on the screen resolution
    off_screen_pos = (screen_resolution[0] * 1.5, screen_resolution[1] * 1.5)
    
    # Move the mouse cursor off-screen
    mouse.setPos(newPos=off_screen_pos)

    # Move the box slightly on each trial
    current_box.pos -= (movement_amount, movement_amount)
    
    # Draw the current box on the screen
    current_box.draw()
    win.flip()
    StimTime = core.getTime()

    correct_touch = 0  # Assume touch is incorrect until proven otherwise

    # Wait for a hover to detect touch
    touch_detected = False
    while not touch_detected:
        # Implement your hover detection or touch detection logic here
        # Note: With the mouse moved off-screen, you need to wait for the participant to move it back
        if current_box.contains(mouse.getPos()):
            correct_touch = 1  # Hover detected within the correct box
            touch_detected = True
            responseTime = core.getTime()
            # Optionally, send signal to reward system
            port.write(str.encode('r4'))  # Adjust command as needed
        elif 'escape' in event.getKeys():
            save_data(trial_data_list, data_file_path)  # Save data before exiting
            win.close()
            core.quit()

        core.wait(0.01)  # Small delay to prevent the loop from running too fast

    # Record the touch as correct or incorrect
    correct_touch_count += correct_touch  # Increment only if correct

    # Construct trial data dictionary
    trial_data = {
        "participant": participant_name,
        "color": "green" if current_box == greenBox else "red",
        "correct_touch": correct_touch,
        "correct_touch_count": correct_touch_count,
        "StimTime": StimTime,
        "RT": responseTime - StimTime
    }

    trial_data_list.append(trial_data)  # Append trial data to the list

    # Provide feedback
    feedback_text = visual.TextStim(win, text=f"Correct touches: {correct_touch_count}", pos=(0, -300))
    feedback_text.draw()
    win.flip()
    core.wait(1.5)  # Display feedback for 1.5 seconds

    # Clear the screen for the next trial
    win.flip()

    # If 7 or more correct touches, switch to the other box
    if correct_touch_count >= 7:
        current_box = redBox if current_box == greenBox else greenBox
        correct_touch_count = 0
        trial_count = 0

# At the end of all trials
save_data(trial_data_list, data_file_path)

# Cleanup
win.close()
core.quit()


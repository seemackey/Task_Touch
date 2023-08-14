# Touch task
# Chase Mackey 2023

from psychopy import visual, core, event, data, gui
import json

# Create a dialog box to get the participant's name
dlg = gui.Dlg(title="Participant Information")
dlg.addField("Participant Name:")
dlg.show()

if not dlg.OK:
    core.quit()

participant_name = dlg.data[0]

# Load monitor specifications from JSON file
with open("monitor_specifications.json", "r") as json_file:
    monitor_specs = json.load(json_file)

# Extract monitor parameters
screen_resolution = monitor_specs["screen_resolution"]
monitor_width = monitor_specs["monitor_width"]
full_screen = monitor_specs["full_screen"]
print(monitor_width)
print(screen_resolution)

# Create a PsychoPy window
win = visual.Window(
    size=screen_resolution,
    units="pix",
    fullscr=full_screen,
    monitor="debugging_monitor",  # Replace with your monitor calibration name
    waitBlanking=True
)

# Define the box size and movement amount based on monitor width
box_size = monitor_width * 0.1  # 10% of monitor width
movement_amount = box_size * 0.1  # 10% movement

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

# Create a list of trials for each box
green_trials = data.TrialHandler(
    trialList=[{}],
    nReps=10,  # Number of repetitions for each color
    method='sequential'
)

current_box = greenBox  # Start with the green box
correct_touch_count = 0
trial_count = 0
performance_data = []

# Create a PsychoPy data file
exp_data = data.ExperimentHandler(
    name=f"animal_training_{participant_name}",
    version="1.0",
    extraInfo={"participant": participant_name}
)

# Main experiment loop
for trial in green_trials:
    trial_count += 1

    # Move the box slightly on each trial
    current_box.pos += (movement_amount, movement_amount)

    # Draw the current box on the screen
    current_box.draw()
    win.flip()

    # Wait for a mouse click
    while not any(event.waitKeys(keyList=["mouse"])):
        pass

    # Get mouse position
    mouseX, mouseY = event.mouse.getPos()

    # Check if mouse click was within the box
    if current_box.contains(mouseX, mouseY):
        correct_touch = 1
        correct_touch_count += 1
    else:
        correct_touch = 0
    
    # Save trial data
    trial_data = {
        "box_color": "green",
        "correct_touch": correct_touch,
        "correct_touch_count": correct_touch_count
    }
    exp_data.addData(trial_data)

    # Append performance data
    performance_data.append(correct_touch_count / trial_count)

    # Provide feedback
    feedback_text = visual.TextStim(win, text=f"Correct touches: {correct_touch_count}/10", pos=(0, -300))
    feedback_text.draw()
    win.flip()
    core.wait(1.5)  # Display feedback for 1.5 seconds

    # Clear the screen
    win.flip()

    # If 7 or more correct touches, switch to the other box
    if correct_touch_count >= 7:
        if current_box == greenBox:
            current_box = redBox
        correct_touch_count = 0
        trial_count = 0

    # Check for escape key press to exit the experiment
    if 'escape' in event.getKeys():
        break

# Save data to files
exp_data.saveAsWideText(f"experiment_data_{participant_name}.csv")
exp_data.save()

# Clean up
win.close()
core.quit()


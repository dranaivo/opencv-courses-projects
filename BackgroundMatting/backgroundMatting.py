'''
Instructions:

1 - Select the input_video and define the output_video [in __main__]
2 - Select the background [in __main__]
3 - Execute this script
4 - Select a square patch (click and maintain, draw rectangle, then release)
5 - Adjust the slider for the tolerance.
6 - Press y to launch.

'''

import cv2
import numpy as np

### Helpers
def mean_hue(image):
    return int(np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:, :, 0]))

def transform(image, mean_color, tolerance_threshold):
    pass

### Callback functions
def color_patch_selector(action, x, y, flags, userdata):
    
    # Referencing global variables
    global mean_color, dummy, topleft, bottomright

    # Action to be taken when left mouse button is pressed
    if action==cv2.EVENT_LBUTTONDOWN:
        topleft = (x,y)
        # Mark the vertex
        cv2.circle(source, topleft, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow("Patch selection", source)

    # Action to be taken when left mouse button is released
    elif action==cv2.EVENT_LBUTTONUP:
        bottomright = (x,y)
        # Mark the vertex
        cv2.circle(source, bottomright, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # Draw selected patch
        cv2.rectangle(source, topleft, bottomright, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow("Patch selection", source)

        # Get the mean hue value of the selected patch
        patch = dummy[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]
        mean_color = mean_hue(patch)

def hue_tolerance(*args):
    global tolerance
    tolerance = args[0]
 
if __name__ == "__main__":
    # I/O
    input_video = "greenscreen-asteroid.mp4"
    output_video = "background-asteroid.mp4"

    # Video Init
    cap = cv2.VideoCapture(input_video)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video,cv2.VideoWriter_fourcc('M','J','P','G'), 20, (w, h)) 

    # Background
    background = cv2.imread("background.jpeg")
    background = cv2.resize(background, dsize=(w, h), interpolation=cv2.INTER_AREA)

    cv2.namedWindow("Patch selection", flags=cv2.WINDOW_NORMAL)
    instructions = "Select a square, adjust the tolerance then press y to confirm."

    # Callback parameters
    mean_color = 90 # middle of green hue value, initalization
    trackbar_name = "Tolerance value."
    tolerance = 1 
    scale = 30

    # Frame from which to select the background
    _, source = cap.read()
    dummy = source.copy()
    
    # Setting callbacks
    cv2.setMouseCallback("Patch selection", color_patch_selector)
    cv2.createTrackbar(trackbar_name, "Patch selection", tolerance, scale, hue_tolerance)

    k = 0
    cv2.putText(source, instructions, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
        (0, 0, 255), 2)
    cv2.imshow("Patch selection", source)
    while k != ord("y") :
        # Here to exit
        k = cv2.waitKey(20) & 0xFF

    cv2.destroyWindow("Patch selection")

    cv2.namedWindow("Display", flags=cv2.WINDOW_NORMAL)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Upper-bound and lower bound for hue value
        lower_bound = (mean_color - tolerance, 120, 70)
        upper_bound = (mean_color + tolerance, 255, 255)

        # Replacing the background
        mask = cv2.inRange(hsv, lower_bound, upper_bound) # add morph. closing
        not_mask = cv2.bitwise_not(mask)
        mask = cv2.merge((mask, mask, mask))
        not_mask = cv2.merge((not_mask, not_mask, not_mask))

        fore = cv2.bitwise_and(frame, not_mask)
        back = cv2.bitwise_and(background, mask)
        result = cv2.add(fore, back)

        # Show
        cv2.imshow("Display", result)
        cv2.waitKey(10)

        # Writing video
        out.write(result)

    # Clean-up
    cv2.destroyWindow("Display")
    cap.release()
    out.release()


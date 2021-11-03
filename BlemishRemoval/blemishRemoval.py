import cv2
import operator
import numpy as np

### Helpers
def crop_image(image, c_x, c_y, radius=30):
    top_x, bottom_x = (c_x - radius), (c_x + radius)
    top_y, bottom_y = (c_y - radius), (c_y + radius)
    tmp = image.copy()
    
    return tmp[top_y:bottom_y, top_x:bottom_x]

def smoothness_index(img):
    # Converting image to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply sobel filter along x and y direction 
    sobelx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    sobely = cv2.Sobel(img, cv2.CV_32F, 0, 1)

    # Take the abs value and apply mean
    sobelx = np.mean(np.abs(sobelx)).astype("int")
    sobely = np.mean(np.abs(sobely)).astype("int")

    return max(sobelx, sobely)

def seamless_clone(src, dst, c_x, c_y):
    mask = 255 * np.ones(src.shape, src.dtype)
    return cv2.seamlessClone(src, dst, mask, (c_x, c_y), cv2.NORMAL_CLONE)

def search_grid(image, center_x, center_y, radius):
    # This function will search around the neighborhood and return the center
    # of the patch with which to replace the current patch
    selection_x, selection_y = center_x, center_y
    min_smoothness = 100 # I assume that this a maximum value for initialization
    for j in range(-1, 2):
        for i in range(-1, 2):
            s_x = center_x + i*radius
            s_y = center_y + j*radius
            smoothness = smoothness_index(crop_image(image, s_x, s_y, radius))
            if smoothness < min_smoothness:
                # The selected center is updated
                min_smoothness = smoothness
                selection_x = s_x
                selection_y = s_y

    return selection_x, selection_y

def smoothing_callback(action, x, y, flags, userdata):
    global radius, image

    if action==cv2.EVENT_LBUTTONUP:
        h, w = image.shape[:2]
        # Condition of having a valid x and y
        assert not (x < 2*radius or y < 2*radius or x > w - 2*radius or y > h - 2*radius), \
            "Keep away from the border! Select a more inner region!"

        # Searching in grid
        c_x, c_y = search_grid(image, x, y, radius)
        image = seamless_clone(crop_image(image, c_x, c_y, radius), image, x, y)

        # Show
        cv2.imshow("Window", image)

if __name__ == "__main__":
    image = cv2.imread("blemish.png", cv2.IMREAD_COLOR)
    dummy = image.copy()

    # radius to consider
    radius = 15

    # highgui function called when mouse events occur
    cv2.namedWindow("Window")
    cv2.setMouseCallback("Window", smoothing_callback)

    k = 0
    # loop unitl "q" is pressed
    while k != ord("q"):
        cv2.imshow("Window", image)
        cv2.putText(image,'''Press i to initialize, q to quit.''' , (5,15), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255, 0, 0), 2 )
        
        k = cv2.waitKey(20) & 0xFF
        # Initialize
        if k == ord("i"):
            image = dummy.copy()

    cv2.destroyAllWindows()

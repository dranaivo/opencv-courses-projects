import cv2
import numpy as np

### Face detection function 
def detectFaceOpenCVDnn(net, frame):
    frameOpencvDnn = frame.copy()
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], False, False)

    net.setInput(blob)
    detections = net.forward()
    
    x1 = int(detections[0, 0, 0, 3] * frameWidth)
    y1 = int(detections[0, 0, 0, 4] * frameHeight)
    x2 = int(detections[0, 0, 0, 5] * frameWidth)
    y2 = int(detections[0, 0, 0, 6] * frameHeight)
    bbox = [x1, y1, x2, y2]
    cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
    
    return frameOpencvDnn, bbox

if __name__ == "__main__":
    ### Loading images
    img = cv2.imread("musk.jpg")
    sunglasses = cv2.imread("sunglass.png", cv2.IMREAD_UNCHANGED)
    sunglasses, alpha = sunglasses[:, :, :3], sunglasses[:, :, 3]
    landscape = cv2.imread("background.jpeg", cv2.IMREAD_COLOR)

    ### Load the model
    modelFile = "opencv_face_detector_uint8.pb"
    configFile = "opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)

    ### Detection
    outOpencvDnn, bbox = detectFaceOpenCVDnn(net, img)

    ### Face region
    imgCopy = img.copy()
    face_region = imgCopy[bbox[1]:bbox[3], bbox[0]:bbox[2]]

    # Apply a heuristic formula for getting the eye region from face
    face_height, face_width = face_region.shape[:2]
    eyeTop = int(1/6.0*face_height)
    eyeBottom = int(3/6.0*face_height)
    eye_region = face_region[eyeTop:eyeBottom, :, :]

    # A cascade classifier for detecting eyes
    eye_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")

    # Display
    gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
    eyes = eye_cascade.detectMultiScale(gray)
    for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(eye_region, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)
        
    # Eye resizing: heihgt = eye_height + 0.1*eight_heigt, width = face_width 
    resize_width = int(bbox[2] - bbox[0])
    resize_height = int(1.25 * eh)
    sunglasses, alpha = list(map(lambda img:cv2.resize(img, (resize_width, resize_height)), [sunglasses, alpha]))

    # the center of this sunglass image should be at the center precised below:
    center_y = int(bbox[1] + 1/6 * face_height + ey + eh / 2)
    center_x = int(bbox[0] + (bbox[2] - bbox[0])/2)

    center_y_sunglasses = int(sunglasses.shape[0] / 2)
    center_x_sunglasses = int(sunglasses.shape[1] / 2)

    ### SUNGLASS FILTER
    # Create tmp copy of the entire image
    tmp = img.copy()

    # Get the eye and background region from the face image
    eye_roi = [
        int(center_x - sunglasses.shape[1] / 2),
        int(center_y - sunglasses.shape[0] / 2),
        int(center_x + sunglasses.shape[1] / 2),
        int(center_y + sunglasses.shape[0] / 2),
    ]
    eyeROI= tmp[eye_roi[1]:eye_roi[3], eye_roi[0]:eye_roi[2]]

    # hardcoded
    background_roi = [
        955,
        249,
        955 + sunglasses.shape[1],
        249 + sunglasses.shape[0],
    ]
    backgroundROI= landscape[background_roi[1]:background_roi[3], background_roi[0]:background_roi[2]]

    # Use the mask to create the masked eye region
    glassMask = cv2.merge([alpha, alpha, alpha])
    maskedEye = cv2.bitwise_and(eyeROI, cv2.bitwise_not(glassMask))

    # Use the mask to create the weighted masked sunglass region
    a1 = 0.75 # glass alpha 
    a2 = 0.8 # landscape alpha
    eyeGlass = cv2.bitwise_and(eyeROI, glassMask)
    backgroundGlass = cv2.bitwise_and(backgroundROI, glassMask)

    maskedGlass = cv2.bitwise_and(sunglasses, glassMask)
    maskedGlass = cv2.addWeighted(maskedGlass, a1, eyeGlass, 1-a1, 0)
    maskedGlass = cv2.addWeighted(maskedGlass, a2, backgroundGlass, 1-a2, 0)

    # Combine the Sunglass in the Eye Region to get the augmented image
    eyeRoiFinal = cv2.bitwise_or(maskedEye, maskedGlass)

    # Replace the eye ROI with the output from the previous section
    tmp[eye_roi[1]:eye_roi[3], eye_roi[0]:eye_roi[2]] = eyeRoiFinal

    ### Display and saving
    cv2.imshow("Sunglass Filter", tmp)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite("output.jpg", tmp)

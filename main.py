import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import utils
import cv2
import numpy as np

manualCheck = False

# Step 1: Calibrate camera
fpath = '.\camera_cal\calibration1.jpg'
mtx, dist = utils.calibrateCamera(fpath, 9, 5, manualCheck = manualCheck)

# Step 2: Calculate perspective matrix M.
# Apply a distortion correction to raw images.
straight_line_image = mpimg.imread('test_images/straight_lines1.jpg')
# straight_line_image = mpimg.imread('test_images/challenge01.jpg')
undistorted = cv2.undistort(straight_line_image, mtx, dist)

### Manually measured 4 points (255, 683), (1052, 683), (594, 448), (684, 448)
selected_points = np.float32([[260.041, 681.833],[1044.35, 681.833], [685.594, 450.61],[593.598, 450.61]])
# Desired 4 points, make sure the center is 640
points = np.float32([[390, 700],[890, 700],[890, 0], [390, 0]])

img_shape = (straight_line_image.shape[1], straight_line_image.shape[0])
M = cv2.getPerspectiveTransform(selected_points, points)
inverseM = cv2.getPerspectiveTransform(points, selected_points)
warpped = cv2.warpPerspective(undistorted, M, img_shape, flags=cv2.INTER_LINEAR)
if manualCheck:
    plt.imshow(warpped)
    plt.show()

# Use color transforms, gradients, etc., to create a thresholded binary image.
# combined_binary, color_binary = utils.createThresholdBinary(undistorted, manualCheck = manualCheck)
combined_binary, color_binary = utils.createThresholdBinary(warpped, manualCheck = manualCheck)


# [important] define process image
### Need parameters mtx, dist, M
def process_image(img):
    global left_fit
    global right_fit

    undistorted = cv2.undistort(img, mtx, dist)
    warpped = utils.getPerspectiveBinary(undistorted, M)
    margin = 50
    if left_fit != None and right_fit != None:
        left_fit, right_fit = utils.detectLanesWithPreFram(warpped, 25, left_fit, right_fit)
    else:
        print("detectLanesWithoutPreFrame is executed")
        left_fit, right_fit = utils.detectLanesWithoutPreFrame(warpped, margin, 7, visualization = manualCheck)

    # Warp the detected lane boundaries and draw back onto the original image.
    return utils.drawDetectedBoundary(undistorted, inverseM, left_fit, right_fit)
    
    
    
# Step 3: Apply preprocess in a test image
# Apply a perspective transform to undistorted binary image ("birds-eye view").
test_image = mpimg.imread('test_images/straight_lines1.jpg')
# test_image = mpimg.imread('test_images/challenge01.jpg')
warpped = utils.getUndistortedPerspectiveBinary(test_image, mtx, dist, M, manualCheck=manualCheck)

# Step 4: Detect lane pixels and fit to find the lane boundary
margin = 50 # How much to slide left and right for searching
#window_centroids = utils.find_window_centroids(warpped, window_width, window_height, margin)
#utils.display_window(window_centroids, warpped, window_width, window_height, margin)
left_fit, right_fit = utils.detectLanesWithoutPreFrame(warpped, margin, 7, visualization = manualCheck)

# Step 5: Find curvature in next frame
test_image = mpimg.imread('test_images/straight_lines2.jpg')
warpped = utils.getUndistortedPerspectiveBinary(test_image, mtx, dist, M, manualCheck=manualCheck)
utils.detectLanesWithPreFram(warpped, margin, left_fit, right_fit, visualization = manualCheck)

# Step 6: Warp the detected lane boundaries back onto the original image.
utils.drawDetectedBoundary(test_image, inverseM, left_fit, right_fit)


# # Step 7: Generate video
from moviepy.editor import VideoFileClip

left_fit = None
right_fit = None
# white_output = 'harder_challenge_video_output.mp4'
white_output = 'project_video_output.mp4'
# To speed up the testing process you may want to try your pipeline on a shorter subclip of the video
#clip1 = VideoFileClip("test_videos/solidWhiteRight.mp4").subclip(0,2)
# clip1 = VideoFileClip("harder_challenge_video.mp4")
clip1 = VideoFileClip("project_video.mp4")
white_clip = clip1.fl_image(process_image) #NOTE: this function expects color images!!
# %time white_clip.write_videofile(white_output, audio=False)
white_clip.write_videofile(white_output, audio=False)

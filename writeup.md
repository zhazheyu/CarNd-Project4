## Writeup Template

### You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---

**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./examples/undistort_output.png "Undistorted"
[image2]: ./examples/undistorted_image.png "Undistorted example"
[image3]: ./examples/color_map.png "Colormap"
[image4]: ./examples/warped_image.png "Warp Example"
[image5]: ./examples/Image_process.png "Image process"
[image6]: ./examples/fit_straight_line.png "Fit without previous image"
[image7]: ./examples/drawbackresult.png "draw back image"
[image8]: ./examples/pre_process.png "Preprocess"

[video1]: ./project_video_output.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!

### Camera Calibration

#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The code for this step is contained in the ”Section 1: Calibrate camera“ of the IPython notebook located in "./example.ipynb" .  

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![alt text][image1]

### Pipeline (single images)

#### 1. Provide an example of a distortion-corrected image.

To demonstrate this step, I will describe how I apply the distortion correction to one of the test images like this one:
![alt text][image2]

#### 2. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

The code for my perspective transform is located in "Section 3: Calculate perspective matrix M." of the IPython notebook.  It takes as inputs an image (`img`) and used hardcode  the source and destination points in the following manner. The src code is chosen by manually measure straight line image:

```python
selected_points = np.float32([[260.041, 681.833],[1044.35, 681.833], [685.594, 450.61],[593.598, 450.61]])
# Desired 4 points, make sure the center is 640
points = np.float32([[390, 700],[890, 700],[890, 0], [390, 0]])
```

This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 260.041, 681.833    | 390, 700    | 
| 1044.35, 681.833    | 890, 700    |
| 685.594, 450.61     | 890, 0      |
| 593.598, 450.61     | 390, 0      |

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

![alt text][image4]

#### 2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

First, in order to reduce the cause of lightness effect, CLAHE method is used to enhance contrast on different lightness image. 
https://stackoverflow.com/questions/24341114/simple-illumination-correction-in-images-opencv-c/24341809#24341809
Then, a combination of color and gradient thresholds to generate a binary image (thresholding steps Section 4: Use color transforms, gradients, etc., to create a thresholded binary image in IPython notebook).  Here's an example image on different color map channel

![alt text][image3]

Based on the above image, the following channel are selected: l-channel, and b-channel and x-derivative s-channel.  The the image will be converted as binary as following:

![alt text][image5]

![alt text][image8]

#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

Then I did some other stuff and fit my lane lines with a 2nd order polynomial kinda like this:
After getting binary image, it starts the followings to get lane lines:
1. Get histogram of bottom 1/4 binary image.
2. Take maximum of histogram on left side image as start point of left lane, similiar for right lane.
3. Based on the center of lane line, draw rectangle window (with center window height) of interest area to get points.
4. From the points extracted from step 3, re-calculate the center point, then draw another window to repeat step 3, until it reach the top of image.
5. Then take all the points in these windows, to fit 2nd order polynomial line.  Left and right lines are separate.

![alt text][image6]

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

I did this in function detectLanesWithPreFram and detectLanesWithoutPreFrame in `utils.py`
For detectLanesWithoutPreFrame function:
1. It will follow the instruction on Section 4, to get 2nd order polynomial left and right lanes.

For detectLanesWithPreFram:
For detectLanesWithPreFram function: 
1. it will take the polyfit in last image as reference.  Based on the assumption that the two continuous images in video have very similar lane curvatures.  Thus, it will use the polyfit as baseline to extract interest points.  Then, calculate curvature.

With 2nd polynomial fit, then it can covert polynomial coefficients from pixels to meters here:

    left_fit_cr = np.polyfit(ploty*ym_per_pix, left_fitx*xm_per_pix, 2)
    
    right_fit_cr = np.polyfit(ploty*ym_per_pix, right_fitx*xm_per_pix, 2)
    
Then calculate the curvature on the position of vehicle, y-corrodinate 700 is take here, since it is zero-based in "birds-eye" image.
 left_curv = ((1 + (2*left_fit_cr[0]*y_eval*ym_per_pix + left_fit_cr[1])**2)**1.5) / np.absolute(2*left_fit_cr[0])
 right_curv = ((1 + (2*right_fit_cr[0]*y_eval*ym_per_pix + right_fit_cr[1])**2)**1.5) / np.absolute(2*right_fit_cr[0])

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

I implemented this step in lines # through # in my code in `yet_another_file.py` in the function `map_lane()`.  Here is an example of my result on a test image:

![alt text][image7]

---

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./project_video_output.mp4)


#### 2. Provide a link to chanllenge video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./challenge_video_output.mp4)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.

The treshold on combination of colomap image, need to fine-tuning based on different images.  For example, for project_video, it has better environment -- relatively unique environment, no shadow, and discruptive road surface.  So it has more tolorence about these parameters selection.  Through this project, it is found that different threshold parameters fits for different environments. 

Back to chanllenge_video, it can be found that there is a couple of seconds that fit line does not fit totally at far end of road.  It is caused that binary image generation also consider the left side corner line.  Thus we may need to improve the image precess method to avoid this line.

The implementation here also based on assumption that there is no line between left/right lane, for example, for left-turn/straight lane, it may have two left/right lanes.  Then the implementation will fail.
Moreover, like in challenge_video, if discruptive line on road surface has similar color, then the implementation will also fail.  
Since the distance b/w left and right line is fixed, we can use it to select interest windows. For example, if we found that there is one peak in right side of binary image, but two in left side, then we can select one based on distance.


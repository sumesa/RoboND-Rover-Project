## Project: Mars Rover Sample Pickup Project
## Introduction
A robot can be defined as a machine that can carry out the following 3 steps: perception, decision making and Action. The following mars rover project helps gain a better understand these 3 basic laws of robotics.
The goal of this project was give the rover the ability to percieve its surrounding with the help of the camera mounted in the front. Allow it make decisions such as obstacle navigation, identify rock samples, and take appropriate decisions such as picking up the rock samples, throttle or apply brakes.
[images1]: .misc/rover_image.jpg
## Perception
Perception can be defined as the rovers ability to see things, giving the rovers its eyes. The camera in front of the rover captures 160 by 320 pixel size RGB images at 25fps. Images captured from the camera need to be processed in order for the robot to make sense of it. In the case of rover image processing achieved by applying color thresholds; transfroming the 2d image into a 3d persective and then converting the image frame into the rovers co-oridinate frame of reference. Each of the steps are explained in detail below: 
### Perspective transaform
The images recevied from the rover's camera are 8 bit images with intensity range of 0 to 255. Since they are 2d images, they lack important information about the rover, such as the position of the obeject with respect to the rover in the image received, etc. To obtain this information, perspective transform is performed on the received rovers image as seen below [image 4]. Perspective transfrom helps map 3d points on 2d image plane. Thus providing images which can be used to map the differnt types of areas defined in image thresholding.  To understand the position of the surrounding objects on the transformed image' each image is divided into 10*10 $${pix}^2$$ gird, where each block resembles $$0.1*0.1{m}^2$$ area.
### Color Threshold
To provide the robot with the ability to understand the images it is receiving the image is filtered into binary channels based on the thresold range they fall in. Image thresholding allows the rover to transform raw perspective transformed images into rover specific vision data. Allowing the rover to make sense of what its surronding. In the figure [images 2] it can be observed that the navigable ground area has lower threshold value than the landscape. Thus pixels with threshold values above 160 are set as obstacle area while lower than 160 as navigable. While the pixel thresholds that fall in the range of `[20,100,100] to [30,255,255]` set as rock samples. 
[image 3]. 
### Cooridnate Transform
The input images are still in image pixels cooridnate system and are requrired to be transformed into the rovers perspective. Transforming the image into rover-centric coordinate system will help dertermine the surronunding in rover's perspective. Allowing the rover to make decisions based on the different types of thresholded pixels. This cooridnate transform is done with the help of moving the rover at the bottom center of every image received as shown in image 4. 
[images2]: 
[images3]:

## Decision Making
Once the rover completes the image procession it is required to perform specifc actions. This is done by creating a decsion tree, giving rover the intelligence to work in specific environments. The task the rover was to navigate through a given terrain and pickup all the available rock samples.
The decision tree is primiraly broken down into 3 modes `forward , stop and seen_rock` with the initial default set to throttle at maximum speed. 
As the rover moves forward it checks if there is any obstacle in its near vision `np.sum(Rover.vision_image[130:150, 150:170, 0]) < 160`. If path is clear then check if there is a rock in the image.









#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  



![alt text][image3]



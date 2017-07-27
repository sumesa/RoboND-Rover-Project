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

## Decision Making and Actions
Once the rover completes the image procession it is required to perform specifc actions. This is done by creating a decsion tree, giving rover the intelligence to work in specific environments. The task the rover was to navigate through a given terrain and pickup all the available rock samples.
The decision tree is primiraly broken down into 3 modes `forward , stop and seen_rock` with the initial default set to throttle at maximum speed. 
As the rover moves forward it checks if there is any obstacle in its near vision `np.sum(Rover.vision_image[130:150, 150:170, 0]) < 160`. If path is clear then check if there is a rock in the image. But if there are 2 rocks in visible at the same time then the robot dosenot understand which to pick. For this reason we check if there is a rock present only on the right side of the rovers vision `np.any(Rover.vision_image[130:150,150:320,1])`from the center of the rover. If a rock is visibile then the rock_seen mode is enabled. In other case it keeps going forward with steer set to be clipped under -15 to 15 degrees of mean navigable angles.
If there are any obstacles then stop mode is enabled. In stop mode brakes are release and the rover starts to steer till it finds a clear path. Once the path is clear then then the forward mode is enabled. The stop mode enables the rover to handle braking and steer to find clear path. 

The actions taken by the rover are moving forward, detection of rock samples and then pick them up and th stop when needed. All actions are performed based on the processed images received from the rovers camera.

## Conclusion
Overall the project provided a great learing opprtunity to understand image processing and the basics of building a decision tree. It help gain an basic understanding of to process telemetry data and Image processing.
Few of the challenges that are still to be overcome:
* Navigating through routes which have the landscape shadows on them. When applied with perspective transform the landscapae shadows appear darker resembling obstacle areas but in reality are just navigable areas. 
* Enhancing the decision tree to steer in both the directions in stop mode. Tried to provide the steering based on the max possible navi angles. But there would occur scenarios wherein the robot would get stuck in a mode where the sum of nav angles are same on both ends causing it to just break.
* Getting the rover out of the round loop it gets stuck it while trying to navigate.
* Getting fedility to improve above 70%.
* Making the rover to select co-ordinates based on validating if it had visited that specific map area. 



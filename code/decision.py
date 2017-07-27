import numpy as np
import cv2
# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def identify_navigable(img, rgb_thresh=(157, 157, 158)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

# Identify pixels below the threshold
def identify_obstacles(obstacle_img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(obstacle_img[:,:,0])
    # Require that each pixel be below all three threshold values in RGB
    # below_thresh will now contain a boolean array with "True"
    # where threshold was met
    below_thresh = (obstacle_img[:,:,0] < rgb_thresh[0]) \
                & (obstacle_img[:,:,1] < rgb_thresh[1]) \
                & (obstacle_img[:,:,2] < rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[below_thresh] = 1
    # Return the binary image 
    return color_select

# Identufy pixels between a specific color range to identify colored rock
def identify_rock(obstacle_img):
    # convert color space
    img_bgr = obstacle_img[..., : : -1]
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # define range of yellow color in HSV
    lower_yellow = np.array([20,100,100])
    upper_yellow = np.array([30,255,255])

    # Threshold the HSV image to get only yellow colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    color_select = np.zeros_like(obstacle_img[:,:,0])

    mask = mask > 0
    color_select[mask] = 1
    return mask

# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
    
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    mask =  cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1],img.shape[0]))
    return warped, mask 


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    image=Rover.img
    scale = 10
    dst_size = 5 
    bottom_offset = 6
    world_size = Rover.worldmap.shape[0]
    xpos, ypos = Rover.pos
    # 1) Define source and destination points for perspective transform
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                  [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  ])
    # 2) Apply perspective transform
    perspective_transformed_image, masked_image=perspect_transform(image,source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable_image=identify_navigable( perspective_transformed_image)
    #Apply color threshold to identify obstacles
    obstacle_image=np.absolute(np.float32(navigable_image)-1)*masked_image
    #identify_obstacles( perspective_transformed_image)
     #Apply color threshold to identify rocks
    rock_image = identify_rock( perspective_transformed_image)
    #returns true if rock_image contains only 0
    all_zeros = not np.any(rock_image)
    
    # 4) Update Rover.vision_image (this will be displayed on left side of screen) to obstacle color-thresholded binary image
    Rover.vision_image[:,:,0] = obstacle_image * 255
    #Update Rover.vision_image (this will be displayed on left side of screen) to rock_sample color-thresholded binary image
    Rover.vision_image[:,:,1] = rock_image *255
    #Update Rover.vision_image (this will be displayed on left side of screen) to navigable color-thresholded binary image   
    Rover.vision_image[:,:,2] = navigable_image * 255

    # 5) Convert map image pixel values to rover-centric coords
    #returns the rover-centric coords for navigable image
    xpix_navigable, ypix_navigable = rover_coords(navigable_image)
    #returns the rover-centric coords for obstacle image
    xpix_obstacles, ypix_obstacles = rover_coords(obstacle_image)
    #returns the rover-centric coords for rock image only if the image matrix is not all 0
    if all_zeros is False:
        xpix_rock, ypix_rock = rover_coords(rock_image)

    # 6) Convert rover-centric pixel values to world coordinates
    # returns world coordinates for over-centric coords for navigable coords
    navigable_x_world, navigable_y_world=pix_to_world(xpix_navigable, ypix_navigable,\
                                      np.float32(xpos),np.float32(ypos),\
                                      np.float32(Rover.yaw),world_size, scale)
    # returns world coordinates for over-centric coords for obstacle coords
    obstacle_x_world, obstacle_y_world=pix_to_world(xpix_obstacles, ypix_obstacles,\
                                     np.float32(xpos),np.float32(ypos),\
                                     np.float32(Rover.yaw),world_size, scale)
    # returns world coordinates for over-centric coords for rock image coords
    if all_zeros is False:
        rock_x_world,rock_y_world=pix_to_world(xpix_rock, ypix_rock,\
                                np.float32(xpos),np.float32(ypos),\
                                np.float32(Rover.yaw),world_size, scale)
   
    # 7) Update Rover worldmap (to be displayed on right side of screen)
    #Update Rover worldmap with obstacle image
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    #Update Rover worldmap with rocks
    if all_zeros is False: 
        Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    #Update Rover worldmap with navigable image    
    Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Calculate Rover pixel distances and angles
    rover_centric_pixel_distances, rover_centric_angles = to_polar_coords(xpix_navigable, ypix_navigable)
    rover_centric_obs_dists , rover_centric_obs_angles = to_polar_coords(xpix_obstacles, ypix_obstacles)
    if all_zeros is False: 
        rover_centric_rock_distances, rover_centric_rock_angles = to_polar_coords(xpix_rock, ypix_rock)
   # Define Rover pixel distances
    Rover.nav_dists = rover_centric_pixel_distances
    # Define Rover pixel angle
    Rover.nav_angles = rover_centric_angles
    Rover.obs_angles = rover_centric_obs_angles
    Rover.obs_dists = rover_centric_obs_dists
    if all_zeros is False:
        Rover.rock_dists = rover_centric_rock_distances
        print("Rock distance initalized in perception")
        Rover.rock_angles = rover_centric_rock_angles
        print("Rock distance initalized in perception  min",np.min(Rover.rock_dists), "  and mean ", np.mean(Rover.rock_angles))
    return Rover

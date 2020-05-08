# Sous-Chef
**Sous-chef: The digital cooking assistant**

[Final Presentation Video](https://youtu.be/cTHWWE7bAkg)

# Contents
* README - this file
* code
  * audio - folder of all the audio files for Sous-chef's responses
  * pyleap_master - Eran Egozy's python bindings for the Leap Motion API
  * ui - folder of all of the graphics used for the GUI
  * requirements.txt - all of the python packages required to run Sous-Chef
  * sous.kv - the kivy file which defines Sous-chef's UI
  * **sous_chef.py** - Sous-chef's main file


# Requirements
## Hardware
 * Webcam
 * Leap Motion Controller
 * A cooking surface

## Software
All necessary python packages are defined in requirements.txt

Sous-chef was built using python version 3.7 on a Windows machine. I have note tested it on a Mac.

# How to Install
1. Download Sous-chef from github
2. Open up the command prompt
3. Run _pip install -r requirements.txt_ to download the necessary python libraries

# How to Use Sous-Chef
## Startup
1. Setup your webcam above your cooking surface
2. Set the temperature to about 375-400°
3. Plug in the webcam and leap motion controller to a laptop off to the side
4. Open up the command prompt and navigate to where you saved the Sous-chef code
5. Run __python sous_chef.py__
6. Click start
7. Select your desired level of doneness
8. Get cooking! - cook as you normally would while following Sous-chef's queues, it will automatically pick up every patty you add to the cooking surface

## Burger Query
To ask how long until a burger is done, wave your hand above the leap motion controller until you see the cursor show up on the screen. The cursor should look like a small white circle. Point to the burger you would like to ask about, move your hand in towards the screen until the cursor turns green. Once it turns green the system will answer your query about whichever burger is under the cursor. 

## Exiting
To quit Sous-Chef press the 'q' key on your keyboard.

# Troubleshooting
Try the steps listed in order to solve the following common problems.
## Flickering burgers
 * Nudge the patty under which the flickering is centerred
 * If the keep overlapping, increase the value of MIN_DIST in sous_chef.py
 * Try adjusting the height of the camera above the cooking surface.
## Circles are stable but aren't on patties
 * Adjust the circle detection paramters in sous_chef.py: PATTY_SIZE_MIN and PATTY_SIZE_MAX
## Burgers are over/underdone
 * In sous_chef.py, adjust the values in the dictionary COOK_TIMES according to the patties you are using. Take into account temperature, patty thickness, frozen/thawed patties, etc.

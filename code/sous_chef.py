"""
Sous-chef : 
The cooking assistant that helps you learn how to know when you're food's done

By: Tosin Olabinjo
Last edited: 4/7/2020

"""
import cv2
import numpy as np
import time
import kivy
from kivy.app import App
from kivy.uix.widget import Widget

#credit: https://stackoverflow.com/questions/37749378/integrate-opencv-webcam-into-a-kivy-user-interface
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from gtts import gTTS
from playsound import playsound as ps
import os

# credit:
#from pyleap.leap import getLeapInfo, getLeapFrame
GRID_W = 5
GRID_H = 5
SHIFT_LIMIT = 30

BURGER_LINE = 2
THICK_LINE = 4

BURGER_STATES = ["new" , "flip" , "done" , "overdone"]

BURGER_COLOR = { 
    "new":(255, 155, 0),
    "flip":(0, 255, 255),
    "done":(77, 255, 77),
    "overdone":(0 , 0, 255),
    "flipped":(180, 175, 100)

}
#TODO - update colors and states - flip state and color? 
#OR two round of states - before and after flip?

#turn into dict for rare, medium, and well_done
#check actual times after debugging
DONE_TIMES = {
    "new" : 0,
    "flip" : 30 , 
    "done" : 60,
    "overdone" : 100
}
REM_TIME = 30
FLIP_MIN = 5

MIN_DIST = 80


class StartWind(Widget):
    pass
    # def build(self):
    #     print("idk")


class KivyCV(Image):
    def __init__(self, capture, fps, **kwargs):
        Image.__init__(self, **kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faceCascade = cv2.CascadeClassifier("lbpcascade_frontalface.xml")
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags = cv2.CASCADE_SCALE_IMAGE
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            buf = cv2.flip(frame, 0).tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture


class CookWind(Widget):
    def build(self):
        # print("built cookwind")
        # self.img1=Image()
        # print("making layout")
        # layout = BoxLayout()
        # print("affing cv img")
        # layout.add_widget(self.img1)

        # print("started capture")
        # #opencv2 stuffs
        # self.capture = cv2.VideoCapture(0)
        
        # print("first frame")
        # ret, frame = self.capture.read()
        # # display image from cam in opencv window
        # cv2.imshow("CV2 Image", frame)

        # cv2.namedWindow("CV2 Image")
        # Clock.schedule_interval(self.update, 1.0/33.0)
        # return layou
        print("startcook")
        self.capture = cv2.VideoCapture(0)
        my_camera = KivyCV(capture=self.capture, fps=60)
        return my_camera
    
    def on_stop(self):
        self.capture.release()

    # def update(self, dt):
    #     print("called update")
    #     #get frame from camera
    #     ret, frame = self.capture.read()
        
    #     #---perform operations on image here

    #     #-----

    #     # display image from cam in opencv window
    #     cv2.imshow("CV2 Image", frame)

    #     # convert it to texture
    #     buf1 = cv2.flip(frame, 0)
    #     buf = buf1.tostring()
    #     texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
    #     #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
    #     texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
    #     # display image from the texture
    #     self.img1.texture = texture1
        

class SousApp(App):
    def build(self):
        #cur_window = StartWind()
        cur_window = CookWind()
        #print("started sous")
        #return CookWind()
        return cur_window


def do_cv():
    cap = cv2.VideoCapture(0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        cv2.imshow('frame',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def do_cv_circle(chef):
    cap = cv2.VideoCapture(1)
    

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Convert to grayscale. 
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        
        # Blur using 3 * 3 kernel. 
        gray_blurred = cv2.blur(gray, (3, 3)) 
        
        # Apply Hough transform on the blurred image. 
        detected_circles = cv2.HoughCircles(gray_blurred,  
                        cv2.HOUGH_GRADIENT, 1, MIN_DIST, param1 = 50, 
                    param2 = 30, minRadius = 40, maxRadius = 80) 

        missing_burgers = chef.all_burgers.copy()
        
        # Draw circles that are detected. 
        if detected_circles is not None: 
            #this is where i would run the burgers function and it will output the actual outlines to draw
        
            # Convert the circle parameters a, b and r to integers. 
            detected_circles = np.uint16(np.around(detected_circles)) 

        
            for pt in detected_circles[0, :]: 
                a, b, r = pt[0], pt[1], pt[2] 
                
                chef.set_frame((frame.shape[1] , frame.shape[0])) #change this to a cook-cv class characteristic that gets passed in
                patty = chef.check_burgers(a,b,r)
                if patty.name in missing_burgers.keys():
                    del(missing_burgers[patty.name])
                print(patty.name , patty.cur_state, time.time())
                #if(patty.flipped): print ("is_flipped")
        
                cv2.circle(frame, patty.coords, patty.rad, patty.color, patty.line_weight) 
        
        #check through chef's burgers to see if any burgers in his list weren't detected
        #maybe handling overall missing burgers in other main method
        chef.check_missing(missing_burgers) 

        #flip images
        frame = cv2.flip(frame , 1)
        frame = cv2.flip(frame , 0)
        #resize image
        #cv2.namedWindow("main", cv2.WINDOW_NORMAL)
        scale_ratio = 1.75 # percent of original size
        width = int(frame.shape[1] * scale_ratio)
        height = int(frame.shape[0] * scale_ratio)
        dim = (width, height)
        # resize image
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        
        # Display the resulting frame
        cv2.imshow("main", resized)
        #cv2.imshow('blurred img' , gray_blurred)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    return


class speaker(object):
    def __init__(self):
        self.state_msgs = {
            "new" : "",
            "flip": "This burger is ready to be flipped",
            "done": "This burger is ready",
            "overdone" : "This burger is starting to overcook"
        }
        

    def play_state(self, b_state):
        #create audio file if it doensn't exist
        a_file = os.getcwd() + "/audio/states/"+b_state+".wav"
        if not os.path.isfile(a_file):
            speech = gTTS(text = self.state_msgs[b_state] , lang = 'en', slow = False)
            speech.save(a_file)
        ps(self.state_msgs[b_state])
        return

    #TODO - need functions for done time answer & processing input speech




class burger(object):
    '''class that defines burger patty and methods to check it'''
    def __init__(self, x , y , rad):
        #find way to unique name burgers based on location
        self.name = "burg-"+str(int(x/10))+"-"+str(int(y/10))

        self.time_to_cook = None #later adjust cooktimes based on size of patty
        self.start_time = time.time()

        #patty.coords, patty.rad, patty.color, patty.line_weight) 
        self.coords = (x, y)
        self.rad = rad
        self.cur_state = "new"
        self.color = BURGER_COLOR[self.cur_state]
        self.line_weight = BURGER_LINE

        self.do_update = True

        self.time_gone = 0
        self.time_seen = 0
        self.flipped = False

    def check_gone(self, chef):
        gone_delt = time.time() - self.time_seen
        self.time_gone = gone_delt
        
        if gone_delt > REM_TIME:
            chef.remove_burger(self)
            print("removed", self.name)
        
        return


    def check_done(self,x,y):
        '''method that updates doneness state of the food based on time passed'''
        old_state = self.cur_state
        time_delt = time.time() - self.start_time
        self.time_seen = time.time()

        #TODO - have to tracks, before and after flip: will look at different times and colors
        
        
        #update location if significantly different
        if abs(self.coords[0] - x) > SHIFT_LIMIT and abs(self.coords[1] - y > SHIFT_LIMIT):
            self.coords = (x,y)

        #check the sone state
        for state in BURGER_STATES:
            if time_delt >= DONE_TIMES[state]:
                self.cur_state = state


        #check if flipping #TODO - replace with color ? test!
        #TODO - change state track based on flip or not, two lists, two sets of colors?
        if self.cur_state == "flip" and self.time_gone > FLIP_MIN and self.flipped == False:
            #for now, pretend being flipped is "new" on the other side
            self.flipped = True
            self.cur_state = "new"
            self.color = BURGER_COLOR["flipped"]
            self.start_time = time.time()
            print("flipped", self.name)

            return

        #if it's already been flipped, once it gets back to that state it should be done
        if self.cur_state == "flip" and self.flipped:
            self.cur_state = "done"

        #update outline color
        if self.cur_state != old_state:
            self.color = BURGER_COLOR[self.cur_state]
            #self.do_update = True

        #TODO - add in audio here, change to elifs so flipping doesn't break

        return




class sous_chef(object):
    '''
    Class that manages the main workflow of sous-chef
    '''
    def __init__(self):
        self.running = True
        self.cur_window = None #later start with start, for now go straight to cooking 
        self.burgers = [[None]*GRID_W]*GRID_H
        self.all_burgers = {}
        #self.camera_feed
        self.frame_dims = (-1,-1) #w,h

    
    def set_frame(self, coords):
        self.frame_dims = coords

    def grid_loc(self, x , y):
        x_b = int( (x * 5) / self.frame_dims[0])
        y_b = int( (y * 5) / self.frame_dims[1])
        return (x_b , y_b)
        
    
    def check_burgers(self , x , y, r):
        new_patty = burger(x , y, r)

        x_b, y_b = self.grid_loc(x,y)

        #check if brand new, new location of old, or just old

        if self.burgers[y_b][x_b] == None:
            self.burgers[y_b][x_b] = new_patty
            self.all_burgers[new_patty.name] = (x_b, y_b)
            print("brand new")
            return new_patty
        else:
            this_patty = self.burgers[y_b][x_b]
            this_patty.check_done(x,y)
            return this_patty

    def check_missing(self, missing_burgs):
        for burg in missing_burgs.keys():
            x,y = missing_burgs[burg]
            self.burgers[y][x].check_gone(self)

    def remove_burger(self, burger):
        b_loc = self.all_burgers[burger.name]
        del(self.all_burgers[burger.name])
        self.burgers[b_loc[1]][b_loc[0]] = None
        return
              

    def show_start(self):
        pass

    def run(self):
        #start window
        #SousApp().run()

        #start cooking
        do_cv_circle(self)

        return





def main():
    sc = sous_chef()
    sc.run()
    # #close window after running stops
    # cv2.destroyAllWindows()

    #do_cv()
    

    return

if __name__ == "__main__":
    main()
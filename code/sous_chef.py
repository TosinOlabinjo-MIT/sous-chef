"""
Sous-chef : 
The cooking assistant that helps you learn how to know when you're food's done

By: Tosin Olabinjo
Last edited: 4/13/2020

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
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from gtts import gTTS
import winsound
import sounddevice as sd
import soundfile as sf
from playsound import playsound as ps
from pydub import AudioSegment
import os

# credit:
from time import sleep
import sys
#sys.path.insert(0, os.path.abspath('..'))
from pyleap_master.pyleap.leap import getLeapInfo, getLeapFrame


GRID_W = 5
GRID_H = 5
SHIFT_LIMIT = 30

MIN_DIST = 300

BURGER_LINE = 2
THICK_LINE = 5
THICK_TIME = 2

BURGER_STATES = ["new" , "flip" , "done" , "overdone"]

BURGER_COLOR = { 
    "new":(255, 155, 0),
    "flip":(0, 255, 255),
    "done":(77, 255, 77),
    "overdone":(0 , 0, 255),
    "flipped":(200, 10, 100)

}

CURSOR_COLOR = (255, 255, 255)

#turn into dict for rare, medium, and well_done
#check actual times after debugging

#adjust times and time dictionaries later
# MED_COOK_TIME = 60
# RARE_COOK_TIME = 45
# WELL_COOK_TIME = 90


COOK_TIMES = {
             "Rare":
                {
                "pre-flip":{ 
                    "new" : 0,
                    "flip" : 20 , 
                    "done" : float("inf"),
                    "overdone" : 45
                            },
                "post-flip":{
                    "new" : 0,
                    "flip" : float("inf") , 
                    "done" : 20,
                    "overdone" : 45
                            }
                },
            "Med":
                {
                "pre-flip":{ 
                    "new" : 0,
                    "flip" : 30 , 
                    "done" : float("inf"),
                    "overdone" : 60
                            },
                "post-flip":{
                    "new" : 0,
                    "flip" : float("inf") , 
                    "done" : 30,
                    "overdone" : 60
                            }
                },
            "Well":
                {
                "pre-flip":{ 
                    "new" : 0,
                    "flip" : 45 , 
                    "done" : float("inf"),
                    "overdone" : 90
                            },
                "post-flip":{
                    "new" : 0,
                    "flip" : float("inf") , 
                    "done" : 45,
                    "overdone" : 90
                            }
                }
            }

TOT_COOK_TIMES = {"Rare" : COOK_TIMES["Rare"]["pre-flip"]["flip"] + COOK_TIMES["Rare"]["post-flip"]["done"] , "Med" : COOK_TIMES["Med"]["pre-flip"]["flip"]  + COOK_TIMES["Med"]["post-flip"]["done"], "Well" : COOK_TIMES["Well"]["pre-flip"]["flip"] + COOK_TIMES["Well"]["post-flip"]["done"]}
TOT_TIME = TOT_COOK_TIMES["Med"]

TOT_FLIP_TIMES = {"Rare" : COOK_TIMES["Rare"]["pre-flip"]["flip"] , "Med" : COOK_TIMES["Med"]["pre-flip"]["flip"] , "Well" : COOK_TIMES["Well"]["pre-flip"]["flip"]}
FLIP_TIME = TOT_FLIP_TIMES["Med"]

# DONE_TIMES = {
#     "new" : 0,
#     "flip" : 30 , 
#     "done" : float("inf"),
#     "overdone" : 60
# }
# DONE_TIMES_2 = {
#     "new" : 0,
#     "flip" : float("inf") , 
#     "done" : 30,
#     "overdone" : 60
# }

REM_TIME = 7
FLIP_MIN = 0.75


#----------------UI code------------------------------------
def callback(instance):
    #instance.disabled = True
    val = instance.value
    #print(val)

    #open the correct window
    open_window(val)

    #do only for buttons with commmands? TODO
    #send the command
    #send_command(val)
    
    #play correct audio
    #play_audio(val)
    
    #instance.disabled = False
    
    return

def open_window(button_pressed):
    #open the appropiate window
    
    #bring up doneness selction #TODO
    if button_pressed == "Start":	
        cd_popup = ChooseDone()
        cd_popup.open()
        
        
    #display card reader instructions
    elif button_pressed in ("Rare", "Med", "Well"):
        global TOT_TIME
        global FLIP_TIME
        #set cooktimes based on button press #TODO
        print("Pressed", button_pressed)
        times = COOK_TIMES[button_pressed]
        TOT_TIME = TOT_COOK_TIMES[button_pressed]
        FLIP_TIME = TOT_FLIP_TIMES[button_pressed]
        print(TOT_COOK_TIMES[button_pressed])

        sc = sous_chef(times)
        sc.run()
        
    
    else:
        #display wait msg
        pass
    
    return


class StartWind(Widget):
    pass
    # def build(self):
    #     print("idk")

class ChooseDone(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #rare
        rare_button = self.ids.Rare
        rare_button.bind(on_release = callback)

        #med
        med_button = self.ids.Medium
        med_button.bind(on_release = callback)

        #well done
        well_button = self.ids.Well_done
        well_button.bind(on_release = callback)

class SousApp(App):
    def build(self):
        start_window = StartWind()
        
        #start button
        start_button = start_window.ids.start_button
        start_button.bind(on_release = callback)

        return start_window

#------------------------------------------------



#------------Cooking Code--------------------------

class cv_cooktop(object):
    def __init__(self, cam = 1):
        self.cap = cv2.VideoCapture(cam)
        
    def get_circles(self):
         # Capture frame-by-frame
        ret, frame = self.cap.read()

        #flip images
        frame = cv2.flip(frame , 1)
        frame = cv2.flip(frame , 0)

        # resize image
        scale_ratio = 1.75 # percent of original size
        width = int(frame.shape[1] * scale_ratio)
        height = int(frame.shape[0] * scale_ratio)
        dim = (width, height)
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        
        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Convert to grayscale. 
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        
        # Blur using 3 * 3 kernel. 
        gray_blurred = cv2.blur(gray, (3, 3)) 
        
        # Apply Hough transform on the blurred image. 
        detected_circles = cv2.HoughCircles(gray_blurred,  
                        cv2.HOUGH_GRADIENT, 1, MIN_DIST, param1 = 50, 
                    param2 = 30, minRadius = 95, maxRadius = 115) 

        if detected_circles is None: 
            return ([], frame)
                
        # Convert the circle parameters a, b and r to integers. 
        detected_circles = np.uint16(np.around(detected_circles))

        return (detected_circles, frame)
        
        
    def circ_to_burg(self, chef, detected_circles , frame):
        missing_burgers = chef.all_burgers.copy()

        if detected_circles != []:
            for pt in detected_circles[0, :]: 
                a, b, r = pt[0], pt[1], pt[2] 
                
                chef.set_frame((frame.shape[1] , frame.shape[0])) #change this to a cook-cv class characteristic that gets passed in
                #print(chef.frame_dims)
                patty = chef.check_burgers(a,b,r)
                if patty.name in missing_burgers.keys():
                    del(missing_burgers[patty.name])
                #print(patty.name , patty.cur_state, time.time())
                #if(patty.flipped): print ("is_flipped")
                #print(r)
        
                cv2.circle(frame, patty.coords, patty.rad, patty.color, patty.line_weight) 
                #print(patty.coords)

                #draw pie chart timer
                end_angle = ((TOT_TIME - patty.get_time_left()) / TOT_TIME)*360
                
                if patty.flipped: end_angle += 180
                
                if patty.cur_state == "done":
                    #TODO have a - until overdone 
                    pass
                
                if patty.cur_state == "overdone" : 
                    end_angle = 360
                    
                cv2.ellipse(frame, patty.coords, (7,7), -90, 0, end_angle, patty.color, thickness=3, lineType=8, shift=0) 
        
        return (frame , missing_burgers)

    def show_frame(self, frame):
               
        #apply any other transofrmations on the frame     

        # Display the resulting frame
        cv2.imshow("main", frame)
        
        #cv2.imshow('blurred img' , gray_blurred)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        return frame


class speaker(object):
    def __init__(self):
        self.state_msgs = {
            "new" : "",
            "flip": "This burger is ready to be flipped",
            "done": "This burger is done",
            "overdone" : "This burger is starting to overcook on this side"
        }

        self.state_msgs_2 = {
            "new" : "",
            "flip": "This burger is ready to be flipped",
            "done": "This burger is done",
            "overdone" : "This burger is starting to overcook"
        }

        self.flip_end = self.make_clip("seconds until this burger needs to be flipped. ", "flip_end")

        self.done_end = self.make_clip("seconds until this burger is done.", "done_end")
        
        self.flip_phrases = {}

        self.done_phrases = {}

        self.populate_phrases()


    def populate_phrases(self):

        for phrases in ("flip", "done"):
            for mins in range(0,5): #TODO - adjust if there's another max
                if phrases == "flip":
                    self.flip_phrases[mins] = {}
                else:
                    self.done_phrases[mins] = {}
                for secs in range(0,60):
                    if phrases == "flip":
                        #sentence
                        resp = "{0} minutes and {1} seconds until this burger needs to be flipped. ".format(mins, secs)
                        #make audio
                        name = "{0}_{1}_flip-resp".format(mins, secs)
                        #print(name)
                        clip = self.make_clip(resp , name)
                        #save in dict
                        self.flip_phrases[mins][secs] = clip
                    else: #phrases = done
                        resp = "{0} minutes and {1} seconds until this burger is done.".format(mins, secs)
                        #make audio
                        name = "{0}_{1}_done-resp".format(mins, secs)
                        #print(name)
                        clip = self.make_clip(resp , name)
                        #save in dict
                        self.done_phrases[mins][secs] = clip
        return
                    

    def play_state(self, b_state, is_flipped):
        #check audio folder
        a_folder = os.getcwd() + "\\audio\\states\\"
        #a_folder = "C:/sous-chef/code/audio/states/"
        if not os.path.exists(a_folder):
            os.makedirs(a_folder)



        #create audio file if it doensn't exist
        filename = a_folder+b_state
        if is_flipped: filename += "-flip"
        a_file = filename+".mp3"
        a_wav = filename+".wav"
        if not os.path.isfile(a_file):
            sp_text = self.state_msgs_2[b_state] if is_flipped else self.state_msgs[b_state]
            speech = gTTS(text = sp_text, lang = 'en', slow = False)
            speech.save(a_file)
            sound = AudioSegment.from_mp3(a_file)
            sound.export(a_wav, format="wav")

        #play audio  
        if b_state == "overdone":
            winsound.Beep(400,500)  
        #os.system(a_wav)
        #ps(a_wav)
        #winsound.PlaySound(a_wav, winsound.SND_FILENAME)
        data, fs = sf.read(a_wav, dtype='float32')  
        sd.play(data, fs)
        #status = sd.wait()  # Wait until file is done playing
        return

    def make_clip(self, script, name):
        #check audio folder
        a_folder = os.getcwd() + "\\audio\\resp\\"
        #a_folder = "C:/sous-chef/code/audio/states/"
        if not os.path.exists(a_folder):
            os.makedirs(a_folder)


        #create audio file if it doensn't exist
        filename = a_folder+ name
        a_file = filename+".mp3"
        a_wav = filename+".wav"
        if not os.path.isfile(a_file):
            sp_text = script
            speech = gTTS(text = sp_text, lang = 'en', slow = False)
            speech.save(a_file)
            sound = AudioSegment.from_mp3(a_file)
            sound.export(a_wav, format="wav")

        return a_wav

    def say(self, script):
        #check audio folder
        a_folder = os.getcwd() + "\\audio\\resp\\"
        #a_folder = "C:/sous-chef/code/audio/states/"
        if not os.path.exists(a_folder):
            os.makedirs(a_folder)


        #create audio file if it doensn't exist
        filename = a_folder+"resp" #TODO - change this
        a_file = filename+".mp3"
        a_wav = filename+".wav"
        #if not os.path.isfile(a_file):
        sp_text = script
        speech = gTTS(text = sp_text, lang = 'en', slow = False)
        speech.save(a_file)
        sound = AudioSegment.from_mp3(a_file)
        sound.export(a_wav, format="wav")


        #play audio
        data, fs = sf.read(a_wav, dtype='float32')  
        sd.play(data, fs)

        return

    #TODO - need functions for done time answer & processing input speech

    def say_time_left(self, time_left , burger):

        tot_time = time_left
        #resp = "" 

        if not burger.flipped:
            min_flip = int(time_left/60.0)
            sec_flip = int(time_left%60)
            #resp += "{0} minutes and {1} seconds until this burger needs to be flipped. ".format(min_flip, sec_flip)
            # resp += "{0} minutes and {1} ".format(min_flip, sec_flip)
            # tot_time = time_left + burger.time_after_flip
            # self.say(resp)
            # time.sleep(1.8)
            #play premade end
            aud = self.flip_phrases[min_flip][sec_flip]
            data, fs = sf.read(aud, dtype='float32')  
            sd.play(data, fs)
            
            
        else:
            min_left = int(tot_time/60.0)
            sec_left = int(tot_time%60)
            # #resp += "{0} minutes and {1} seconds until this burger is done.".format(min_left, sec_left)
            # resp += "{0} minutes and {1} ".format(min_left, sec_left)
            # self.say(resp)
            # time.sleep(1.8)
            # #play premade end
            aud = self.done_phrases[min_left][sec_left]
            data, fs = sf.read(aud, dtype='float32')  
            sd.play(data, fs)

        # self.say(resp)
        return
        


class burger(object):
    '''class that defines burger patty and methods to check it'''
    def __init__(self, x , y , rad):
        #find way to unique name burgers based on location
        self.name = "burg-"+str(int(x/10))+"-"+str(int(y/10))

        self.time_to_cook = TOT_TIME #later adjust cooktimes based on size of patty
        self.time_to_flip = FLIP_TIME
        self.time_after_flip = int(self.time_to_cook/2)
        self.start_time = time.time()

        #patty.coords, patty.rad, patty.color, patty.line_weight) 
        self.coords = (x, y)
        self.rad = rad
        self.cur_state = "new"
        self.color = BURGER_COLOR[self.cur_state]
        self.line_weight = BURGER_LINE

        #self.do_update = True

        self.delt_gone = 0
        self.time_seen = time.time()
        self.flipped = False
        self.time_thick = time.time()

    def check_gone(self, chef):
        gone_delt = time.time() - self.time_seen
        self.delt_gone = gone_delt
        #print(gone_delt)
        
        if gone_delt > REM_TIME:
            chef.remove_burger(self)
            print("removed", self.name)
        
        return

    def get_time_left(self):
        time_cooked = time.time() - self.start_time
        #returns it in seconds
        time_left = self.time_to_cook - self.time_to_flip - time_cooked
        #also return until done or until flip
        return (time_left)

    def get_time_flip(self):
        time_cooked = time.time() - self.start_time
        #returns it in seconds
        time_left = self.time_to_flip - time_cooked
        #also return until done or until flip
        return (time_left)


    def update(self,x,y, chef):
        '''method that updates doneness state of the food based on time passed'''
        old_state = self.cur_state
        time_delt = time.time() - self.start_time
        self.time_seen = time.time()

        speaker = chef.speak
        cook_times = chef.cook_times
              
        #update location if significantly different
        if abs(self.coords[0] - x) > SHIFT_LIMIT and abs(self.coords[1] - y > SHIFT_LIMIT):
            self.coords = (x,y)

        #update line thickness if used for emphasis
        if self.line_weight == THICK_LINE and time.time() - self.time_thick > THICK_TIME:
            self.line_weight = BURGER_LINE

        #update state based on which side it's on
        if not self.flipped:
            #check the done state
            for state in BURGER_STATES:
                if time_delt >= cook_times["pre-flip"][state]:
                    self.cur_state = state


            #check if flipping #TODO - replace with color ? test!
            if (self.cur_state == "flip" or self.cur_state == "overdone") and not self.flipped and self.delt_gone > FLIP_MIN:
                #for now, pretend being flipped is "new" on the other side
                self.flipped = True
                self.cur_state = "new"
                self.color = BURGER_COLOR["flipped"]
                self.start_time = time.time()
                print("flipped", self.name)

                return
        
        #if it has been flipped
        else:
            #check the done state
            for state in BURGER_STATES:
                if time_delt >= cook_times["post-flip"][state]:
                    self.cur_state = state

            #if it's already been flipped, once it gets back to that state it should be done
            if self.cur_state == "flip":
                self.cur_state = "done"


        #update outline color
        if self.cur_state != old_state:
            self.color = BURGER_COLOR[self.cur_state]
            if self.cur_state != "new": 
                self.time_thick = time.time()
                self.line_weight = THICK_LINE

                #play state change audio
                speaker.play_state(self.cur_state, self.flipped)
            #self.do_update = True
     
        return

    def flash_thick(self):
        self.time_thick = time.time()
        self.line_weight = THICK_LINE
        return



class sous_chef(object):
    '''
    Class that manages the main workflow of sous-chef
    '''
    def __init__(self , cook_times = COOK_TIMES["Med"]):
        self.running = True
        #self.cur_window = None #later start with start, for now go straight to cooking 
        #self.burgers = [[None]*GRID_W]*GRID_H
        self.burgers = [ [ None for i in range(GRID_W) ] for j in range(GRID_H) ]
        #print(self.burgers)
        self.all_burgers = {}
        #self.missing_burgers = {}
        #self.camera_feed
        self.frame_dims = (-1,-1) #w,h
        self.speak = speaker()

        self.cooktop = cv_cooktop(cam = 0)
        self.is_cooking = True
        self.cook_times = cook_times

        

    
    def set_frame(self, coords):
        self.frame_dims = coords

    def grid_loc(self, x , y):
        #print(self.frame_dims)
        #print(x,y)
        x_b = int( (x * GRID_W) / self.frame_dims[0])
        y_b = int( (y * GRID_H) / self.frame_dims[1])
        #print(x_b , y_b)
        return (x_b , y_b)

    
    def get_burger(self,x,y):
    
        this_burger = self.burgers[y][x]

        #switch x and y?
        return this_burger

    
    def ask_time_left(self, event, x, y , flags, param):
        # if the left mouse button was clicked, record the
        # (x, y) coordinates
        # performed
        # if event == cv2.EVENT_LBUTTONDOWN:
        #     point = (x, y)
        #     #get recording
        
        # check to see if the left mouse button was released
        # elif event == cv2.EVENT_LBUTTONUP:
        #replace this to be leap motion based #TODO
        if event == cv2.EVENT_LBUTTONUP:
            # record the (x, y) coordinates
            point = (x,y)
            
            #send audio to google speech API - #TODO and get actual question

            #convert point to burger loc
            bx,by = self.grid_loc(point[0], point[1])
            print("screen", x, y)
            print('burg', bx, by)
            this_burger = self.get_burger(bx,by) 
            if this_burger == None:
                return
           
            #TODO - highlight burger outline?
            this_burger.flash_thick()

            #answer question about burger
            time_left = -1
            if this_burger.flipped:
                time_left = this_burger.get_time_left()
            else:
                time_left = this_burger.get_time_flip()

            self.speak.say_time_left(time_left , this_burger)

        return

    def ask_time_leap(self, x, y):
  
        # record the (x, y) coordinates
        point = (x,y)
        
        #send audio to google speech API - #TODO and get actual question

        #convert point to burger loc
        bx,by = self.grid_loc(point[0], point[1])
        print("screen", x, y)
        print('burg', bx, by)
        this_burger = self.get_burger(bx,by) 
        if this_burger == None:
            return
    
        this_burger.flash_thick()

        #answer question about burger
        time_left = this_burger.get_time_left()
        self.speak.say_time_left(time_left , this_burger)

        return
        
    
    def check_burgers(self , x , y, r):
        new_patty = burger(x , y, r)

        x_b, y_b = self.grid_loc(x,y)
        #print("screen", x,y)
        #print("burger" , x_b, y_b)
        #check if brand new, new location of old, or just old

        if self.burgers[y_b][x_b] == None:
            
            self.burgers[y_b][x_b] = new_patty
            self.all_burgers[new_patty.name] = (x_b, y_b)
            print("brand new")
            #print(self.burgers)
            return new_patty
        else:
            this_patty = self.burgers[y_b][x_b]
            #TODO - pass in cooktimes from self
            this_patty.update(x,y, self)
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

    def cook(self):
        pinch_state = False
        while(self.is_cooking):
            #get circles
            detected_circles, frame = self.cooktop.get_circles()
            missing_burgers = {}

            #check through circles and update
            #if detected_circles != []:
            frame, missing_burgers = self.cooktop.circ_to_burg(self, detected_circles , frame )
                #check through chef's burgers to see if any burgers in his list weren't detected
                #maybe handling overall missing burgers in other main method
            self.check_missing(missing_burgers) 

            pinch_state, do_ask, hand_pos = self.do_leap_stuff(frame, pinch_state)

            self.cooktop.show_frame(frame)

            #check for questions and answer them
            cv2.setMouseCallback("main", self.ask_time_left)
            
            if do_ask:
                self.ask_time_leap(hand_pos[0], hand_pos[1])



            #check if stopped
            if cv2.waitKey(1) & 0xFF == ord('q'):
                #break
                self.is_cooking = False

        # When everything done, release the capture
        self.cooktop.cap.release()
        cv2.destroyAllWindows()
        return
              

    def do_leap_stuff(self, frame, been_pinched):
        #LEAP stuff----------
        #get hand loc
        #info = getLeapInfo()
        hand = getLeapFrame().hands[0]


        if hand.id != -1:
            hand_x = hand.palm_pos[0]
            hand_y = hand.palm_pos[1]

            # status text
            #status = 'service:{} connected:{} focus:{}  '.format(*[('NO ', 'YES')[x] for x in info])

            #draw hand cursor
            #x_pos = int(np.interp(hand_x, [-200, 200], [0, 1100]))
            x_pos = int(np.interp(hand_x, [-120, 120], [0, 1100]))
            #y_pos = int(np.interp(hand_y, [-200, 200], [800, 100]))
            y_pos = int(np.interp(hand_y, [0, 200], [1100, 100]))

            cv2.circle(frame, (x_pos , y_pos), 3, CURSOR_COLOR, 2) 
            #print(self.frame_dims)
            # print(status)
            # print("hand = ", hand_x , hand_y)
            # print("scaled = ", x_pos , y_pos)

            #check pinch - actually just point toward screen
            #base on fingers ring and middle
            pointer = hand.fingers[1]
            middle = hand.fingers[2]
            ring = hand.fingers[3]
            #print(middle[2] , ring[2])
            print(pointer[2])

            #pinch = ring[2] > -50 and middle[2] > -50 #TODO - tune these params
            pinch = pointer[2] < -120

            if pinch:
                #ask time left based on hand loc
                cv2.circle(frame, (x_pos , y_pos), 3, (10, 225, 0), 2) 
                was_pinched = True
                if not been_pinched:
                    do_ask = True
                    return (was_pinched, do_ask, (x_pos , y_pos))
                
                return (was_pinched, False, (x_pos , y_pos))

        #-------------------
        return (False, False, (-1 , -1))

    def run(self):
        #start window
        #SousApp().run()

        #start cooking
        self.cook()

        return





def main():

    SousApp().run()

    #sc = sous_chef()
    #sc.run()

    # #close window after running stops
    # cv2.destroyAllWindows()
    

    return

if __name__ == "__main__":
    main()
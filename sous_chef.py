"""
Sous-chef : 
The cooking assistant that helps you learn how to know when you're food's done

By: Tosin Olabinjo
Last edited: 4/7/2020

"""


# class food(object):
#     '''parent class that defines food and methods to check it'''
#     def __init__(self):
#         self.cook_time = None
#         self.start_time = None
#         self.done_state = None
#         pass

#     def update_state():
#         '''method that updates doneness state of the food based on time passed'''
#         pass

#     def show_outline(current_state):
#         '''method to color outline of food based on how it done it is'''
#         pass


class burger(object):
    '''class that defines burger patty and methods to check it'''
    def __init__(self):
        self.cook_time = None
        self.start_time = None
        self.done_state = None
        pass

    def update_state():
        '''method that updates doneness state of the food based on time passed'''
        pass

    def show_outline(current_state):
        '''method to color outline of food based on how it done it is'''
        pass


class sous_chef(object):
    '''
    Class that manages the main workflow of sous-chef
    '''
    def __init__(self):
        self.running = True
        pass

    def cook(self):
        '''method for a single cooking run'''
        #start camera feed
        #display camera with overlay?
        #start with edges of pot not visible or say biggest circle is pot later?
        #run burger manager
        #burger manager takes camera feed, updates overlay based on burgers it sees
        pass

    def run(self):
        #create window
        #start window
        #on button press:
        #start cooking
        # cooking exits on button press
        #loop back to start window
        #if not running exit
        pass








def main():
    pass

if __name__ == "__main__":
    pass
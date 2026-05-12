################################## LIBRARIES ########################################################

import random
import time
import button
import button1
import os
#pygame
#pip install pygame
import pygame
from pygame.locals import *
from pygame import mixer
#detection
#pip install numpy, mediapipe, pyautogui
import cv2
import mediapipe as mp
import pyautogui
#firebase
#pip install firebase_admin, pyrebase4
import firebase_admin
from firebase_admin import credentials, db
import pyrebase
import json
import requests

#####################################################################################################

##################################### SETTINGS ######################################################

# Set the initial position of the Pygame window
os.environ['SDL_VIDEO_WINDOW_POS'] = "800,150"

pygame.init()

#_______________________FIREBASE_________________________#

#firebase settings initialization
config = {
    "apiKey": "AIzaSyAJNUfYSuR8bInj88qgIIEVdknfVvae6dQ",
    "authDomain": "final-project-csc-436.firebaseapp.com",
    "databaseURL": "https://final-project-csc-436-default-rtdb.europe-west1.firebasedatabase.app",
    "storageBucket": "final-project-csc-436.appspot.com"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("resources/credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL" : "https://final-project-csc-436-default-rtdb.europe-west1.firebasedatabase.app/"})

#_______________________FRAME_________________________#

# frame settings
clock = pygame.time.Clock()
fps = 30
# Set up a variable to track the last time movement was detected
#we are putting a delay so that the car does not directly jump 2 lanes at a time if there was a lot of unintentional movement
last_movement_time = time.time()

#_______________________MOUSE_________________________#

# mouse settings
# Hand detector
hand_detector = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils
# Get screen size
screen_width, screen_height = pyautogui.size()
# Initialize variables for hand
palm_x = 0
palm_y = 0

#_______________________MOVEMENT_________________________#

# webcam settings
video = cv2.VideoCapture(0)  # 0 channel for the webcam
#assign frame
check, frame1 = video.read()
check, frame2 = video.read()

# coordinates for left and right rectangles for webcam
upperLeftL = (50, 50)
bottomRightL = (200, 300)
upperLeftR = (450, 50)
bottomRightR = (600, 300)
movementR = False
movementL = False

#_______________________SCREEN_________________________#

gameName = 'Dynamic Dodge'
# create the window of pygame
minScreenWidth = 500
minScreenHeight = 500
screenWidth = minScreenWidth
screenHeight = minScreenHeight
screen = pygame.display.set_mode((minScreenWidth, minScreenHeight), pygame.RESIZABLE)
pygame.display.set_caption(gameName)

#placement of the second window
cv2.namedWindow("Movement Detection")
# Move the windows to specific positions on the screen
cv2.moveWindow("Movement Detection", 80, 130)

#_______________________FONTS_________________________#

#font initialization
#font type, size
font40 = pygame.font.Font('resources/images/VarelaRound-Regular.ttf', 40)
font30 = pygame.font.Font('resources/images/VarelaRound-Regular.ttf', 30)
font20 = pygame.font.Font('resources/images/VarelaRound-Regular.ttf', 20)
font10 = pygame.font.Font('resources/images/VarelaRound-Regular.ttf', 10)

#_______________________COLOUR_________________________#

# colour initialization
#(red, green, blue)
black = (10, 10, 10)
white = (255, 255, 255)
green = (76, 208, 56)
grey = (100, 100, 100)
lightgrey = (150, 150, 150)
yellow = (255, 232, 0)
red = (200, 20, 20)

#_______________________COORDINATES_________________________#

# road and marker sizes
#done using proportions
road_width = screenWidth * 0.6 #300 (posistion par rapport a 500)
marker_width = screenWidth * 0.016 #8
marker_height = screenHeight * 0.08 #40

# lane coordinates
left_lane = screenWidth * 0.3 #150
center_lane = screenWidth * 0.5 #250
right_lane = screenWidth * 0.7 #350
lanes = [left_lane, center_lane, right_lane]

# road and edge markers for the rectangles
road = (screenWidth * 0.2, 0, road_width, screenHeight) #100
left_edge_marker = (screenWidth * 0.19, 0, marker_width, screenHeight) #95
right_edge_marker = (screenWidth * 0.79, 0, marker_width, screenHeight) #395

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's initial coordinates
player_x = screenWidth * 0.5 #250
player_y = screenHeight * 0.8 #400

#_______________________RECTANGLES_________________________#

# Input fields coordinates for login page
#(x, y, width, height)
email_box = pygame.Rect(screenWidth * 0.25, screenHeight * 0.29, screenWidth * 0.5, screenHeight * 0.08) #(125, 145, 250, 40)
password_box = pygame.Rect(screenWidth * 0.25, screenHeight * 0.49, screenWidth * 0.5, screenHeight * 0.08) #(125, 245, 250, 40)
display_name_box = pygame.Rect(screenWidth * 0.25, screenHeight * 0.69, screenWidth * 0.5, screenHeight * 0.08) #(125, 345, 250, 40)
sign_in_box = pygame.Rect(screenWidth * 0.21, screenHeight * 0.1, screenWidth * 0.16, screenHeight * 0.08) #(105, 50, 80, 40)
sign_up_box = pygame.Rect(screenWidth * 0.38, screenHeight * 0.1, screenWidth * 0.16, screenHeight * 0.08) #(190, 50, 80, 40)

white_trans_rect = pygame.Surface((screenWidth * 0.6, screenHeight * 0.8)) #((300,400))  # the size of your rect
white_trans_rect.set_alpha(150) # lower number more transparent
white_trans_rect.fill(white) # this fills the entire surface

# coordinates of rect cars to change colours
redRect = pygame.Rect(screenWidth * 0.08, screenHeight * 0.08, screenWidth * 0.2, screenHeight * 0.38) #(40, 40, 100, 190)
blueRect = pygame.Rect(screenWidth * 0.74, screenHeight * 0.08, screenWidth * 0.2, screenHeight * 0.38) #(370, 40, 100, 190)
yellowRect = pygame.Rect(screenWidth * 0.08, screenHeight * 0.5, screenWidth * 0.2, screenHeight * 0.38) #(40, 250, 100, 190)
greenRect = pygame.Rect(screenWidth * 0.74, screenHeight * 0.5, screenWidth * 0.2, screenHeight * 0.38) #(370, 250, 100, 190)

#_______________________VARIABLES_________________________#

# game settings and variables
colour = 'red' #colour of selected car
lockBlue = True #to see if this colour can be selected
lockYellow = True
lockGreen = True
initialSpeed = 8 #speed of movement of the vehicules
speed = initialSpeed
score = 0
lastScore = 0
highScore = 0
coins = 0
displayCoin = 0
sound = True
running = False #running the program of the main game
game = False #for the actual game part where the car is moving
start_menu = False #for the menu at the beginning before the game starts
setting_menu = False #settings menu 
gameplay_menu = False #tutorial
login_menu = True
theme_menu = False
gameover = False #when the player looses the round but did not yet return to the menu or played another round 
right = False #for collision detection
left = False

#for login
email = ''
cutEmail = '' #if email too big to fit inside the email box
password = ''
displayName = ''
cutPassword = '' #if password too big to fit inside the password box
uid = None #user id from Firebse
name = None
errorDisplay = None
activeEmail = False #to see if box is selected
activePassword = False
activeDisplayName = False
signUp = False #to see which page to display
signIn = True

#_______________________SOUNDS_________________________#

#list of songs on the radio
songs = ['drive', 'chase', 'In Dreams', 'Better Day', 'Powerful Trap', 'Titanium']
loadedSongs = []
choiceSong = 0 #which song is selected

#load sounds
crash_sound = pygame.mixer.Sound("resources/sounds/crash_sound.wav")
crash_sound.set_volume(0.50) #volume par rapport au volume de l'ordinateur

spending_money_sound = pygame.mixer.Sound("resources/sounds/spending_money_sound.wav")
spending_money_sound.set_volume(0.50)

#go through the list of songs on the radio to load them
for song in songs:
    song_sound = pygame.mixer.Sound("resources/sounds/" + song +".wav")
    song_sound.set_volume(0.30)
    loadedSongs.append(song_sound)

#_______________________IMAGES_________________________#

#load the crash image
crash = pygame.image.load('resources/images/crash.png')
crash_rect = crash.get_rect() #when crash let the center of the image be the coordinates

#load image
#we use convert_alpha() instead of convert() because it supports transparent backgrounds
bg = pygame.image.load("resources/images/road_background.png")
scaled_bg = bg #use this so the quality stay the same while resizing window
bg_car_view = pygame.image.load("resources/images/bg_car_view.png")
scaled_bg_car_view = bg_car_view
start_img = pygame.image.load('resources/images/start_button.png').convert_alpha()
exit_img = pygame.image.load('resources/images/exit_button.png').convert_alpha()
setting_img = pygame.image.load('resources/images/setting_button.png').convert_alpha()
reload_img = pygame.image.load('resources/images/reload_button.png').convert_alpha()
return_img = pygame.image.load('resources/images/return_button.png').convert_alpha()
sound_img = pygame.image.load('resources/images/sound_button.png').convert_alpha()
not_sound_img = pygame.image.load('resources/images/not_sound_button.png').convert_alpha()
return_back_img = pygame.image.load('resources/images/return_back_button.png').convert_alpha()
gameplay_img = pygame.image.load('resources/images/gameplay_button.png').convert_alpha()
next_img = pygame.image.load('resources/images/next_button.png').convert_alpha()
previous_img = pygame.image.load('resources/images/previous_button.png').convert_alpha()
sign_up_img = pygame.image.load('resources/images/sign_up_button.png').convert_alpha()
sign_in_img = pygame.image.load('resources/images/sign_in_button.png').convert_alpha()
x_img = pygame.image.load('resources/images/x_button.png').convert_alpha()
clear_img = pygame.image.load('resources/images/clear_button.png').convert_alpha()
theme_img = pygame.image.load('resources/images/theme_button.png').convert_alpha()
red_car_img = pygame.image.load('resources/images/car_red.png').convert_alpha()
blue_car_img = pygame.image.load('resources/images/car_blue.png').convert_alpha()
yellow_car_img = pygame.image.load('resources/images/car_yellow.png').convert_alpha()
green_car_img = pygame.image.load('resources/images/car_green.png').convert_alpha()
block_img = pygame.image.load('resources/images/block.png').convert_alpha()

#load the vehicle images
#we put them in a list so we can later choose randomely one
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('resources/images/' + image_filename)
    vehicle_images.append(image)

#_______________________BUTTONS_________________________#

# Initialize the buttons
# button1 for virtual mouse
# button for regular physical mouse
start_button = button1.Button(screenWidth * 0.38, screenHeight * 0.54, start_img) #width, height, object(or image)
exit_button = button1.Button(screenWidth * 0.38, screenHeight * 0.64, exit_img)
setting_button = button1.Button(screenWidth * 0.38, screenHeight * 0.74, setting_img)
reload_button = button1.Button(screenWidth * 0.28, screenHeight * 0.26, reload_img)
return_button = button1.Button(screenWidth * 0.64, screenHeight * 0.26, return_img)
sound_button = button1.Button(screenWidth * 0.38, screenHeight * 0.51, sound_img)
not_sound_button = button1.Button(screenWidth * 0.38, screenHeight * 0.51, not_sound_img)
return_back_button = button1.Button(screenWidth * 0.38, screenHeight * 0.71, return_back_img)
gameplay_button = button1.Button(screenWidth * 0.38, screenHeight * 0.61, gameplay_img)
next_button = button1.Button(screenWidth * 0.88, screenHeight * 0.9, next_img)
previous_button = button1.Button(screenWidth * 0.04, screenHeight * 0.9, previous_img)
sign_up_button = button.Button(screenWidth * 0.52, screenHeight * 0.8, sign_up_img)
sign_in_button = button.Button(screenWidth * 0.52, screenHeight * 0.8, sign_in_img)
x_button = button.Button(screenWidth * 0.86, screenHeight * 0.04, x_img)
clear_button = button.Button(screenWidth * 0.22, screenHeight * 0.8, clear_img)
theme_button = button.Button(screenWidth * 0.86, screenHeight * 0.04, theme_img)

#_______________________LISTS_________________________#

#lists of objects used when resizing
buttonsLogin = [sign_up_button, sign_in_button, x_button, clear_button]

buttonsGame = [start_button, exit_button, setting_button, reload_button, return_back_button,
                return_button, sound_button, not_sound_button, gameplay_button, next_button, 
                previous_button, theme_button]

rectLogin = [email_box, password_box, display_name_box, sign_in_box, sign_up_box]

rectGame = [redRect, blueRect, yellowRect, greenRect]

#####################################################################################################

##################################### FUNCTIONS #####################################################

# Functions to resize objects if resize window
def resizeButton(button, xRatio, yRatio):
    button.rect.topleft = (button.rect.x * xRatio, button.rect.y * yRatio)
    button.image = pygame.transform.smoothscale(button.image, (int(button.image.get_width() * xRatio), int(button.image.get_height() * yRatio)))

def resizeRect(rect, xRatio, yRatio):
    rect.x *= xRatio
    rect.y *= yRatio
    rect.width *= xRatio
    rect.height *= yRatio

def resizeImage(image, xRatio, yRatio):
    return pygame.transform.smoothscale(image, (int(image.get_width() * xRatio), int(image.get_height() * yRatio)))

#function to draw text using the center (where the center of the text is on the coordinates not the top left corner)
def drawTextCenter(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    imgRect = img.get_rect() #get dimensions of the image(here text box)
    imgRect.center = (x, y) #make the center of the text on the coordinates
    screen.blit(img, imgRect)

#function to draw text
def drawText(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x,y))

#function to draw the road background
def drawBackground(lane_marker_move_y):
    # draw the grass
    screen.fill(green)
    # draw the road
    pygame.draw.rect(screen, grey, road) #where to draw, color, coordinates (x, y, width, height)
    # draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)
    #draw the lane markers
    for y in range(int(marker_height * -2), int(screenHeight), int(marker_height * 2)):
        pygame.draw.rect(screen, white, (left_lane + (screenWidth * 0.09), y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + (screenWidth * 0.09), y + lane_marker_move_y, marker_width, marker_height))

def drawColourCar(coins, lockYellow, lockBlue, lockGreen, colour):
    #draw background
    screen.fill(green)
    screen.blit(scaled_bg, (0,0))
    #draw number of coins
    drawTextCenter('Coins: ' + str(coins), font20, black, screenWidth * 0.5, screenHeight * 0.06)
    #draw the different coloured cars
    screen.blit(red_car_img, (screenWidth * 0.1, screenHeight * 0.1)) #(50,50))
    screen.blit(blue_car_img, (screenWidth * 0.76, screenHeight * 0.1)) #(380,50))
    screen.blit(yellow_car_img, (screenWidth * 0.1, screenHeight * 0.52)) #(50,260))
    screen.blit(green_car_img, (screenWidth * 0.76, screenHeight * 0.52)) #(380,260))

    #see which colour is selected to see where to draw a black rectangle around the corresponding car
    if colour == 'yellow':
        pygame.draw.rect(screen, black, yellowRect, 4)
    elif colour == 'blue':
        pygame.draw.rect(screen, black, blueRect, 4)
    elif colour == 'green':
        pygame.draw.rect(screen, black, greenRect, 4)
    elif colour == 'red':
        pygame.draw.rect(screen, black, redRect, 4)

    #see which car is locked to see if a block image will be added on top
    #with the number of coins needed to unlock it
    if lockYellow:
        screen.blit(block_img, (screenWidth * 0.15, screenHeight * 0.68)) #(75, 340))
        drawTextCenter('price: 10 coins', font10, black, screenWidth * 0.18, screenHeight * 0.9) #90, 450)
    if lockGreen:
        screen.blit(block_img, (screenWidth * 0.81, screenHeight * 0.68)) #(405,340))
        drawTextCenter('price: 15 coins', font10, black, screenWidth * 0.84, screenHeight * 0.9) #420, 450)
    if lockBlue:
        screen.blit(block_img, (screenWidth * 0.81, screenHeight * 0.26)) #(405, 130))
        drawTextCenter('price: 5 coins', font10, black, screenWidth * 0.84, screenHeight * 0.48) #420, 240)

def drawGameplay():
    screen.fill(green)
    screen.blit(scaled_bg, (0,0))
    drawText('1.Move the car left or right:', font20, black, screenWidth * 0.2, screenHeight * 0.24) #205, 120)
    drawText('by moving inside the rectangles', font20, black, screenWidth * 0.2, screenHeight * 0.32) #225, 160)
    drawText('or using the arrows on the keyboard', font20, black, screenWidth * 0.2, screenHeight * 0.38) #245, 190)
    drawText('2.Dodge other cars to avoid crashing', font20, black, screenWidth * 0.2, screenHeight * 0.5) #250, 250)
    drawText('3.Have fun!', font20, black, screenWidth * 0.2, screenHeight * 0.62) #128, 310)

def drawRadio(choiceSong):
    #draw the bottom of the radio
    pygame.draw.rect(screen, black, (0, screenHeight * 0.98, screenWidth, screenHeight * 0.02), 0) #0 at the end to indicate that rectangle is filled
    # if a number is placed instead of 0 it will be the width of the borders of rectangles and it will be empty inside
    displayName = False
    widthRadio = screenWidth - (screenWidth * 0.2) #place for the previous and next button
    x = screenWidth * 0.16 #80 #starting point to draw
    #loop through the list of songs
    for song in songs:
        #for each song draw a black rectangles (like teeth)
        pygame.draw.rect(screen, black, (x - (screenWidth * 0.01), screenHeight * 0.95, screenWidth * 0.02, screenHeight * 0.05), 0)
        if songs[choiceSong] == song:
            displayName = True
            #draw a red rectangle to know the song is selected
            pygame.draw.rect(screen, red, (x - (screenWidth * 0.01), screenHeight * 0.93, screenWidth * 0.02, screenHeight * 0.07), 0)
            if displayName:
                drawTextCenter(song, font20, black, screenWidth/2, screenHeight * 0.92)
                displayName = False
        x = x + (widthRadio / len(songs) )

#function to reset the game
def resetGame():
    speed = initialSpeed
    score = 0
    coins = 0
    vehicle_group.empty() #remove all the entities from the group
    coin_group.empty()
    player_group.empty()
    player = PlayerVehicle(player_x, player_y, colour)
    player_group.add(player)
    return speed, score, coins, player

# function for detection (movement and virtual mouse)
def motionDetection(frame1, frame2, frame):
    #before the drawing of the rectangles we switch right with left because frame1 and 2 are not fliped like image_frame IN THE COORDONATES
    #compaire the two frames to see if there is a difference
    delta_frame = cv2.absdiff(frame1, frame2)
    #turn them to gray
    gray = cv2.cvtColor(delta_frame, cv2.COLOR_BGR2GRAY)

    #just blur the area of interest (inside the two rectangles)
    roi_grayR = gray[upperLeftL[1]:bottomRightL[1], upperLeftL[0]:bottomRightL[0]] #here
    roi_blurR = cv2.GaussianBlur(roi_grayR, (21, 21), 0)
    roi_grayL = gray[upperLeftR[1]:bottomRightR[1], upperLeftR[0]:bottomRightR[0]]
    roi_blurL = cv2.GaussianBlur(roi_grayL, (21, 21), 0)

    #make them binary
    _, threshold_frameR = cv2.threshold(roi_blurR, 50, 255, cv2.THRESH_BINARY)
    dilatedR = cv2.dilate(threshold_frameR, None, iterations=3)
    _, threshold_frameL = cv2.threshold(roi_blurL, 50, 255, cv2.THRESH_BINARY)
    dilatedL = cv2.dilate(threshold_frameL, None, iterations=3)

    #if there is any difference make the corresponding movement variable true
    movementR = dilatedR.any()
    movementL = dilatedL.any()

    #draw the rectangles (blue for no movement, red for movement)
    if not movementR:
        cv2.putText(frame, "Right", (upperLeftR[0] + 5, bottomRightR[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.rectangle(frame, upperLeftR, bottomRightR, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Right", (upperLeftR[0] + 5, bottomRightR[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.rectangle(frame, upperLeftR, bottomRightR, (255, 0, 0), 2)

    if not movementL:
        cv2.putText(frame, "Left", (upperLeftL[0] + 5, bottomRightL[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.rectangle(frame, upperLeftL, bottomRightL, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Left", (upperLeftL[0] + 5, bottomRightL[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.rectangle(frame, upperLeftL, bottomRightL, (255, 0, 0), 2)

    return movementL, movementR

def virtualMouse(frame):
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Hand detection
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks

    #for every hand that is showing
    if hands:
        for hand in hands:
            #draw the red dots on the hands
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark

            #loop trough the dots
            for id, landmark in enumerate(landmarks):
                #save the coordinates of the current dot
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)

                #if it is the dot 9 (base of middle finger)
                if id == 9:
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 0, 255))

                    #save the coordinates
                    palm_x = int(screen_width * x / frame_width)
                    palm_y = int(screen_height * y / frame_height)

                    #let the mouse move same as the coordinates of the dot 9
                    pyautogui.moveTo(palm_x, palm_y)

                #if it is the dot 12 (tip of middle finger)
                if id == 12:
                    middle_x = int(screen_width * x / frame_width)
                    middle_y = int(screen_height * y / frame_height)
                    #if abs(palm_y - middle_y) < 20: #or
                    #if the dot 12 is bellow the dot 9 (the person closed it fist)
                    if palm_y <= middle_y:
                        #click the mouse
                        pyautogui.click()
                        pyautogui.sleep(1)

# Function to sign in and up
def sign_up(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user, None  # Return user and no error
    except requests.exceptions.HTTPError as e:
        error_json = json.loads(e.args[1])
        error = error_json['error']['message']
        if error == 'EMAIL_EXISTS':
            return None, "Email address already used"
        elif error == 'INVALID_EMAIL':
            return None, "Invalid email format (emailaddress@something.com)"
        elif error == 'WEAK_PASSWORD : Password should be at least 6 characters':
            return None, "Choose a stronger password (min. 6 characters)"
        else:
            return None, str(e)
    
def sign_in(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user, None  # Return user and no error
    except requests.exceptions.HTTPError as e:
        error_json = json.loads(e.args[1])
        error = error_json['error']['message']
        if error == 'EMAIL_NOT_FOUND':
            return None, "No user record corresponding to this email"
        elif error == "INVALID_LOGIN_CREDENTIALS":
            return None, 'Incorrect email or password'
        elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error:
            return None, 'Too many incorrect attempts, try later (15 min.)'
        else:
            return None, str(e)
    
# Function to get the data for the logged-in user
    #structure in database:
    # uid : 
    #     -name: "text"
    #     -score:
    #            -high: "number"
    #            -last: "number"
    #     -coins: "number"
    #     -colour:
    #            -blue: "bool"
    #            -yellow: "bool"
    #            -green: "bool"
def getScore(uid, type):

    #structure:
    # uid :
    #     -score:
    #            -high:
    #            -last:

    # Reference to the Realtime Database node for storing numbers
    numbers_ref = db.reference(uid)

    # Get the number for the user
    user_data = numbers_ref.child('score').get() #let the user_data be the child of the score that beongs to uid
    if user_data:
        if type == 'high':
            return user_data.get('high')
        elif type == 'last':
            return user_data.get('last')
        else:
            return 0 #if there is no data
    else:
        return 0
    
def saveScore(uid, score):
    # Reference to the Realtime Database node for storing numbers
    score_ref = db.reference(uid)

    # Update always the 'last' field
    score_ref.child('score').update({'last': score})
    high_score = getScore(uid, 'high')
    if high_score != None:
        if score > high_score:
            # Update only if the new score is higher than the existing high score
            score_ref.child('score').update({'high': score})
    else:
        #if there is no prior high score update
        score_ref.child('score').update({'high': score})

def saveDisplayName(uid, displayName):
    # Reference to the Realtime Database node for storing numbers
    name_ref = db.reference(uid)
    name_ref.update({'name': displayName})

def getDisplayName(uid):
    name_ref = db.reference(uid)
    return name_ref.child('name').get()

def saveCoins(uid, coin):
    # Reference to the Realtime Database node for storing numbers
    coin_ref = db.reference(uid)
    coins = getCoins(uid)#get the saved number of coins for the user
    coins += coin #add the gained coins in this round
    coin_ref.update({'coins': coins}) #save the sum

def removeCoins(uid, coin):
    # Reference to the Realtime Database node for storing numbers
    coin_ref = db.reference(uid)
    coins = getCoins(uid)#get the saved number of coins for the user
    coins -= coin #remove the coins of the price of the colour
    coin_ref.update({'coins': coins}) #save the difference

def getCoins(uid):
    coin_ref = db.reference(uid)
    coins = coin_ref.child('coins').get()
    if coins == None:
        return 0
    else:
        return int(coins)
    
def saveColour(uid, colour):
    colour_ref = db.reference(uid)
    if colour == 'yellow':
        colour_ref.child('colour').update({'yellow': False})
    elif colour == 'blue':
        colour_ref.child('colour').update({'blue': False})
    elif colour == 'green':
        colour_ref.child('colour').update({'green': False})
    else:
        colour_ref.child('colour').update({'yellow': True})
        colour_ref.child('colour').update({'blue': True})
        colour_ref.child('colour').update({'green': True})

def getColour(uid, colour):
    colour_ref = db.reference(uid)
    colourCar = colour_ref.child('colour').get()
    if colourCar:
        if colour == 'yellow':
            return colourCar.get('yellow')
        elif colour == 'blue':
            return colourCar.get('blue')
        elif colour == 'green':
            return colourCar.get('green')
        else:
            return True
    else:
        return True

#####################################################################################################

##################################### CLASSES #######################################################

#class for objects
class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        # scale the image down so it's not wider than the lane
        image_scale = (screenWidth * 0.09) / image.get_rect().width #45
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (int(new_width), int(new_height)))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):

    #inherite from classe Vehicule
    def __init__(self, x, y, colour):
        image = pygame.image.load(f'resources//images/car_' +  colour + '.png')
        super().__init__(image, x, y)

class Coins(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        #pygame.sprite.Sprite().__init__(self)
        super().__init__()
        self.images = []
        #create animation : list of still pictures 
        for num in range(1, 5):
            img = pygame.image.load(f"resources/images/coins/coin{num}.png")
            #add loaded img to list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0 #to control speed animation
        self.speed = speed

    def update(self):
        global coins
        animation_speed = 3
        #update coin animation
        self.counter += 1
        if self.counter >= animation_speed and self.index < len(self.images) - 1: #so it doesn't exceed the list of images 
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #if the animation complete delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= animation_speed:
            self.counter = 0
            self.index = 0
        
        if pygame.sprite.spritecollide(self, player_group, False):
            coins += 1
            self.kill()

        self.rect.y += self.speed
        if self.rect.top > screenHeight:
            self.kill()

#####################################################################################################

##################################### SPRITES #######################################################

# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

#####################################################################################################

##################################### LOGIN LOOP ####################################################

while login_menu:

    for event in pygame.event.get():
        #press the x button of the window to exit the program
        if event.type == pygame.QUIT:
            login_menu = False 
            running = False

        #event if mouse clicked
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #check if collision between certain box and mouse position
            if sign_up_box.collidepoint(event.pos):
                signUp = True
                signIn = False
            if sign_in_box.collidepoint(event.pos):
                signUp = False
                signIn = True
            if email_box.collidepoint(event.pos):
                activeEmail = True
            else:
                activeEmail = False
            if password_box.collidepoint(event.pos):
                activePassword = True
            else:
                activePassword = False
            if signUp:
                if display_name_box.collidepoint(event.pos):
                    activeDisplayName = True
                else:
                    activeDisplayName = False

        #check event for resize window
        elif event.type == pygame.VIDEORESIZE:
            oldWidth, oldHeight = screenWidth, screenHeight
            # Get the new dimensions of the window
            screenWidth, screenHeight = event.size

            #if the width or height smaller than initial return to initial
            if screenWidth <= minScreenWidth:
                screenWidth = minScreenWidth
            if screenHeight <= minScreenHeight:
                screenHeight = minScreenHeight

            xRatio = screenWidth / oldWidth
            yRatio = screenHeight / oldHeight

            # Scale the background image to fit the new window size without interpolation
            # do not use the original so we can keep the quality of the image when resizing from smaller to bigger
            scaled_bg = pygame.transform.scale(bg, (screenWidth, screenHeight))

            #resize everything on the screen
            for button in buttonsLogin:
                resizeButton(button, xRatio, yRatio)

            for rect in rectLogin:
                resizeRect(rect, xRatio, yRatio)

            white_trans_rect = pygame.Surface((screenWidth * 0.6, screenHeight * 0.8))
            white_trans_rect.set_alpha(150)
            white_trans_rect.fill(white)
            
            # Set the new size of the window
            screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)

        #check event of keyboard use
        elif event.type == pygame.KEYDOWN:
            #check which box is active
            if activeEmail and not activePassword and not activeDisplayName:
                #if return is pressed make the active box not active
                if event.key == pygame.K_RETURN:
                    activeEmail = False
                #if backspace remove last letter from designed text
                elif event.key == pygame.K_BACKSPACE:
                    email = email[:-1]
                #else add the the character pressed to text
                else:
                    email += event.unicode
            if activePassword and not activeEmail and not activeDisplayName:
                if event.key == pygame.K_RETURN:
                    activePassword = False
                    if signUp:
                        activeDisplayName = True
                elif event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                else:
                    password += event.unicode
            if activeDisplayName and not activeEmail and not activePassword:
                if event.key == pygame.K_RETURN:
                    activeDisplayName = False
                elif event.key == pygame.K_BACKSPACE:
                    displayName = displayName[:-1]
                else:
                    if len(displayName) < 15:
                        displayName += event.unicode

    # Draw background
    screen.fill(white)
    screen.blit(scaled_bg, (0,0))

    screen.blit(white_trans_rect, (screenWidth * 0.2, screenHeight * 0.1)) #(100,50)) 

    #draw buttons while checking collision that is done inside button class
    if x_button.draw(screen):
        login_menu = False
        running = False

    if clear_button.draw(screen):
        password = ''
        email = ''
        displayName = ''
        cutEmail = ''
        cutMPassword = ''
        cutPassword = ''
        errorDisplay = ''

    # Draw input fields
    pygame.draw.rect(screen, white, email_box, 0)
    pygame.draw.rect(screen, white, password_box, 0)

    #draw line to separate sign in from up
    #pygame.draw.line(surface, color, start_pos, end_pos, width)
    pygame.draw.line(screen, lightgrey, [screenWidth * 0.37, screenHeight * 0.1], [screenWidth * 0.37, screenHeight * 0.18], 2) #[185, 50], [185, 90], 2)

    # Draw text
    drawText("EMAIL", font30, black, email_box.x , email_box.y - (screenHeight * 0.08))
    drawText("PASSWORD", font30, black, password_box.x , password_box.y - (screenHeight * 0.08))

    #draw error message if there is one
    if errorDisplay != None:
        drawTextCenter(str(errorDisplay), font20, red, screenWidth * 0.5, screenHeight * 0.95) #250, 475)

    # Render and display the current text
    #email
    if activeEmail:
        if font20.size(email)[0] < email_box.w :
            drawText(email, font20, black, email_box.x + (screenWidth * 0.01), email_box.y + (screenHeight * 0.012))
            cutEmail = email
        #if width of email is longer than the one of the box
        else:
            while font20.size(cutEmail + "...")[0] > email_box.w - 7:
                cutEmail = cutEmail[:-1]  # Remove one character at a time until it fits
            drawText(cutEmail + "...", font20, black, email_box.x + (screenWidth * 0.01), email_box.y + (screenHeight * 0.012))
        #draw a dark outline around the selected box
        pygame.draw.rect(screen, grey, (email_box.x, email_box.y, email_box.w, email_box.h), 2)
    elif not activeEmail:
        #if not active make the text inside a lighter colour
        if cutEmail == email:
            drawText(email, font20, grey, email_box.x + (screenWidth * 0.01), email_box.y + (screenHeight * 0.01))
        else:
            drawText(cutEmail + '...', font20, grey, email_box.x + (screenWidth * 0.01), email_box.y + (screenHeight * 0.01))

    #password
    if activePassword:
        if font20.size(password)[0] < password_box.w :
            drawText(password, font20, black, password_box.x + (screenWidth * 0.01), password_box.y + (screenHeight * 0.012))
            cutPassword = password
        else:
            while font20.size(cutPassword + "...")[0] > password_box.w - 7:
                cutPassword = cutPassword[:-1]  # Remove one character at a time until it fits
            drawText(cutPassword + "...", font20, black, password_box.x + (screenWidth * 0.01), password_box.y + (screenHeight * 0.012))
        pygame.draw.rect(screen, grey, (password_box.x, password_box.y, password_box.w, password_box.h), 2)
    elif not activePassword:
        #hide the password when not selected
        maskedPassword = '•' * len(password)
        if font20.size(maskedPassword)[0] < password_box.w :
            drawText(maskedPassword, font20, grey, password_box.x + (screenWidth * 0.01), password_box.y + (screenHeight * 0.01))
        else:
            cutMPassword = maskedPassword
            while font20.size(cutMPassword + "...")[0] > password_box.w - 7:
                cutMPassword = cutMPassword[:-1]
            drawText(cutMPassword + '...', font20, grey, password_box.x + (screenWidth * 0.01), password_box.y + (screenHeight * 0.01))

    #if the sign up is selected display the following page
    if signUp:
        drawText("SIGN UP", font20, black, sign_up_box.x , sign_up_box.y + (screenHeight * 0.02))
        drawText("SIGN IN", font20, grey, sign_in_box.x , sign_in_box.y + (screenHeight * 0.02))
        #draw all the things that are in sign up but not in sign in
        #because all the common things have been drawn before
        drawText("NAME", font30, black, display_name_box.x, display_name_box.y - (screenHeight * 0.08))
        drawText("emailaddress@something.com", font10, black, email_box.x  , email_box.y + (screenHeight * 0.08))
        drawText("minimum 6 characters", font10, black, password_box.x , password_box.y + (screenHeight * 0.08))
        drawText("maximum 15 characters", font10, black, display_name_box.x , display_name_box.y + (screenHeight * 0.08))
        pygame.draw.rect(screen, white, display_name_box, 0)
        if activeDisplayName:
            drawText(displayName, font20, black, display_name_box.x + (screenWidth * 0.01), display_name_box.y + (screenHeight * 0.012))
            pygame.draw.rect(screen, grey, (display_name_box.x, display_name_box.y, display_name_box.w, display_name_box.h), 2)
        elif not activeDisplayName:
            drawText(displayName, font20, grey, display_name_box.x + (screenWidth * 0.01), display_name_box.y + (screenHeight * 0.01))
        #if sign up button is pressed
        if sign_up_button.draw(screen) and signUp:
            user, errorDisplay = sign_up(email, password)
            #check if there is no error message and that the used id is successfully retreived
            if errorDisplay == None:
                uid = user["localId"]
                saveDisplayName(uid, displayName)
                saveColour(uid, 'red')
                name = getDisplayName(uid)
                displayCoin = getCoins(uid)
                email = ''
                password = ''
                displayName = ''
                if uid != None:
                    if screenHeight != minScreenHeight or screenWidth != minScreenWidth:
                        screenWidth = minScreenWidth
                        screenHeight = minScreenHeight
                        scaled_bg = pygame.transform.scale(bg, (screenWidth, screenHeight))
                        screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
                    login_menu = False #exist this loop and enter the game loop after getting all the needed user info
                    start_menu = True
                    running = True
                    break
        
    #if the sign in is selected display the following page
    if signIn:
        drawText("SIGN UP", font20, grey, sign_up_box.x , sign_up_box.y + (screenHeight * 0.02))
        drawText("SIGN IN", font20, black, sign_in_box.x , sign_in_box.y + (screenHeight * 0.02))
        if sign_in_button.draw(screen):
            user, errorDisplay = sign_in(email, password)
            if errorDisplay == None:
                uid = user["localId"]
                email = ''
                password = ''
                displayName = '' 
                if uid != None:
                    if screenHeight != minScreenHeight or screenWidth != minScreenWidth:
                        screenWidth = minScreenWidth
                        screenHeight = minScreenHeight
                        scaled_bg = pygame.transform.scale(bg, (screenWidth, screenHeight))
                        screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
                    name = getDisplayName(uid)
                    displayCoin = getCoins(uid)
                    login_menu = False
                    start_menu = True
                    running = True

    pygame.display.update() #to update the display if changes happens to elements on the screen each loop

#####################################################################################################

##################################### GAME LOOP #####################################################

# game loop
while running:

    song = loadedSongs[choiceSong]

    _, image_frame = video.read()
    flip_image_frame = cv2.flip(image_frame, 1)

    #we put this here so where ever the player was they can quit with the X
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #evenet for resize window
        elif event.type == pygame.VIDEORESIZE:
            oldWidth, oldHeight = screenWidth, screenHeight
            # Get the new dimensions of the window
            screenWidth, screenHeight = event.size

            #if the width or height smaller than initial return to initial
            if screenWidth <= minScreenWidth:
                screenWidth = minScreenWidth
            if screenHeight <= minScreenHeight:
                screenHeight = minScreenHeight

            #make the width and height same value
            if screenWidth != oldWidth:
                screenHeight = screenWidth
            elif screenHeight !=  oldHeight:
                screenWidth = screenHeight

            xRatio = screenWidth / oldWidth
            yRatio = screenHeight / oldHeight

            # Scale the background image to fit the new window size without interpolation
            # do not use the original so we can keep the quality of the image when resizing from smaller to bigger
            scaled_bg = pygame.transform.scale(bg, (screenWidth, screenHeight))
            scaled_bg_car_view = pygame.transform.scale(bg_car_view, (screenWidth, screenHeight))

            #resize everything when window is resized
            for button in buttonsGame:
                resizeButton(button, xRatio, yRatio)

            for rect in rectGame:
                resizeRect(rect, xRatio, yRatio)

            red_car_img = resizeImage(red_car_img, xRatio, yRatio)
            blue_car_img = resizeImage(blue_car_img, xRatio, yRatio)
            yellow_car_img = resizeImage(yellow_car_img, xRatio, yRatio)
            green_car_img = resizeImage(green_car_img, xRatio, yRatio)
            block_img = resizeImage(block_img, xRatio, yRatio)

            road_width = screenWidth * 0.6
            marker_width = screenWidth * 0.016
            marker_height = screenHeight * 0.08

            left_lane = screenWidth * 0.3
            center_lane = screenWidth * 0.5
            right_lane = screenWidth * 0.7
            lanes = [left_lane, center_lane, right_lane]

            road = (screenWidth * 0.2, 0, road_width, screenHeight)
            left_edge_marker = (screenWidth * 0.19, 0, marker_width, screenHeight)
            right_edge_marker = (screenWidth * 0.79, 0, marker_width, screenHeight)

            player_x = screenWidth * 0.5 
            player_y = screenHeight * 0.8 

            # Set the new size of the window
            screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)

        #check for collision if the theme menu is displayed
        if theme_menu:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if redRect.collidepoint(event.pos):
                    colour = 'red'
                if blueRect.collidepoint(event.pos):
                    #if the colour is locked and user have enough coins unlock the car and select it
                    if lockBlue and displayCoin > 5:
                        lockBlue = True
                        colour = 'blue'
                        saveColour(uid, 'blue')
                        removeCoins(uid, 5)
                        if sound:
                            spending_money_sound.play(0)
                    #if it is unlocked just select it
                    elif not lockBlue:
                        colour = 'blue'
                if yellowRect.collidepoint(event.pos):
                    if lockYellow and displayCoin > 10:
                        lockYellow = True
                        colour = 'yellow'
                        saveColour(uid, 'yellow')
                        removeCoins(uid, 10)
                        if sound:
                            spending_money_sound.play(0)
                    elif not lockYellow:
                        colour = 'yellow'
                if greenRect.collidepoint(event.pos):
                    if lockGreen and displayCoin > 15:
                        lockGreen = True
                        colour = 'green'
                        saveColour(uid, 'green')
                        removeCoins(uid, 15)
                        if sound:
                            spending_money_sound.play(0)
                    elif not lockGreen:
                        colour = 'green'
        
    #start menu
    if start_menu:

        #use the virtual mouse
        virtualMouse(flip_image_frame)
        # show the fliped image so it is in the right direction
        cv2.imshow("Movement Detection", flip_image_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #display background
        #background should be drawn first then everything on top because if we draw button then bg the buttons will not appear, they will be behind
        screen.fill(green)  
        screen.blit(scaled_bg, (0,0))
        # display the title
        drawTextCenter(gameName, font40, black, screenWidth/2, screenHeight * 0.12)

        song.stop()

        #display the buttons
        if start_button.draw(screen):
            # create the player's car if there is not a player already
            if not player_group:
                player = PlayerVehicle(player_x, player_y, colour)
                player_group.add(player)
            #exit the menu and enter the game
            start_menu = False
            game = True
        if exit_button.draw(screen):
            #exit the program
            running = False
        if setting_button.draw(screen):
            #exit the start menu and enter the settings menu
            start_menu = False
            setting_menu = True

    #settings menu
    if setting_menu and not start_menu:

        #the virtual mouse can be used just in the part of the loop that this function is called in
        virtualMouse(flip_image_frame)
        cv2.imshow("Movement Detection", flip_image_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #display background
        screen.fill(green)  
        screen.blit(scaled_bg, (0,0))
        screen.blit(scaled_bg_car_view, (0,screenHeight * 0.06))
        #display the scores and email of the player
        lastScore = getScore(uid, 'last')
        highScore = getScore(uid, 'high')
        displayCoin = getCoins(uid)
        drawTextCenter(name, font30, black, screenWidth * 0.496, screenHeight * 0.12)
        drawTextCenter('Latest Score: ' + str(lastScore), font20, black, screenWidth * 0.496, screenHeight * 0.2)
        drawTextCenter('Highest Score: ' + str(highScore), font20, black, screenWidth * 0.496, screenHeight * 0.26)
        drawTextCenter('Coins: ' + str(displayCoin), font20, black, screenWidth * 0.496, screenHeight * 0.32)

        if next_button.draw(screen):
            if choiceSong == len(songs) - 1:
                choiceSong = 0
            else:
                choiceSong += 1
        if previous_button.draw(screen):
            if choiceSong == 0:
                choiceSong = len(songs) - 1
            else:
                choiceSong -= 1
        drawRadio(choiceSong)

        #if the sound is True display the button mute so when clicked it will make the sound False
        #if the sound is false display the button unmute when clicked it will make the sound true
        if sound: 
            if sound_button.draw(screen):
                sound = False
        else:
            if not_sound_button.draw(screen):
                sound = True
        
        #display return button and tutorial button and theme button
        if return_back_button.draw(screen):
            start_menu = True
            setting_menu = False
        if gameplay_button.draw(screen):
            gameplay_menu = True
            setting_menu = False
        if theme_button.draw(screen):
            theme_menu = True
            setting_menu = False

    if gameplay_menu:

        virtualMouse(flip_image_frame)
        cv2.imshow("Movement Detection", flip_image_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        drawGameplay()
        if return_back_button.draw(screen):
            setting_menu = True
            gameplay_menu = False

    if theme_menu:
        virtualMouse(flip_image_frame)
        cv2.imshow("Movement Detection", flip_image_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #get which colour is locked from the user to know which can be selected
        lockBlue = getColour(uid, 'blue')
        lockGreen =getColour(uid, 'green')
        lockYellow =getColour(uid, 'yellow')

        displayCoin = getCoins(uid)
        drawColourCar(displayCoin, lockYellow, lockBlue, lockGreen, colour)

        if return_back_button.draw(screen):
            setting_menu = True
            theme_menu = False

    #main game
    if game:
        
        clock.tick(fps) #let the game be diplayed 30 frame per second

        #the part where the player is moving the car before crashing
        if not gameover:

            #get the movements
            movementL, movementR = motionDetection(frame1, frame2, flip_image_frame)
            cv2.imshow("Movement Detection", flip_image_frame)
            
            #update the frames
            frame1 = frame2
            check, frame2 = video.read()
            #if there is already a song playing it does not start another one
            if sound and not pygame.mixer.get_busy():
                song.play()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                #see if a key on the keyboard is pressed so if the player does not want to use cam, the keyboard can be used
                if event.type == KEYDOWN:
                    #if the arrow left key is pressed check if the car is not on the last left lane to move
                    if event.key == K_LEFT and player.rect.center[0] > left_lane:
                        player.rect.x = player.rect.x - (screenWidth * 0.2)
                        left = True
                        right = False
                    #if the arrow right key is pressed check if the car is not on the last right lane to move
                    elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                        player.rect.x = player.rect.x + (screenWidth * 0.2)
                        right = True
                        left = False
                        #player movement based of lanes positions instead of just removingcor adding a value to player position
                        # if player.rect.center[0] < center_lane:
                        #     player.rect.x = center_lane - player.rect.width / 2
                        # elif player.rect.center[0] < right_lane:
                        #     player.rect.x = right_lane - player.rect.width / 2

            #check for movemennt based of cam
            if (movementR or movementL) and time.time() - last_movement_time >= 0.5:
                #add the last movement so that the sensitivity is low
                # so that if two unintendent consecutive movements are made it does not consider the second
                last_movement_time = time.time()  # Update the last movement time
                if movementR and not movementL and player.rect.center[0] < lanes[2]:
                    player.rect.x = player.rect.x + (screenWidth * 0.2)
                    right = True
                    left = False
                elif not movementR and movementL and player.rect.center[0] > lanes[0]:
                    player.rect.x = player.rect.x - (screenWidth * 0.2)
                    left = True
                    right = False

            #coin update so it move
            coin_group.update()

            #update the position of the lane_marker so they move
            lane_marker_move_y += speed * (screenHeight * 0.004) #2
            if lane_marker_move_y >= marker_height * 2:
                lane_marker_move_y = 0

            # add a vehicle and coins
            #if there is less than 2 vehicules on the screen
            if len(vehicle_group) < 2:
                add_vehicle = True
                for vehicle in vehicle_group:
                    if vehicle.rect.top < vehicle.rect.height * 1.5:
                        add_vehicle = False

                if add_vehicle:
                    lane = random.choice(lanes)
                    image = random.choice(vehicle_images)
                    vehicle = Vehicle(image, lane, screenHeight / -2)
                    vehicle_group.add(vehicle)
                    coin = Coins(random.choice(lanes), (screenHeight / -2) - (screenHeight * 0.4), speed)
                    coin_group.add(coin)

            # make the vehicles move by increasing the y of the vehicule depending the speed
            for vehicle in vehicle_group:
                vehicle.rect.y += speed

                #when the vehicules exit the screen kill the entity to free up space and increase the score and speed
                if vehicle.rect.top >= screenHeight:
                    vehicle.kill()
                    score += 1

                    if score > 0 and score % 5 == 0:
                        speed += 1

        #those are the elements that should be displayed in the game and while gameover
        #check for collision between the vehicules and player
        for vehicle in vehicle_group:
            if pygame.sprite.spritecollide(player, vehicle_group, False):
            #pygame.sprite.GroupSingle(vehicle)
                if not gameover:
                    # Check if the collision is from the right
                    if right and not left:
                        player.rect.right = vehicle.rect.left
                        crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    # Check if the collision is from the left
                    elif left and not right:
                        player.rect.left = vehicle.rect.right
                        crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    else:
                        crash_rect.center = [player.rect.center[0], player.rect.top]

                    if sound:
                        song.stop()
                        crash_sound.play(0) # 0 so the sound does not repeat and -1 for endless loop
                    
                    saveCoins(uid, coins)
                    displayCoin = getCoins(uid)
                    gameover = True #if there is collision go to gameover screen

        #display the background of the road
        drawBackground(lane_marker_move_y)

        # draw the player's car
        player_group.draw(screen)

        # draw the vehicles
        vehicle_group.draw(screen)

        coin_group.draw(screen)

        # display the score
        drawTextCenter('Score: ' + str(score), font20, white, screenWidth * 0.1, screenHeight * 0.8) #50, 400)
        drawTextCenter('Coins: ' + str(coins), font20, white, screenWidth * 0.1, screenHeight * 0.86) #50, 430)

        #remake right and left false so if the player  did not move and collided with anothe vehicle it will be at the bottom
        right = False
        left = False

    #game over screen
    #elements that should be added when game over
    if gameover:

        virtualMouse(flip_image_frame)
        cv2.imshow("Movement Detection", flip_image_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, (200, 0, 0), (0, screenHeight * 0.1, screenWidth, screenHeight * 0.2))

        drawTextCenter('Game over', font20, white, screenWidth / 2, screenHeight * 0.18)
        drawTextCenter('Play again?', font20, white, (screenWidth / 2), screenHeight * 0.22)
        saveScore(uid, score)

        song.stop()

        if reload_button.draw(screen):
            gameover = False
            speed, score, coins, player = resetGame()
            game = True

        if return_button.draw(screen):
            gameover = False
            start_menu = True
            game = False
            speed, score, coins, player = resetGame()
            player_group.empty()

    pygame.display.update()

#####################################################################################################

##################################### QUIT ##########################################################

video.release()
cv2.destroyAllWindows()
pygame.quit()

#####################################################################################################

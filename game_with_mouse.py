import pygame
from pygame.locals import *
from pygame import mixer
import cv2
import mediapipe as mp
import pyautogui
import random
import time
import button
import os
import firebase_admin
from firebase_admin import credentials, db
import pyrebase
import json
import requests

# Set the position of the Pygame window
os.environ['SDL_VIDEO_WINDOW_POS'] = "800,150"

pygame.init()

#firebase settings
config = {
    "apiKey": "",
    "authDomain": ",
    "databaseURL": "",
    "storageBucket": ""
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("resources/credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL" : ""})

# frame settings
clock = pygame.time.Clock()
fps = 30
gameName = 'Dynamic Dodge'

# mouser settings
# Hand detector
hand_detector = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils
# Get screen size
screen_width, screen_height = pyautogui.size()
# Initialize variables
palm_x = 0
palm_y = 0

# create the window
width = 500
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption(gameName)

# Set up a variable to track the last time movement was detected
#we are putting a delay so that the car does not directly jump 2 lanes at a time if there was a lot of unintentional movement
last_movement_time = time.time()

#font initialization
font40 = pygame.font.Font('resources/images/VarelaRound-Regular.ttf', 40)
font30 = pygame.font.Font('resources/images/VarelaRound-Regular.ttf', 30)
font20 = pygame.font.Font('resources/images/VarelaRound-Regular.ttf', 20)
font10 = pygame.font.Font('resources/images/VarelaRound-Regular.ttf', 10)

# webcam settings
video = cv2.VideoCapture(0)  # 0 channel for the webcam
check, frame1 = video.read()
check, frame2 = video.read()

upperLeftL = (50, 50)
bottomRightL = (200, 300)

upperLeftR = (450, 50)
bottomRightR = (600, 300)

movementR = False
movementL = False

#colour initialization
black = (10, 10, 10)
white = (255, 255, 255)
green = (76, 208, 56)
grey = (100, 100, 100)
lightgrey = (150, 150, 150)
yellow = (255, 232, 0)
red = (200, 20, 20)

# road and marker sizes
road_width = 300
marker_width = 8
marker_height = 40

# lane coordinates
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# road and edge markers for the rectangles
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# Input fields coordinates for login page
email_box = pygame.Rect(125, 150, 250, 40)
password_box = pygame.Rect(125, 250, 250, 40)
display_name_box = pygame.Rect(125, 350, 250, 40)
sign_in_box = pygame.Rect(105, 50, 80, 40)
sign_up_box = pygame.Rect(190, 50, 80, 40)

white_trans_rect = pygame.Surface((300,400))  # the size of your rect
white_trans_rect.set_alpha(150) # lower number more transparent
white_trans_rect.fill(white) # this fills the entire surface

# for animating movement of the lane markers
lane_marker_move_y = 0

# game settings and variables
initialSpeed = 8
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
gameover = False #when the player looses the round but did not yet return to the menu or played another round 
right = False
left = False

#for login
email = ''
cutEmail = ''
password = ''
displayName = ''
cutPassword = ''
uid = None
name = None
errorDisplay = None
activeEmail = False
activePassword = False
activeDisplayName = False
signUp = False
signIn = True

# player's initial coordinates
player_x = 250
player_y = 400

#list of songs on the radio
songs = ['drive', 'chase', 'In Dreams', 'Better Day', 'Powerful Trap', 'Titanium']
loadedSongs = []
choiceSong = 0

#load image
#we use convert_alpha() instead of convert() because it supports transparent backgrounds
bg = pygame.image.load("resources/images/road_background.png")
bg_car_view = pygame.image.load("resources/images/bg_car_view.png")
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

#load the crash image
crash = pygame.image.load('resources/images/crash.png')
crash_rect = crash.get_rect() #when crash let the center of the image be the coordinates

#load the vehicle images
#we put them in a list so we can later choose randomely one
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('resources/images/' + image_filename)
    vehicle_images.append(image)

#load sounds
crash_sound = pygame.mixer.Sound("resources/sounds/crash_sound.wav")
crash_sound.set_volume(0.50)

for song in songs:
    song_sound = pygame.mixer.Sound("resources/sounds/" + song +".wav")
    song_sound.set_volume(0.30)
    loadedSongs.append(song_sound)

# Initialize the buttons
start_button = button.Button((width / 2)  - 60, (height / 2)+ 20, start_img) #width, height, object(or image)
exit_button = button.Button((width / 2)  - 60, (height / 2) + 70, exit_img)
setting_button = button.Button((width / 2) - 60, (height / 2) + 120, setting_img)
reload_button = button.Button((width / 2) -110, 130, reload_img)
return_button = button.Button((width / 2) + 70, 130, return_img)
sound_button = button.Button((width / 2)  - 60, (height / 2)+ 5, sound_img)
not_sound_button = button.Button((width / 2)  - 60, (height / 2)+ 5, not_sound_img)
return_back_button = button.Button((width / 2) - 60, (height / 2) + 105, return_back_img)
gameplay_button = button.Button((width / 2)  - 60, (height / 2) + 55, gameplay_img)
next_button = button.Button(width - 60, height - 50, next_img)
previous_button = button.Button(20, height - 50, previous_img)
sign_up_button = button.Button(190, 400, sign_up_img) #width, height, object(or image) #old coordinates (190, 320)
sign_in_button = button.Button(190, 400, sign_in_img)

#function to draw text using the center
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
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

#function to reset the game
def resetGame():
    speed = initialSpeed
    score = 0
    coins = 0
    vehicle_group.empty()
    coin_group.empty()
    player.rect.center = [player_x, player_y]
    return speed, score, coins

def motionDetection(frame1, frame2, frame):
    #before the drawing of the rectangles we switch right with left because frame1 and 2 are not fliped like image_frame IN THE COORDONATES
    delta_frame = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(delta_frame, cv2.COLOR_BGR2GRAY)

    roi_grayR = gray[upperLeftL[1]:bottomRightL[1], upperLeftL[0]:bottomRightL[0]] #here
    roi_blurR = cv2.GaussianBlur(roi_grayR, (21, 21), 0)

    roi_grayL = gray[upperLeftR[1]:bottomRightR[1], upperLeftR[0]:bottomRightR[0]]
    roi_blurL = cv2.GaussianBlur(roi_grayL, (21, 21), 0)

    _, threshold_frameR = cv2.threshold(roi_blurR, 50, 255, cv2.THRESH_BINARY)
    dilatedR = cv2.dilate(threshold_frameR, None, iterations=3)

    _, threshold_frameL = cv2.threshold(roi_blurL, 50, 255, cv2.THRESH_BINARY)
    dilatedL = cv2.dilate(threshold_frameL, None, iterations=3)

    movementR = dilatedR.any()
    movementL = dilatedL.any()

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
                    #save the coordinates
                    palm_x = int(screen_width * x / frame_width)
                    palm_y = int(screen_height * y / frame_height)
                    #let the mouse move same as the coordinates of the dot 9
                    pyautogui.moveTo(palm_x, palm_y)

                #if it is the dot 12 (tip of middle finger)
                if id == 12:
                    middle_x = int(screen_width * x / frame_width)
                    middle_y = int(screen_height * y / frame_height)
                    #print('distance', abs(palm_y - middle_y))
                    #if abs(palm_y - middle_y) < 20: #or
                    #if the dot 12 is bellow the dot 9 (the person closed it fist)
                    if palm_y <= middle_y:
                        #click the mouse
                        pyautogui.click()
                        pyautogui.sleep(1)

def drawGameplay():
    screen.fill(green)
    screen.blit(bg, (0,0))
    drawTextCenter('1.Move the car left or right:', font20, black, 205, 120)
    drawTextCenter('by moving inside the rectangles', font20, black, 225, 160)
    drawTextCenter('or using the arrows on the keyboard', font20, black, 245, 190)
    drawTextCenter('2.Dodge other cars to avoid crashing', font20, black, 250, 250)
    drawTextCenter('3.Have fun!', font20, black, 128, 310)

def drawRadio(choiceSong):
    pygame.draw.rect(screen, black, (0,height-10,width,10), 0)
    displayName = False
    widthRadio = width - 100
    x = 80
    for song in songs:
        pygame.draw.rect(screen, black, (x - 5, height - 25, 10, 25), 0)
        if songs[choiceSong] == song:
            displayName = True
            pygame.draw.rect(screen, red, (x - 5, height - 35, 10, 35), 0)
            if displayName:
                drawTextCenter(song, font20, black, width/2, height - 40)
                # Introduce a delay of 1000 milliseconds (1 second)
                #pygame.time.delay(1000)
                displayName = False
        x = x + widthRadio / len(songs)

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
            return None, 'Too many incorrect attempts, try later'
        else:
            return None, str(e)
    
# Function to get the number for the logged-in user
def getScore(uid, type):
    # Reference to the Realtime Database node for storing numbers
    numbers_ref = db.reference(uid)

    # Get the number for the user
    user_data = numbers_ref.child('score').get()
    if user_data:
        if type == 'high':
            return user_data.get('high')
        elif type == 'last':
            return user_data.get('last')
        else:
            return 0
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
    coins = getCoins(uid)
    coins += coin
    coin_ref.update({'coins': coins})

def getCoins(uid):
    coin_ref = db.reference(uid)
    coins = coin_ref.child('coins').get()
    if coins == None:
        return 0
    else:
        return int(coins)

class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        # scale the image down so it's not wider than the lane
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (int(new_width), int(new_height)))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    
    def __init__(self, x, y):
        image = pygame.image.load('resources//images/car.png')
        super().__init__(image, x, y)

class Coins(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        #pygame.sprite.Sprite().__init__(self)
        super().__init__()
        self.images = []
        #create animation : list of still pictures 
        for num in range(1, 5):
            img = pygame.image.load(f"resources/images/coins/coin{num}.png")
            #add img to list
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
        if self.rect.top > height:
            self.kill()

# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)


cv2.namedWindow("Movement Detection")
# Move the windows to specific positions on the screen
cv2.moveWindow("Movement Detection", 80, 130)

while login_menu:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            login_menu = False
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
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

        elif event.type == pygame.KEYDOWN:
            if activeEmail and not activePassword and not activeDisplayName:
                if event.key == pygame.K_RETURN:
                    activeEmail = False
                elif event.key == pygame.K_BACKSPACE:
                    email = email[:-1]
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
    screen.blit(bg, (0,0))

    screen.blit(white_trans_rect, (100,50)) 

    # Draw input fields
    pygame.draw.rect(screen, white, email_box, 0)
    pygame.draw.rect(screen, white, password_box, 0)

    #draw line to separate sign in from up
    #pygame.draw.line(surface, color, start_pos, end_pos, width)
    pygame.draw.line(screen, lightgrey, [185, 50], [185, 90], 2)

    # Draw text
    drawText("EMAIL", font30, black, email_box.x , email_box.y - 40)
    drawText("PASSWORD", font30, black, password_box.x , password_box.y - 40)

    if errorDisplay != None:
        drawTextCenter(str(errorDisplay), font20, red, 250, 475)
        #print(errorDisplay)

    # Render and display the current text
    if activeEmail:
        if font20.size(email)[0] < email_box.w :
            drawText(email, font20, black, email_box.x+5, email_box.y+6)
            cutEmail = email
        else:
            while font20.size(cutEmail + "...")[0] > email_box.w - 7:
                cutEmail = cutEmail[:-1]  # Remove one character at a time until it fits
            drawText(cutEmail + "...", font20, black, email_box.x+5, email_box.y+6)
        pygame.draw.rect(screen, grey, (email_box.x, email_box.y, email_box.w, email_box.h), 2)
    elif not activeEmail:
        if cutEmail == email:
            drawText(email, font20, grey, email_box.x+5, email_box.y+5)
        else:
            drawText(cutEmail + '...', font20, grey, email_box.x+5, email_box.y+5)

    if activePassword:
        if font20.size(password)[0] < password_box.w :
            drawText(password, font20, black, password_box.x+5, password_box.y+6)
            cutPassword = password
        else:
            while font20.size(cutPassword + "...")[0] > password_box.w - 7:
                cutPassword = cutPassword[:-1]  # Remove one character at a time until it fits
            drawText(cutPassword + "...", font20, black, password_box.x+5, password_box.y+6)
        pygame.draw.rect(screen, grey, (password_box.x, password_box.y, password_box.w, password_box.h), 2)
    elif not activePassword:
        maskedPassword = '•' * len(password)
        if font20.size(maskedPassword)[0] < password_box.w :
            drawText(maskedPassword, font20, grey, password_box.x+5, password_box.y+5)
        else:
            cutMPassword = maskedPassword
            while font20.size(cutMPassword + "...")[0] > password_box.w - 7:
                cutMPassword = cutMPassword[:-1]
            drawText(cutMPassword + '...', font20, grey, password_box.x+5, password_box.y+5)


    if signUp:
        drawText("SIGN UP", font20, black, sign_up_box.x , sign_up_box.y + 10)
        drawText("SIGN IN", font20, grey, sign_in_box.x , sign_in_box.y + 10)
        drawText("NAME", font30, black, display_name_box.x, display_name_box.y - 40)
        drawText("emailaddress@something.com", font10, black, email_box.x  , email_box.y + 40)
        drawText("minimum 6 characters", font10, black, password_box.x , password_box.y + 40)
        drawText("maximum 15 characters", font10, black, display_name_box.x , display_name_box.y + 40)
        pygame.draw.rect(screen, white, display_name_box, 0)
        if activeDisplayName:
            drawText(displayName, font20, black, display_name_box.x+5, display_name_box.y+6)
            pygame.draw.rect(screen, grey, (display_name_box.x, display_name_box.y, display_name_box.w, display_name_box.h), 2)
        elif not activeDisplayName:
            drawText(displayName, font20, grey, display_name_box.x+5, display_name_box.y+5)
        if sign_up_button.draw(screen) and signUp:
            user, errorDisplay = sign_up(email, password)
            if errorDisplay == None:
                uid = user["localId"]
                saveDisplayName(uid, displayName)
                name = getDisplayName(uid)
                displayCoin = getCoins(uid)
                email = ''
                password = ''
                displayName = ''
                if uid != None:
                    login_menu = False
                    start_menu = True
                    running = True
                    break
                    #game = True
        
    if signIn:
        drawText("SIGN UP", font20, grey, sign_up_box.x , sign_up_box.y + 10)
        drawText("SIGN IN", font20, black, sign_in_box.x , sign_in_box.y + 10)
        if sign_in_button.draw(screen):
            user, errorDisplay = sign_in(email, password)
            if errorDisplay == None:
                #print(user)
                uid = user["localId"]
                email = ''
                password = ''
                displayName = '' 
                if uid != None:
                    name = getDisplayName(uid)
                    displayCoin = getCoins(uid)
                    login_menu = False
                    start_menu = True
                    running = True
                    #game = True

    pygame.display.update()

# game loop
while running:

    song = loadedSongs[choiceSong]

    _, image_frame = video.read()
    flip_image_frame = cv2.flip(image_frame, 1)

    #cv2.imshow("Movement Detection", flip_image_frame)

    #we put this here so where ever the player was they can quit with the X
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    if start_menu:

        # _, frame = video.read()
        # frame = cv2.flip(frame, 1)
        virtualMouse(flip_image_frame)
        cv2.imshow("Movement Detection", flip_image_frame)
        #cv2.imshow('Virtual Mouse', frame)
        #cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #display background
        #background should be drawn first then everything on top because if we draw button then bg the buttons will not appear, they will be behind
        screen.fill((76, 208, 56))  
        screen.blit(bg, (0,0))
        # display the title
        drawTextCenter(gameName, font40, black, width/2, 60)

        song.stop()

        #display the buttons
        if start_button.draw(screen):
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

    if setting_menu and not start_menu:
        #display background
        screen.fill(green)  
        screen.blit(bg, (0,0))
        screen.blit(bg_car_view, (0,30))
        #display the scores and email of the player
        lastScore = getScore(uid, 'last')
        highScore = getScore(uid, 'high')
        drawTextCenter(name, font30, black, (width/2) - 2, 60)
        drawTextCenter('Latest Score: ' + str(lastScore), font20, black, (width/2) - 2, 100)
        drawTextCenter('Highest Score: ' + str(highScore), font20, black, (width/2) - 2, 130)
        drawTextCenter('Coins: ' + str(displayCoin), font20, black, (width/2) - 2, 160)

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
        
        #display return button and tutorial button
        if return_back_button.draw(screen):
            start_menu = True
            setting_menu = False
        if gameplay_button.draw(screen):
            gameplay_menu = True
            setting_menu = False

    if gameplay_menu:
        drawGameplay()
        if return_back_button.draw(screen):
            setting_menu = True
            gameplay_menu = False

    if game:
        # motion detection
        # _, image_frame = video.read()

        # flip_image_frame = cv2.flip(image_frame, 1)
        
        movementL, movementR = motionDetection(frame1, frame2, flip_image_frame)
        cv2.imshow("Movement Detection", flip_image_frame)
        
        #cv2.imshow("Movement Detection", flip_image_frame)
        #update the frames
        frame1 = frame2
        check, frame2 = video.read()

        # game
        clock.tick(fps) #let the game be diplayed 120 frame per second

        #if there is already a song playing it does not start another one
        if sound and not pygame.mixer.get_busy():
            song.play()

        if not gameover:

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                #see if a key on t0he keyboard is pressed
                if event.type == KEYDOWN:
                    #if the arrow left key is pressed check if the car is not on the last left lane to move
                    if event.key == K_LEFT and player.rect.center[0] > left_lane:
                        player.rect.x -= 100
                        left = True
                        right = False
                    #if the arrow right key is pressed check if the car is not on the last right lane to move
                    elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                        player.rect.x += 100
                        right = True
                        left = False

            if (movementR or movementL) and time.time() - last_movement_time >= 0.5:
                last_movement_time = time.time()  # Update the last movement time
                if movementR and not movementL and player.rect.center[0] < right_lane:
                    player.rect.x += 100
                    right = True
                    left = False
                elif not movementR and movementL and player.rect.center[0] > left_lane:
                    player.rect.x -= 100
                    left = True
                    right = False

            #coin update
            coin_group.update()

            #update the position of the lane_marker so they move
            lane_marker_move_y += speed * 2
            if lane_marker_move_y >= marker_height * 2:
                lane_marker_move_y = 0

            # add a vehicle and coins
            if len(vehicle_group) < 2:
                add_vehicle = True
                for vehicle in vehicle_group:
                    if vehicle.rect.top < vehicle.rect.height * 1.5:
                        add_vehicle = False

                if add_vehicle:
                    lane = random.choice(lanes)
                    image = random.choice(vehicle_images)
                    vehicle = Vehicle(image, lane, height / -2)
                    vehicle_group.add(vehicle)
                    coin = Coins(random.choice(lanes), (height / -2) - 150, speed)
                    coin_group.add(coin)

            # make the vehicles move
            for vehicle in vehicle_group:
                vehicle.rect.y += speed

                if vehicle.rect.top >= height:
                    vehicle.kill()
                    score += 1

                    if score > 0 and score % 5 == 0:
                        speed += 1

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
                    gameover = True


        #display the background of the road
        drawBackground(lane_marker_move_y)

        # draw the player's car
        player_group.draw(screen)

        # draw the vehicles
        vehicle_group.draw(screen)

        coin_group.draw(screen)

        # display the score
        drawTextCenter('Score: ' + str(score), font20, white, 50, 400)
        drawTextCenter('Coins: ' + str(coins), font20, white, 50, 430)

        #remake right and left false so if the player  did not move and collided with anothe vehicle it will be at the bottom
        right = False
        left = False

    if gameover:
        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, (200, 0, 0), (0, 50, width, 100))

        drawTextCenter('Game over', font20, white, width / 2, 90)
        drawTextCenter('Play again?', font20, white, (width / 2), 110)
        #lastScore = score
        saveScore(uid, score)

        #highScore = score
        #displayCoin = getCoins(uid)

        song.stop()

        if reload_button.draw(screen):
            gameover = False
            speed, score, coins = resetGame()
            game = True

        if return_button.draw(screen):
            gameover = False
            start_menu = True
            game = False
            speed, score, coins = resetGame()

    pygame.display.update()
        
video.release()
cv2.destroyAllWindows()
pygame.quit()

# Final-year-project-Bachelor
final year project

The Motion Detection Car Game project is an interactive single player 2D game designed to engage players in a challenging yet entertaining experience. Developed using Python, the game involves controlling a car on a moving road by physically moving in specified areas on the screen to avoid collisions with other vehicles.

I.	Project overview
1.	Features:
a.	Gameplay Mechanics:
-	Players control a car's movement within designated areas on the screen or by using the left and right key arrow.
-	The areas consist of specified rectangles on the right and left sides, detecting motion.
-	The rectangles changes colours to indicate movement.
-	In case of a collision, the player loses the game.
-	The player can navigate the menu screen using a virtual mouse. 
b.	Objective:
-	Guide the car across three lanes, avoiding collisions with other cars on the road while collecting the maximum amount of coins.
c.	User Authentication:
-	Players are required to sign in to their account to access the game.
-	If no existing account is available, the player can sign up and create a new account by entering an email and password.
d.	Firebase Integration:
-	The most recent and highest scores are stored in a Firebase database, making scores and progress trackable, as well as creating competition among players.
-	The amount of coins collected in a round is added to the total amount stored in the database. 
-	The car’s colours unlocked by the player are also stored in it.


2.	Technical Specifications:
The Motion Detection Car Game will be developed using the following technologies:
-	Programming Language: Python
-	Webcam Integration: OpenCV
-	User Authentication: Firebase Authentication
-	Database: Firebase Realtime Database
-	Libraries: pygame - firebase_admin - cv2 - pyrebase4 – mediapipe - pyautogui


Many versions of this game has been made:
- a dynamic one where the window can change sizes
- a static one
- a version with backend
- a version with a virtual mouse moved with the mouvement of the hande detected by the cam

import pygame
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.copyImage = image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x , y)
        self.clicked = False

    def draw(self, surface):
        #get mouse position
        action = False
        pos = pygame.mouse.get_pos()
        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and self.clicked == False:
                    self.clicked = True
                    action = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.clicked = False 

            #0:left button, 1:middle, 2:right

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action
    

# The behavior you’re experiencing with pyautogui.click() not being detected by pygame.mouse.get_pressed() but working with MOUSEBUTTONDOWN is likely due to the way these two methods operate:
# pyautogui.click():
# pyautogui.click() simulates a mouse click at the specified coordinates.
# It moves the mouse cursor to the given position and performs a click (press and release).
# However, it does not directly interact with the operating system’s mouse events that pygame.mouse.get_pressed() relies on.
# pygame.mouse.get_pressed():
# This function provides the current state of all mouse buttons (left, middle, and right).
# It reflects the actual state of the physical mouse buttons as detected by the operating system.
# It does not simulate clicks; instead, it reports the real-time button states

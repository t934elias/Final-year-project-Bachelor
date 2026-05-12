import pygame
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x , y)
        self.clicked = False

    def draw(self, surface):
        #get mouse position
        action = False
        pos = pygame.mouse.get_pos()
        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            #0:left button, 1:middle, 2:right
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:  
            self.clicked = False 

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

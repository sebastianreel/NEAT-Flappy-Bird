#--------------------------------------------------------------------------------------------#
# Author: Sebastian Reel                                                                     #
# Inpiration/Tutorial being followed: Tech with Tim on YouTube.com (videos on his channel)   #
# Project: Flappy Bird Game that will have an AI play and find the best possible playing AI  #
#--------------------------------------------------------------------------------------------#

import pygame
import neat
import os
import random
pygame.font.init()

# setting the dimension of the screen
# these have to be all capital because they are constants
WIN_WIDTH = 500
WIN_HEIGHT = 800
GEN = 0
# Loading images, also capitals
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
                # What is this IMAGE load doing?
                # transform - scale2x --> loading the image twice the size of the original png
                # laod is loading the files within the OS path goinginto the folder "imgs" and picking each bird image
                # Overall, this will animate the images
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

#--------------------------------------------------------------------------------------------------------------------------#
# defining the classes associated with the project

class Birb:
    IMGS = BIRD_IMGS        # Loads the images into the class
    MAX_ROTATION = 25       # how much the bird will tilt
    ROT_VELOCITY = 20       # how much to rotate on each frame
    ANIMATION_TIME = 5      # how long the bird will flap its wings in the frame

    def __init__(self, x, y):   
        self.x = x              # this x and y value represent the beginning value / starting position of the bird
        self.y = y
        self.tilt = 0           # how much te bird is tilting at a point
        self.tick_count = 0     # helps with physics of bird
        self.vel = 0            
        self.height = self.y    # the height of the bird on the screen
        self.img_count = 0      # which image is being used in the animation
        self.img = self.IMGS[0] 

    def jump(self):
        self.vel = -10.5        # the velocity needs to be negative for the bird to go upwards ingame
        self.tick_count = 0
        self.height = self.y 

    def move(self):
        self.tick_count += 1        #a tick went by, the bird moved, basically confirming that

        d = self.vel * self.tick_count + 1.5 * self.tick_count**2 
            # this is a physics eqation that helps figure out displacement based on current velocity
            # tick count will represent time in a way
            # and the "**2" is to the power of 2 (squared)
            # worked out: -10.5 + 1.5 = -9 (pixels upwards)
        if d >= 16:         # confirming the terminal velocity to not go to far
            d = 16
        if d < 0:           # if moving upwards, move up a little more, makes it jump nicely
            d -= 2
        
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:  # checking where the bird is on the plane to make sure it can jump
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:                                   # tilt the bird downwards
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY
    
    def draw(self, win):
        self.img_count += 1                                         # checks what image should show based off image count

        if self.img_count < self.ANIMATION_TIME:                    # keeps checking each elif statement to change the flappy bird image to the next one
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        # flap up then down and then reset
        # then reset image count to zero to redo animation

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2        # fixes some animation to make it make sense
        
        # now we need to rotate the picture around its center in Python
        # the poicture is horizontal and static, so we can change that

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rectangle.topleft);


    # this will get the collision form the images touching each other
    # makes a 2D list of the bird and maps the pixels so the hitbox is more accurate
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
# end bird 

class Pipe:
    GAP = 200       # space between pipes
    VEL = 5         # how fast the pipes move across the screen

    def __init__(self, x):
        self.x = x
        self.height = 0
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)        # keeping track of where top
        self.PIPE_BOTTOM = PIPE_IMG                                         # and bottom are

        self.passed = False                             # for collison purposes 
        self.set_height()

    def set_height(self):                               # this is randomly setting the height of the pipes across the screen from a specified range
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):                                     # moves the pipes based off of inputted velocity above
        self.x -= self.VEL

    def draw(self, win):                                # draws the pipes on playable screen
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        # importing the birds mask
        bird_mask = bird.get_mask()
        # creating a top and bottom mask for the pipes
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
            # offset from bird to top mask
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
            # offset from bottom of bird to bottom mask

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
            # points of the bird hitting the pipes

        if t_point or b_point:
            return True
        return False
# end pipe

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0             # first image
        self.x2 = self.WIDTH    # second image following

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:                # explanation:
            self.x1 = self.x2 + self.WIDTH          # we are drawing two images for the base
        if self.x2 + self.WIDTH < 0:                # putting them next to eachother and move them
            self.x2 = self.x1 + self.WIDTH          # it ends up looking like one continuous image
                                                    # you keep cycling these images over and over again
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
# end base

def draw_window(win, birds, pipes, base, score, gen):
    # blit means draw on the window
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    pygame.display.update()
# end window

#-----------------------------------------------------------------------------------------------------------------#
# now lets draw some of this stuff and make the main loop of the game

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Birb(230, 350))        # starting position for the bird
        g.fitness = 0                       # fitness level that the nueral network grows from
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(700)]                                     # sets pipes as a list (2D list i believe)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # set the window
    clock = pygame.time.Clock()
    score = 0

    run = True                      
    while run:                              # set up the main game loop
        clock.tick(30)                      # cotrl speed of fall   
        for event in pygame.event.get():    
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # making the bird move here
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:                               # checking if there arent any more birds, stops propgram
            run = False
            break

        for x, bird in enumerate(birds):    # moves the birds and gives them fitness for every pixel they move 
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                # checking what happens whe nthe bird collides with the pipe
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
            
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        # killing the bird if it hits the top of the screen or ground
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)
# end main

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # this variable can be used to generate the winning bird for every time the program is opened
    # i did not use this in this version, I just made the game and the nueral network
    winner = p.run(main ,50)    

if __name__ == "__main__":
    # grabs the ile from this directory and runs the configuration for NEAT to be able to work
    local_directory = os.path.dirname(__file__)
    config_path = os.path.join(local_directory, "config-feedforward.txt")
    run(config_path)
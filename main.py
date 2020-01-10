

from __future__ import division
import math
import sys
import os
import datetime
import random
import pygame



def load_image_convert_alpha(filename):
    
    return pygame.image.load(os.path.join('images', filename)).convert_alpha()


def load_sound(filename):
   
    return pygame.mixer.Sound(os.path.join('sounds', filename))


def draw_centered(surface1, surface2, position):
    
    rect = surface1.get_rect()
    rect = rect.move(position[0]-rect.width//2, position[1]-rect.height//2)
    surface2.blit(surface1, rect)


def rotate_center(image, rect, angle):
       
        rotate_image = pygame.transform.rotate(image, angle)
        rotate_rect = rotate_image.get_rect(center=rect.center)
        return rotate_image,rotate_rect


def distance(p, q):
    
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)




class GameObject(object):
    
    def __init__(self, position, image, speed=0):
     
        self.image = image
        self.position = list(position[:])
        self.speed = speed

    def draw_on(self, screen):
        draw_centered(self.image, screen, self.position)

    def size(self):
        return max(self.image.get_height(), self.image.get_width())

    def radius(self):
        return self.image.get_width()/2


class Spaceship(GameObject):
    def __init__(self, position):
       
        super(Spaceship, self).__init__(position,\
            load_image_convert_alpha('spaceship-off.png'))

        self.image_on = load_image_convert_alpha('spaceship-on.png')
        self.direction = [0, -1]
        self.is_throttle_on = False
        self.angle = 0

       
        self.active_missiles = []

    def draw_on(self, screen):
        

      
        if self.is_throttle_on:
            new_image, rect = rotate_center(self.image_on, \
                self.image_on.get_rect(), self.angle)
        else:
            new_image, rect = rotate_center(self.image, \
                self.image.get_rect(), self.angle)

        draw_centered(new_image, screen, self.position)


    def move(self):
        

        
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

     
        self.position[0] += self.direction[0]*self.speed
        self.position[1] += self.direction[1]*self.speed


    def fire(self):
        

       
        adjust = [0, 0]
        adjust[0] = math.sin(-math.radians(self.angle))*self.image.get_width()
        adjust[1] = -math.cos(math.radians(self.angle))*self.image.get_height()

       
        new_missile = Missile((self.position[0]+adjust[0],\
                               self.position[1]+adjust[1]/2),\
                               self.angle)
        self.active_missiles.append(new_missile)



class Missile(GameObject):
    
    def __init__(self, position, angle, speed=15):
        super(Missile, self).__init__(position,\
            load_image_convert_alpha('missile.png'))

        self.angle = angle
        self.direction = [0, 0]
        self.speed = speed


    def move(self):
        

       
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

       
        self.position[0] += self.direction[0]*self.speed
        self.position[1] += self.direction[1]*self.speed



class Rock(GameObject):
    
    def __init__(self, position, size, speed=4):
       

      
        if size in {"big", "normal", "small"}:

            
            str_filename = "rock-" + str(size) + ".png"
            super(Rock, self).__init__(position,\
                load_image_convert_alpha(str_filename))
            self.size = size

        else:
          
            return None

        self.position = list(position)

        self.speed = speed

        
        if bool(random.getrandbits(1)):
            rand_x = random.random()* -1
        else:
            rand_x = random.random()

        if bool(random.getrandbits(1)):
            rand_y = random.random() * -1
        else:
            rand_y = random.random()

        self.direction = [rand_x, rand_y]


    def move(self):
       
        self.position[0] += self.direction[0]*self.speed
        self.position[1] += self.direction[1]*self.speed



class MyGame(object):

    
    PLAYING, DYING, GAME_OVER, STARTING, WELCOME = range(5)

  
    REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT+3)

    def __init__(self):
        
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

      
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))

       
        self.bg_color = 0, 0, 0

       
        self.soundtrack = load_sound('soundtrack.wav')
        self.soundtrack.set_volume(.3)

       
        self.die_sound = load_sound('die.wav')
        self.gameover_sound = load_sound('game_over.wav')
        self.missile_sound = load_sound('fire.wav')

      
        self.big_font = pygame.font.SysFont(None, 100)
        self.medium_font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 25)
       
        self.gameover_text = self.big_font.render('GAME OVER',\
            True, (255, 0, 0))

       
        self.lives_image = load_image_convert_alpha('spaceship-off.png')

        
        self.FPS = 30
        pygame.time.set_timer(self.REFRESH, 1000//self.FPS)

       
        self.death_distances = {"big":90,"normal":65 ,"small":40}

        
        self.do_welcome()

       
        self.fire_time = datetime.datetime.now()


    def do_welcome(self):
        

        
        self.state = MyGame.WELCOME

        
        self.welcome_asteroids = self.big_font.render(">>  DEAD SHOT  <<",\
                                                True, (255, 215, 0))
        self.welcome_desc =  self.medium_font.render(\
            "[Click anywhere/press Enter] to begin!", True, (35, 107, 142))


    def do_init(self):
        

       
        self.rocks = []

       
        self.min_rock_distance = 350

       
        self.start()

        
        for i in range(4):
            self.make_rock()

        
        self.lives = 3
        self.score = 0

        
        self.counter = 0


    def make_rock(self, size="big", pos=None):
        

        
        margin = 200

        if pos == None:
            

            rand_x = random.randint(margin, self.width-margin)
            rand_y = random.randint(margin, self.height-margin)

           
            while distance((rand_x, rand_y), self.spaceship.position) < \
                    self.min_rock_distance:

                
                rand_x = random.randint(0, self.width)
                rand_y = random.randint(0, self.height)

            temp_rock = Rock((rand_x, rand_y), size)

        else:
            
            temp_rock = Rock(pos, size)

        
        self.rocks.append(temp_rock)


    def start(self):
       
        self.spaceship = Spaceship((self.width//2, self.height//2))
        self.missiles = []

       
        self.soundtrack.play(-1, 0, 1000)

       
        self.state = MyGame.PLAYING


    def run(self):
       
        running = True
        while running:
            event = pygame.event.wait()

           
            if event.type == pygame.QUIT:
                running = False

           
            elif event.type == MyGame.REFRESH:

                if self.state != MyGame.WELCOME:

                    keys = pygame.key.get_pressed()

                    if keys[pygame.K_SPACE]:
                        new_time = datetime.datetime.now()
                        if new_time - self.fire_time > \
                                datetime.timedelta(seconds=0.15):
                            

                           
                            self.spaceship.fire()

                           
                            self.missile_sound.play()

                            
                            self.fire_time = new_time

                    if self.state == MyGame.PLAYING:
                        

                        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                            
                            self.spaceship.angle -= 10
                            self.spaceship.angle %= 360

                        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                           
                            self.spaceship.angle += 10
                            self.spaceship.angle %= 360

                        if keys[pygame.K_UP] or keys[pygame.K_w]:
                           
                            self.spaceship.is_throttle_on = True

                            if self.spaceship.speed < 20:
                                self.spaceship.speed += 1
                        else:
                            
                            if self.spaceship.speed > 0:
                                self.spaceship.speed -= 1
                            self.spaceship.is_throttle_on = False

                       
                        if len(self.spaceship.active_missiles) > 0:
                            self.missiles_physics()

                        
                        if len(self.rocks) > 0:
                            self.rocks_physics()

                       
                        self.physics()

                
                self.draw()

            elif event.type == MyGame.START:
                pygame.time.set_timer(MyGame.START, 0) 
                if self.lives < 1:
                    self.game_over()
                else:
                    self.rocks = []
                   
                    for i in range(4):
                        self.make_rock()
                   
                    self.start()

           
            elif event.type == MyGame.RESTART:
                pygame.time.set_timer(MyGame.RESTART, 0)
                self.state = MyGame.STARTING

          
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and (self.state == MyGame.STARTING or\
                            self.state == MyGame.WELCOME):
                self.do_init()

           
            elif event.type == pygame.KEYDOWN \
                    and event.key == pygame.K_RETURN and \
                        (self.state == MyGame.STARTING or \
                            self.state == MyGame.WELCOME):
                self.do_init()

            else:
                pass


    def game_over(self):
       
        self.soundtrack.stop()
       
        self.state = MyGame.GAME_OVER
        self.gameover_sound.play()
        delay = int((self.gameover_sound.get_length()+1)*1000)
        pygame.time.set_timer(MyGame.RESTART, delay)


    def die(self):
       
        self.soundtrack.stop()
       
        self.lives -= 1
        self.counter = 0
        self.state = MyGame.DYING
        self.die_sound.play()
        delay = int((self.die_sound.get_length()+1)*1000)
        pygame.time.set_timer(MyGame.START, delay)


    def physics(self):
        

        if self.state == MyGame.PLAYING:

           
            self.spaceship.move()



    def missiles_physics(self):
        

        if len(self.spaceship.active_missiles) >  0:
            for missile in self.spaceship.active_missiles:
               
                missile.move()

              
                for rock in self.rocks:
                    if rock.size == "big":
                       
                        if distance(missile.position, rock.position) < 80:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("normal", \
                                (rock.position[0]+10, rock.position[1]))
                            self.make_rock("normal", \
                                (rock.position[0]-10, rock.position[1]))
                            self.score += 20

                    elif rock.size == "normal":
                       
                        if distance(missile.position, rock.position) < 55:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("small", \
                                (rock.position[0]+10, rock.position[1]))
                            self.make_rock("small", \
                                (rock.position[0]-10, rock.position[1]))
                            self.score += 50
                    else:
                        
                        if distance(missile.position, rock.position) < 30:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)

                            if len(self.rocks) < 10:
                                self.make_rock()

                            self.score += 100


    def rocks_physics(self):
        
        
        if len(self.rocks) > 0:

            for rock in self.rocks:
              
                rock.move()


                
                if distance(rock.position, self.spaceship.position) < \
                        self.death_distances[rock.size]:
                    self.die()

               
                elif distance(rock.position, (self.width/2, self.height/2)) > \
                     math.sqrt((self.width/2)**2 + (self.height/2)**2):

                    self.rocks.remove(rock)
                    if len(self.rocks) < 10:
                        self.make_rock(rock.size)


    def draw(self):
       
        
        self.screen.fill(self.bg_color)

       
        if self.state != MyGame.WELCOME:

            
            self.spaceship.draw_on(self.screen)

            
            if len(self.spaceship.active_missiles) >  0:
                for missile in self.spaceship.active_missiles:
                    missile.draw_on(self.screen)

            
            if len(self.rocks) >  0:
                for rock in self.rocks:
                    rock.draw_on(self.screen)

           
            if self.state == MyGame.PLAYING:

               
                self.counter += 1

                if self.counter == 20*self.FPS:
               

                    if len(self.rocks) < 15: 
                        self.make_rock()

                    
                    if self.min_rock_distance < 200:
                        self.min_rock_distance -= 50

                    
                    self.counter = 0

           
            scores_text = self.medium_font.render(str(self.score),\
                                                    True, (0, 155, 0))
            draw_centered(scores_text, self.screen,\
                (self.width-scores_text.get_width(), scores_text.get_height()+\
                                                        10))

            
            if self.state == MyGame.GAME_OVER or self.state == MyGame.STARTING:
                draw_centered(self.gameover_text, self.screen,\
                                (self.width//2, self.height//2))

            
            for i in range(self.lives):
                draw_centered(self.lives_image, self.screen,\
                    (self.lives_image.get_width()*i*1.2+40,\
                        self.lives_image.get_height()//2))

        else:
            
            draw_centered(self.welcome_asteroids, self.screen,\
                (self.width//2, self.height//2\
                    -self.welcome_asteroids.get_height()))

            draw_centered(self.welcome_desc, self.screen,\
                (self.width//2, self.height//2\
                    +self.welcome_desc.get_height()))

        
        pygame.display.flip()


MyGame().run()
pygame.quit()
sys.exit()



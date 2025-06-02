import pygame
from os.path import join, exists
from random import randint, uniform

# High score setup
high_score = 0
if exists("highscore.txt"):
    with open("highscore.txt", "r") as file:
        high_score = int(file.read())

class Player(pygame.sprite.Sprite):

    def __init__(self,groups):
        super().__init__(groups)        
        self.image = pygame.image.load(join("images","player.png")).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2))
        self.direction = pygame.Vector2()
        self.speed = 300
        self.health = 5
        self.score = 0
        # cooldown section
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        # shield section
        self.shield_cooldown = 600
        self.last_hit_time = 0

        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        
        recent_key= pygame.key.get_just_pressed()
        if recent_key [pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites,laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        if self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.health <= 0:
            self.kill()
            global game_active
            game_active = False
            global high_score
            if self.score > high_score:
                high_score = self.score
                with open("highscore.txt", "w") as file:
                    file.write(str(high_score))
        self.laser_timer()

        # shield timer
        if pygame.time.get_ticks() - self.last_hit_time < self.shield_cooldown:
            self.image.set_alpha(150)
        else:
            self.image.set_alpha(255)
    
class Star(pygame.sprite.Sprite):

    def __init__(self,groups,surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH),randint(0,WINDOW_HEIGHT)))   

class Laser(pygame.sprite.Sprite):
    def __init__(self,surf,pos,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self,dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    
    def __init__(self,surf,pos,groups, has_life=False):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 2000
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(400,500)
        self.rotation_speed = randint(-5,5)
        self.rotation = 0
        self.has_life = has_life

    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top >= WINDOW_HEIGHT:
            self.kill() 
        self.rotation += self.rotation_speed * dt * 10
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation,1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):

    def __init__(self,frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self,dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class Heart(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 3000 # 3 seconds

    def update(self, dt):
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

def display_score():
    current_score_surf = font_score.render(str(player.score), True,(255,255,255))
    current_score_rect = current_score_surf.get_frect(midbottom = (WINDOW_WIDTH/2,WINDOW_HEIGHT - 50))
    display_surface.blit(current_score_surf,current_score_rect)
    pygame.draw.rect(display_surface,(250,250,250),current_score_rect.inflate(20,10).move(0,-7),5,10)

    high_score_surf = font_score.render(f"HI: {high_score}", True,(255,255,255))
    high_score_rect = high_score_surf.get_frect(midtop = (WINDOW_WIDTH/2, 50))
    display_surface.blit(high_score_surf,high_score_rect)

def display_health():
    for i in range(player.health):
        heart_rect = heart_surf.get_frect(topleft=(30 + i * (heart_surf.get_width() + 5), 30))
        display_surface.blit(heart_surf, heart_rect)

def collisions():

    collision_sprites = pygame.sprite.spritecollide(player,meteor_sprites,False,pygame.sprite.collide_mask)
    if collision_sprites and pygame.time.get_ticks() - player.last_hit_time >= player.shield_cooldown:
        damage_sound.play()
        player.health -= 1
        player.last_hit_time = pygame.time.get_ticks()
        for sprite in collision_sprites:
            sprite.kill()
        

    for laser in laser_sprites:
        collided_meteors = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_meteors:
            laser.kill()
            for meteor in collided_meteors:
                player.score += 1
                AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites)
                explosion_sound.play()
                if meteor.has_life:
                    Heart(heart_plus_one_surf, meteor.rect.center, (all_sprites, heart_sprites))

    # Player-heart collision
    collided_hearts = pygame.sprite.spritecollide(player, heart_sprites, True)
    if collided_hearts:
        if player.health < 5:
            player.health += 1

# general setup
pygame.init()
WINDOW_WIDTH , WINDOW_HEIGHT = 1280 , 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH , WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
running = True
clock = pygame.time.Clock()
game_active = False
paused = False

# imports
star_surf = pygame.image.load(join("images","star.png")).convert_alpha()
meteor_surf = pygame.image.load(join("images","meteor.png")).convert_alpha()
laser_surf = pygame.image.load(join("images","laser.png")).convert_alpha()

font_score = pygame.font.Font(join('images','oxanium-bold.ttf'), 40)
font_health = pygame.font.Font(join('images','oxanium-bold.ttf'), 20)
font_start = pygame.font.Font(join('images','oxanium-bold.ttf'), 80)

heart_surf = pygame.image.load(join("images","heart.png")).convert_alpha()
heart_plus_one_surf = pygame.image.load(join("images","heart_plus_one.svg")).convert_alpha()

explosion_frames = [pygame.image.load(join("images","explosion",f"{i}.png")).convert_alpha() for i in range (21)]

laser_sound = pygame.mixer.Sound(join("audio","laser.wav"))
laser_sound.set_volume(0.5)

explosion_sound = pygame.mixer.Sound(join("audio","explosion.wav"))
explosion_sound.set_volume(0.5)

damage_sound = pygame.mixer.Sound(join("audio","damage.ogg"))
damage_sound.set_volume(0.5)

game_music = pygame.mixer.Sound(join("audio","game_music.wav"))
game_music.set_volume(0.3)
game_music.play(loops = -1)

# custom events
meteor_event = pygame.event.custom_type() + 1
pygame.time.set_timer(meteor_event, 1000)

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
heart_sprites = pygame.sprite.Group()

# game setup
player = Player(all_sprites)
for i in range(20):
    Star(all_sprites,star_surf)


while running: # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not game_active:
                if start_rect.collidepoint(event.pos):
                    game_active = True
                    # Clear all existing sprites
                    all_sprites.empty()
                    meteor_sprites.empty()
                    laser_sprites.empty()
                    # Re-initialize player and stars
                    player = Player(all_sprites)
                    for i in range(20):
                        Star(all_sprites, star_surf)
            elif paused:
                if resume_rect.collidepoint(event.pos):
                    paused = False
                elif quit_rect.collidepoint(event.pos):
                    running = False
        if event.type == meteor_event and game_active and not paused:
            x,y = randint(0,WINDOW_WIDTH),randint(-200,-100)
            # Every 5th meteor has a life
            if player.score % 5 == 0 and player.score != 0:
                Meteor(meteor_surf,(x,y),(all_sprites, meteor_sprites), has_life=True)
            else:
                Meteor(meteor_surf,(x,y),(all_sprites, meteor_sprites))

    if game_active and not paused:
        dt = clock.tick() / 1000

        # update
        all_sprites.update(dt)
        collisions()

        # draw
        display_surface.fill("#3a2e3f")
        display_score()
        display_health()
        # Draw all sprites except the player
        for sprite in all_sprites:
            if sprite != player:
                display_surface.blit(sprite.image, sprite.rect)
        # Draw the player last to ensure it's on top
        display_surface.blit(player.image, player.rect)

    elif not game_active:
        display_surface.fill("#3a2e3f")
        start_text = font_start.render("Start", True, (255, 255, 255))
        start_rect = start_text.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        display_surface.blit(start_text, start_rect)

        mouse_pos = pygame.mouse.get_pos()
        if start_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif paused:
        display_surface.fill("#3a2e3f")
        pause_text = font_start.render("Paused", True, (255, 255, 255))
        pause_rect = pause_text.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 100))
        display_surface.blit(pause_text, pause_rect)

        resume_text = font_score.render("Resume", True, (255, 255, 255))
        resume_rect = resume_text.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        display_surface.blit(resume_text, resume_rect)

        quit_text = font_score.render("Quit", True, (255, 255, 255))
        quit_rect = quit_text.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 70))
        display_surface.blit(quit_text, quit_rect)

        mouse_pos = pygame.mouse.get_pos()
        if resume_rect.collidepoint(mouse_pos) or quit_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    pygame.display.update()
pygame.QUIT

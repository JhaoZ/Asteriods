import pygame, sys, random

pygame.init()

size = (width, height) = (750, 750)
screen = pygame.display.set_mode(size)

#variables
speed = [0,0]
bulletSpeed = 20
playerpos = (0,0)

class MainCharacter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('./IdleRocket.png')
        self.image = pygame.transform.scale(self.image, (60, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (375, 375)
        self.last_shot = 0
        self.lives = 5
        self.last_hit = 0

    def update(self):
        self.last_shot = pygame.time.get_ticks()

    def loseLife(self):
        self.lives -= 1
        if self.lives <= 0:
            print("Game Over!")
            sys.exit()
        self.last_hit = pygame.time.get_ticks()


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('./Asteriod.png')
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.rect.center = (width+20,0)
        self.speed = 0

    def spawn(self, h, s):
        self.rect.center = (width+20, h)
        self.speed = s

class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./Laser.png")
        self.image = pygame.transform.scale(self.image, (10,2))
        self.rect = self.image.get_rect()
        self.speed = 10

    def update(self, x, y):
        self.rect.center = (x, y)

class BulletCase(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./BulletCase.png")
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.speed = 5

    def spawn(self, h):
        self.rect.center = (width+20, h)

main = MainCharacter()
main_sprite = pygame.sprite.Group()
main_sprite.add(main)

bullet_group = pygame.sprite.Group()
asteriod_group = pygame.sprite.Group()
power_up_group = pygame.sprite.Group()

bullets = []
asteriods = []
bulletCases = []

lastspawn = 0
clock = pygame.time.Clock()
shoot_interval = 500
to_spawn_interval = 5000
min_asteriod_speed = 2
max_asteriod_speed = 5
power_up_spawn_interval = 5000
last_power_up_spawn = 0
score = 0
last_score_gain = 0
powerup_types = ['BulletCase']
poweruping = False
starting_powerup_time = 0
powerup_interval = 0
time = 0
while True:
    if pygame.time.get_ticks() < 10000:
        time = str(pygame.time.get_ticks())[0:1] + '.' + str(pygame.time.get_ticks())[1:3]
    else:
        time = str(pygame.time.get_ticks())[0:2] + '.' + str(pygame.time.get_ticks())[2:4]
    clock.tick(60)
    screen.fill((0, 0, 0))
    main_sprite.draw(screen)

    key = pygame.key.get_pressed()
    playerpos = [main.rect.x+30, main.rect.y+25]

    bullet_group.draw(screen)
    if key[pygame.K_SPACE]:
        interval = pygame.time.get_ticks() - main.last_shot 
        if interval > shoot_interval: # one second 
            main_sprite.update()
            b = Bullet()
            b.update(playerpos[0]+10, playerpos[1])
            bullet_group.add(b)
            bullets.append(b)    
    
    for bullet in bullets:
        bullet.rect = bullet.rect.move([bullet.speed, 0])
        if bullet.rect.left > width:
            bullets.remove(bullet)
            bullet_group.remove(bullet)

    if pygame.time.get_ticks() - lastspawn > to_spawn_interval:
        lastspawn = pygame.time.get_ticks()
        a = Asteroid()
        a.spawn(random.randrange(0, height, 10), random.randrange(-min_asteriod_speed, -max_asteriod_speed, -1))
        asteriods.append(a)
        asteriod_group.add(a)
        
    asteriod_group.draw(screen)
    for aster in asteriods:
        aster.rect = aster.rect.move([aster.speed,0])
        if aster.rect.left < -20:
            asteriods.remove(aster)
            asteriod_group.remove(aster)


    power_up_group.draw(screen)

    if pygame.time.get_ticks() - last_power_up_spawn > power_up_spawn_interval and not poweruping:
        power_up_spawn_interval = random.randrange(5000, 10000, 1000)
        last_power_up_spawn = pygame.time.get_ticks()
        starting_powerup_time = pygame.time.get_ticks()
        power = random.choice(powerup_types)
        if power == "BulletCase":
            bc = BulletCase()
            bulletCases.append(bc)
            power_up_group.add(bc)
            bc.spawn(random.randrange(0, height, 10))
           
    if poweruping:
        if pygame.time.get_ticks() - starting_powerup_time > powerup_interval:
            poweruping = False
            shoot_interval = 500

    for bc in bulletCases:
        bc.rect = bc.rect.move([-bc.speed, 0])   
        if bc.rect.left < -20:
            bulletCases.remove(bc)
            power_up_group.remove(bc)

    myFont = pygame.font.SysFont("Times New Roman", 18)
    numLivesDraw = myFont.render(f"{main.lives} lives remaining", 1, (250, 250, 250))
    scoreDraw = myFont.render(f"Score: {score}", 1, (250, 250, 250))
    TimeDraw = myFont.render(f"Time: {time}", 1, (250, 250, 250))
    screen.blit(numLivesDraw, (0, 0))
    screen.blit(scoreDraw, (0, 15))
    screen.blit(TimeDraw, (0, 30))


    # Finish Rendering
    pygame.display.flip()


    # Collision Management

    laser_asteriod_collision = pygame.sprite.groupcollide(bullet_group, asteriod_group, True, True)
    if laser_asteriod_collision != {}:
        score += 1000

    player_asteriod_collision = pygame.sprite.spritecollideany(main, asteriod_group)
    if player_asteriod_collision != None:
        damage_interval = pygame.time.get_ticks() - main.last_hit
        if damage_interval > 1000:
            asteriods.remove(player_asteriod_collision)
            asteriod_group.remove(player_asteriod_collision)
            main.loseLife()

    laser_powerup_collision = pygame.sprite.groupcollide(bullet_group, power_up_group, True, True)
    if laser_powerup_collision != {}:
        powerup_interval = 5000
        poweruping = True
        shoot_interval = 100

    player_powerup_collision = pygame.sprite.spritecollideany(main, power_up_group)
    if player_powerup_collision != None:
        powerup_interval = 5000
        poweruping = True
        shoot_interval = 100
        bulletCases.remove(player_powerup_collision)
        power_up_group.remove(player_powerup_collision)


    # Difficulty Ramp
    if pygame.time.get_ticks() > 60000:
        to_spawn_interval = 100
        min_asteriod_speed = 12
        max_asteriod_speed = 20
    elif pygame.time.get_ticks() > 40000:
        to_spawn_interval = 300
    elif pygame.time.get_ticks() > 35000:
        to_spawn_interval = 400
        min_asteriod_speed = 8
        max_asteriod_speed = 15
    elif pygame.time.get_ticks() > 30000:
        to_spawn_interval = 500
    elif pygame.time.get_ticks() > 25000:
        to_spawn_interval = 800
    elif pygame.time.get_ticks() > 20000:
        to_spawn_interval = 1000
        max_asteriod_speed = 12
    elif pygame.time.get_ticks() > 15000:
        to_spawn_interval = 1500
        min_asteriod_speed = 6
        max_asteriod_speed = 10
    elif pygame.time.get_ticks() > 10000:
        to_spawn_interval = 3000
        min_asteriod_speed = 5
        max_asteriod_speed = 8
    elif pygame.time.get_ticks() > 5000:
        to_spawn_interval = 4000
        min_asteriod_speed = 4
    
    # Score Tracking

    if pygame.time.get_ticks() - last_score_gain > 1000:
        last_score_gain = pygame.time.get_ticks()
        score += 100    

    # Movement

    if key[pygame.K_a] and speed[0] > -10:
        speed[0] -= 0.2
    if key[pygame.K_d] and speed[0] < 10:
        speed[0] += 0.2
    if key[pygame.K_w] and speed[1] > -10:
        speed[1] -= 0.2
    if key[pygame.K_s] and speed[1] < 10:
        speed[1] += 0.2

    if main.rect.left < 0 or main.rect.right > width:
        speed[0] = -speed[0]
    if main.rect.top < 0 or main.rect.bottom > height:
        speed[1] = -speed[1]

    if speed[0] > 10:
        speed[0] = 10
    if speed[0] < -10:
        speed[0] = -10
    if speed[1] > 10:
        speed[1] = 10
    if speed[1] < -10:
        speed[1] = -10

    if speed[0] > 1.1:
        speed[0] -= 0.01
        if key[pygame.K_a]:
            speed[0] -= 0.01
    if speed[0] < -1.1:
        speed[0] += 0.01
        if key[pygame.K_d]:
            speed[0] -= 0.01
    if speed[1] > 1.1:
        speed[1] -= 0.01
        if key[pygame.K_s]:
            speed[1] -= 0.01
    if speed[1] < -1.1:
        speed[1] += 0.01
        if key[pygame.K_w]:
            speed[1] -= 0.01

    #print(speed)
    
    main.rect = main.rect.move(speed)


    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()

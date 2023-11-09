import pygame
import random

# Inicializacia hry
pygame.init()

# Obrazovka
width = 1200
height = 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Harry Potter")

# Nastavenie hry
fps = 60
clock = pygame.time.Clock()


# Classy
class Game:
    def __init__(self, our_player, group_of_dementors):
        self.score = 0
        self.round_number = 0

        self.round_time = 0
        self.slow_down_cycle = 0

        self.our_player = our_player
        self.group_of_dementors = group_of_dementors

        # Hudba v pozadi
        pygame.mixer.music.load("media/bg-music-hp.wav")
        pygame.mixer.music.play(-1, 0.0)

        # Fonty
        self.potter_font = pygame.font.Font("fonts/Harry.ttf", 24)
        self.potter_font_big = pygame.font.Font("fonts/Harry.ttf", 45)

        # Obrazok v pozadi
        self.background_image = pygame.image.load("img/bg-dementors.png")
        self.background_image_rect = self.background_image.get_rect()
        self.background_image_rect.topleft = (0, 0)

        # Obrazky
        blue_image = pygame.image.load("img/mozkomor-modry.png")
        green_image = pygame.image.load("img/mozkomor-zeleny.png")
        purple_image = pygame.image.load("img/mozkomor-ruzovy.png")
        yellow_image = pygame.image.load("img/mozkomor-zluty.png")
        self.dementors_images = [blue_image, green_image, purple_image, yellow_image]

        # Generujeme dementora ktoreho chceme chytit
        self.dementor_catch_type = random.randint(0, 3)
        self.dementor_catch_image = self.dementors_images[self.dementor_catch_type]

        self.dementor_catch_image_rect = self.dementor_catch_image.get_rect()
        self.dementor_catch_image_rect.centerx = width / 2
        self.dementor_catch_image_rect.top = 25

    # Kod ktory sa vola stale dokola
    def update(self):
        self.slow_down_cycle += 1
        if self.slow_down_cycle == fps:
            self.round_time += 1
            self.slow_down_cycle = 0

        # Kontrola kolizie
        self.check_collisions()

    # Vykresluje vsetko v hre
    def draw(self):
        dark_yellow = pygame.Color("#938f0c")
        blue = (21, 31, 217)
        green = (24, 194, 38)
        purple = (195, 23, 189)
        yellow = (195, 181, 23)
        colors = [blue, green, purple, yellow]

        # Nastavenie textu
        catch_text = self.potter_font.render("Catch this dementor", True, dark_yellow)
        catch_text_rect = catch_text.get_rect()
        catch_text_rect.centerx = width / 2
        catch_text_rect.top = 5

        score_text = self.potter_font.render(f"Score: {self.score}", True, dark_yellow)
        score_text_rect = score_text.get_rect()
        score_text_rect.topleft = (10, 4)

        lives_text = self.potter_font.render(f"Lives: {self.our_player.lives}", True, dark_yellow)
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.topleft = (10, 30)

        round_text = self.potter_font.render(f"Round: {self.round_number}", True, dark_yellow)
        round_text_rect = round_text.get_rect()
        round_text_rect.topleft = (10, 60)

        time_text = self.potter_font.render(f"Time round: {self.round_time}", True, dark_yellow)
        time_text_rect = time_text.get_rect()
        time_text_rect.topright = (width - 5, 5)

        safe_zone_text = self.potter_font.render(f"Safe zone: {self.our_player.enter_safe_zone}", True, dark_yellow)
        safe_zone_text_rect = safe_zone_text.get_rect()
        safe_zone_text_rect.topright = (width - 10, 35)

        # Blitting
        screen.blit(catch_text, catch_text_rect)
        screen.blit(score_text, score_text_rect)
        screen.blit(lives_text, lives_text_rect)
        screen.blit(round_text, round_text_rect)
        screen.blit(time_text, time_text_rect)
        screen.blit(safe_zone_text, safe_zone_text_rect)

        # Obrazok dementora ktoreho mame chytit
        screen.blit(self.dementor_catch_image, self.dementor_catch_image_rect)

        # Tvary
        pygame.draw.rect(screen, colors[self.dementor_catch_type], (0, 100, width, height - 200), 4)

    # Kontroluje koliziu Harryho s dementorom
    def check_collisions(self):
        # s akym dementorom sme sa zrazili
        collided_dementor = pygame.sprite.spritecollideany(self.our_player, self.group_of_dementors)

        if collided_dementor:
            if collided_dementor.type == self.dementor_catch_type:
                self.our_player.catch_sound.play()
                self.score += 10 * self.round_number
                # Odstranime chyteneho dementora
                collided_dementor.remove(self.group_of_dementors)
                # Existuju dalsi dementori ktorych mozem chytat
                if self.group_of_dementors:
                    self.choose_new_target()
                else:
                    # Kolo je dokoncene vsetkych dementorov sme chytili
                    self.our_player.reset()
                    self.start_new_round()
            else:
                self.our_player.wrong_sound.play()
                self.our_player.lives -= 1
                # Je koniec hry = dosli zivoty
                if self.our_player.lives <= 0:
                    self.pasuse_game(f"Your score: {self.score}", "Press enter if you play again")
                    self.reset_game()
                self.our_player.reset()

    # Zahaji nove kolo
    def start_new_round(self):
        self.score += int(100 * (self.round_number / (1 + self.round_time)))

        # Resetujeme hodnoty
        self.round_time = 0
        self.slow_down_cycle = 0
        self.round_number += 1
        self.our_player.enter_safe_zone += 1

        # Vycistime skupinu dementorov
        for deleted_dementor in self.group_of_dementors:
            self.group_of_dementors.remove(deleted_dementor)

        for i in range(self.round_number):
            self.group_of_dementors.add(
                Dementor(random.randint(0, width - 64), random.randint(100, height - 164), self.dementors_images[0], 0))
            self.group_of_dementors.add(
                Dementor(random.randint(0, width - 64), random.randint(100, height - 164), self.dementors_images[1], 1))
            self.group_of_dementors.add(
                Dementor(random.randint(0, width - 64), random.randint(100, height - 164), self.dementors_images[2], 2))
            self.group_of_dementors.add(
                Dementor(random.randint(0, width - 64), random.randint(100, height - 164), self.dementors_images[3], 3))

            # Vyberame noveho dementora ktoreho mame chytit
            self.choose_new_target()

    # Vybera noveho dementora ktoreho mame chytit
    def choose_new_target(self):
        new_dementor_to_catch = random.choice(self.group_of_dementors.sprites())
        self.dementor_catch_type = new_dementor_to_catch.type
        self.dementor_catch_image = new_dementor_to_catch.image

    # Pozastavenie hry
    def pasuse_game(self, main_text, subheading_text):
        global lets_continue
        # Nastavenie farieb
        dark_yellow = pygame.Color("#938f0c")
        black = (0, 0, 0)

        # Hlavny text pre pause
        main_text_create = self.potter_font_big.render(main_text, True, dark_yellow)
        main_text_create_rect = main_text_create.get_rect()
        main_text_create_rect.center = (width / 2, height / 2)

        # Podnadpis pre pause
        subheading_text_create = self.potter_font_big.render(subheading_text, True, dark_yellow)
        subheading_text_create_rect = subheading_text_create.get_rect()
        subheading_text_create_rect.center = (width / 2, height / 2 + 60)

        # Zobrazenie textu
        screen.fill(black)
        screen.blit(main_text_create, main_text_create_rect)
        screen.blit(subheading_text_create, subheading_text_create_rect)
        pygame.display.update()

        # Zastavenie hry
        paused = True
        while paused:
            for one_event in pygame.event.get():
                if one_event.type == pygame.KEYDOWN:
                    if one_event.key == pygame.K_RETURN:
                        paused = False
                if one_event.type == pygame.QUIT:
                    paused = False
                    lets_continue = False

    # Resetuje hru
    def reset_game(self):
        self.score = 0
        self.round_number = 0
        self.our_player.lives = 5
        self.our_player.enter_safe_zone = 3
        self.start_new_round()

        # Pustenie music v pozadi
        pygame.mixer.music.play(-1, 0.0)


class Dementor(pygame.sprite.Sprite):
    # construktor
    def __init__(self, x, y, image, dementor_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Typy dementorov 0-modry,1-zeleny,2-ruzovy,3-zlty
        self.type = dementor_type

        # Nastavenie nahodneho smeru dementora
        self.x = random.choice([-1, 1])
        self.y = random.choice([-1, 1])
        self.speed = random.randint(1, 5)

    def update(self):
        # Pohyb dementora
        self.rect.x += self.x * self.speed
        self.rect.y += self.y * self.speed

        # odraz dementora
        if self.rect.left < 0 or self.rect.right > width:
            self.x = -1 * self.x

        if self.rect.top < 100 or self.rect.bottom > height - 100:
            self.y = -1 * self.y


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("img/potter-icon.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.bottom = height - 10

        self.lives = 5
        self.enter_safe_zone = 3
        self.speed = 8

        self.catch_sound = pygame.mixer.Sound("media/expecto-patronum.mp3")
        self.catch_sound.set_volume(0.1)
        self.wrong_sound = pygame.mixer.Sound("media/wrong.wav")
        self.wrong_sound.set_volume(0.1)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 100:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < height - 100:
            self.rect.y += self.speed

    # Navrat do bezpecnej zony
    def back_to_safe_zone(self):
        if self.enter_safe_zone > 0:
            self.enter_safe_zone -= 1
            self.rect.bottom = height

    # Vracia hraca spat na vychodiskovu poziciu
    def reset(self):
        self.rect.centerx = width / 2
        self.rect.bottom = height


# Skupina dementorov
dementor_group = pygame.sprite.Group()

# Skupina hracov
player_group = pygame.sprite.Group()
one_player = Player()
player_group.add(one_player)

# Objekt game
my_game = Game(one_player, dementor_group)
my_game.pasuse_game("Harry Potter", "Press enter to start game")
my_game.start_new_round()

# Hlavny cyklus
lets_continue = True
while lets_continue:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            lets_continue = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                one_player.back_to_safe_zone()

    # Vypln obrazovku
    screen.blit(my_game.background_image, my_game.background_image_rect)

    # Updatujeme skupinu dementorov
    dementor_group.draw(screen)
    dementor_group.update()

    # Updatujeme skupinu hracov
    player_group.draw(screen)
    player_group.update()

    # Updatujeme objekt podla classy Game
    my_game.update()
    my_game.draw()

    # Updatujeme obrazovku
    pygame.display.update()

    # Spomalenie cyklu
    clock.tick(fps)

# Ukončenie hry
pygame.quit()

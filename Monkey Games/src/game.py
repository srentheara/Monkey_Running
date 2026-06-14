# ============================================================
# game.py
# Game class --- controls all screens and game logic
# ============================================================

import pygame
import sys
import os
import random

from src.monkey   import Monkey
from src.obstacle import Obstacle, Banana
from src.button   import Button


# ------ Paths ---------------------------------------------------------------------------------------------------------------------------------------------------------------
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR     = os.path.join(BASE_DIR, "assets", "images")
DATA_DIR       = os.path.join(BASE_DIR, "assets", "data")
HIGHSCORE_FILE = os.path.join(DATA_DIR, "highscore.txt")

# ------ Screen constants ---------------------------------------------------------------------------------------------------------------------------------
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 500
FPS           = 60

# ------ Colours ---------------------------------------------------------------------------------------------------------------------------------------------------------
WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)
YELLOW   = (255, 220,  30)
BROWN    = (101,  67,  33)
SKY      = (135, 206, 235)
GREEN    = (34,  139,  34)
ORANGE   = (255, 140,   0)
GREY     = (80,   80,  80)
GOLD     = (255, 215,   0)
RED      = (200,   0,   0)
DARK_BG  = (20,   20,  50)
DARK_RED = (80,   0,   0)
DARK_GRN = (10,  60,  10)


def _try_load_font(size, bold=False):
    """
    Try several font names that support a wide Unicode range.
    Falls back to pygame default if none are found.
    """
    candidates = [
        "Segoe UI Emoji",   
        "Arial Unicode MS",
        "Noto Color Emoji",
        "DejaVu Sans",
        "Arial",
        "Helvetica",
    ]
    for name in candidates:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            # Quick test --- if the font can render a basic char it's usable
            return font
        except Exception:
            continue
    return pygame.font.Font(None, size)


class Game:
    """
    MAIN GAME CLASS.
    Controls all screens and the main game loop.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Monkey Running")
        self.clock = pygame.time.Clock()

        # ------ Fonts ------------------------------------------------------------------------------------------------------------------------------------------
        self.font_large  = _try_load_font(48, bold=True)
        self.font_medium = _try_load_font(30, bold=True)
        self.font_small  = _try_load_font(22)
        self.font_tiny   = _try_load_font(18)

        # ------ Game state ---------------------------------------------------------------------------------------------------------------------------
        self.level            = 1
        self.high_score       = 0
        self.running          = True
        self.paused           = False
        self.distance_counter = 0

        # ------ Load assets ------------------------------------------------------------------------------------------------------------------------
        self.images = self._load_images()
        self._load_sounds()

        # ------ Create game objects ------------------------------------------------------------------------------------------------
        self._init_game_objects()

        # ------ Build UI buttons ---------------------------------------------------------------------------------------------------------
        self._build_buttons()

        # ------ Scrolling background state ---------------------------------------------------------------------------
        self.bg_x1 = 0
        self.bg_x2 = SCREEN_WIDTH

        # ------ Load stored high score ---------------------------------------------------------------------------------------
        self.high_score = self._load_high_score()

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _load_images() --- Try-Except for every image
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _load_images(self):
        images     = {}
        image_files = {
            "monkey":     "monkey.png",
            "banana":     "banana.png",
            "fire":       "fire.png",
            "rock":       "rock.png",
            "spike":      "spike.png",
            "background": "background.png",
        }
        for key, filename in image_files.items():
            try:
                path = os.path.join(IMAGES_DIR, filename)
                images[key] = pygame.image.load(path).convert_alpha()
            except (pygame.error, FileNotFoundError) as e:
                print(f"[Image Warning] Could not load '{filename}': {e}")
                images[key] = None
        return images

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _load_sounds() --- Try-Except: game runs fine without sound
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _load_sounds(self):
        self.sounds = {}
        self.music_on = False
        SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")

        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

            # Load each sound effect with try-except so missing files don't crash
            sound_files = {
                "jump":    "jump.wav",
                "collect": "collect.wav",
                "gameover":"gameover.wav",
                "levelup": "levelup.wav",
            }
            for key, filename in sound_files.items():
                try:
                    path = os.path.join(SOUNDS_DIR, filename)
                    self.sounds[key] = pygame.mixer.Sound(path)
                    self.sounds[key].set_volume(0.55)
                    print(f"[Sound] Loaded: {filename}")
                except (pygame.error, FileNotFoundError) as e:
                    print(f"[Sound Warning] Could not load '{filename}': {e}")

            # Load background music separately via pygame.mixer.music
            try:
                bg_path = os.path.join(SOUNDS_DIR, "background_music.wav")
                pygame.mixer.music.load(bg_path)
                pygame.mixer.music.set_volume(0.35)
                self.music_on = True
                print("[Sound] Background music loaded.")
            except (pygame.error, FileNotFoundError) as e:
                print(f"[Sound Warning] Could not load background music: {e}")

        except pygame.error as e:
            print(f"[Sound Warning] Could not initialise audio mixer: {e}")

    def _play_sound(self, name):
        """Play a sound effect safely."""
        try:
            if name in self.sounds:
                self.sounds[name].play()
        except Exception as e:
            print(f"[Sound Warning] Could not play '{name}': {e}")

    def _start_music(self):
        """Start looping the background music."""
        try:
            if self.music_on:
                pygame.mixer.music.play(-1)   # -1 = loop forever
        except Exception as e:
            print(f"[Sound Warning] Could not start music: {e}")

    def _stop_music(self):
        """Stop the background music."""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def _pause_music(self):
        """Pause the background music."""
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

    def _resume_music(self):
        """Resume the background music after a pause."""
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _init_game_objects()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _init_game_objects(self):
        self.monkey = Monkey(100, Monkey.GROUND_Y, self.images["monkey"])
        self.obstacles = [
            Obstacle("fire",  self.images["fire"],  speed=self._base_speed()),
            Obstacle("rock",  self.images["rock"],  speed=self._base_speed()),
            Obstacle("spike", self.images["spike"], speed=self._base_speed()),
        ]
        self.bananas = [
            Banana(self.images["banana"], speed=self._base_speed()),
            Banana(self.images["banana"], speed=self._base_speed()),
        ]

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _build_buttons() --- plain text labels, no emojis
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _build_buttons(self):
        cx = SCREEN_WIDTH // 2

        # Main menu
        self.btn_play  = Button(cx-115, 240, 230, 55, "  PLAY",
                                colour=(40,160,60), hover_colour=(60,210,80))
        self.btn_instr = Button(cx-115, 310, 230, 55, "  INSTRUCTIONS",
                                colour=(40,100,180), hover_colour=(60,140,220))
        self.btn_exit  = Button(cx-115, 380, 230, 55, "  EXIT",
                                colour=(180,40,40), hover_colour=(220,60,60))

        # Pause
        self.btn_resume = Button(cx-120, 240, 240, 55, "  RESUME",
                                 colour=(40,160,60), hover_colour=(60,210,80))
        self.btn_menu   = Button(cx-120, 310, 240, 55, "MENU",
                                 colour=(40,100,180), hover_colour=(60,140,220))
        self.btn_quit   = Button(cx-120, 380, 240, 55, "  QUIT GAME",
                                 colour=(180,40,40), hover_colour=(220,60,60))

        # Game-over / victory
        self.btn_retry = Button(cx-130, 330, 260, 55, "  TRY AGAIN",
                                colour=(40,160,60), hover_colour=(60,210,80))
        self.btn_back  = Button(cx-130, 400, 260, 55, " MENU",
                                colour=(40,100,180), hover_colour=(60,140,220))

        # Instructions back
        self.btn_instr_back = Button(cx-100, 430, 200, 45, "< BACK",
                                     colour=(80,80,80), hover_colour=(120,120,120))

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Level speed / count helpers
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _base_speed(self):
        if   self.level <= 5:  return 4 + (self.level - 1) * 0.4
        elif self.level <= 10: return 6 + (self.level - 6) * 0.4
        elif self.level <= 15: return 8 + (self.level - 11) * 0.4
        else:                  return 10 + (self.level - 16) * 0.6

    def _obstacle_count(self):
        if   self.level <= 5:  return 1
        elif self.level <= 10: return 2
        elif self.level <= 15: return 3
        else:                  return min(3 + (self.level - 16), 5)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # High score file I/O  --- Try-Except
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _load_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 0
        except ValueError:
            return 0
        except Exception as e:
            print(f"[HighScore] Error reading: {e}")
            return 0

    def _save_high_score(self, score):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(score))
            print(f"[HighScore] Saved: {score}")
        except PermissionError:
            print("[HighScore] Permission denied.")
        except Exception as e:
            print(f"[HighScore] Error saving: {e}")

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _draw_background()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _draw_background(self):
        if self.images["background"]:
            bg    = pygame.transform.scale(
                        self.images["background"], (SCREEN_WIDTH, SCREEN_HEIGHT))
            speed = max(1, int(self._base_speed() * 0.5))
            self.bg_x1 -= speed
            self.bg_x2 -= speed
            if self.bg_x1 <= -SCREEN_WIDTH: self.bg_x1 = SCREEN_WIDTH
            if self.bg_x2 <= -SCREEN_WIDTH: self.bg_x2 = SCREEN_WIDTH
            self.screen.blit(bg, (self.bg_x1, 0))
            self.screen.blit(bg, (self.bg_x2, 0))
        else:
            self.screen.fill(SKY)
            pygame.draw.rect(self.screen, GREEN,
                             (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))
        pygame.draw.line(self.screen, BROWN,
                         (0, Monkey.GROUND_Y + 80),
                         (SCREEN_WIDTH, Monkey.GROUND_Y + 80), 3)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _draw_icon()  --- draw small coloured shape as button icon
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _draw_icon(self, surface, icon_type, cx, cy, size=14):
        """Draw a simple geometric icon (no emoji needed)."""
        if icon_type == "play":        # right-pointing triangle
            pts = [(cx-size//2, cy-size), (cx-size//2, cy+size), (cx+size, cy)]
            pygame.draw.polygon(surface, WHITE, pts)
        elif icon_type == "book":      # rectangle with lines
            r = pygame.Rect(cx-size, cy-size+2, size*2, size*2-2)
            pygame.draw.rect(surface, WHITE, r, 2)
            pygame.draw.line(surface, WHITE, (cx-size+3, cy-3), (cx+size-3, cy-3), 2)
            pygame.draw.line(surface, WHITE, (cx-size+3, cy+3), (cx+size-3, cy+3), 2)
        elif icon_type == "x":         # X cross
            pygame.draw.line(surface, WHITE,
                             (cx-size, cy-size), (cx+size, cy+size), 3)
            pygame.draw.line(surface, WHITE,
                             (cx+size, cy-size), (cx-size, cy+size), 3)
        elif icon_type == "home":      # house shape
            pts = [(cx, cy-size), (cx-size, cy), (cx+size, cy)]
            pygame.draw.polygon(surface, WHITE, pts)
            pygame.draw.rect(surface, WHITE,
                             (cx-size//2, cy, size, size), 0)
        elif icon_type == "refresh":   # circular arrow (simplified)
            pygame.draw.arc(surface, WHITE,
                            (cx-size, cy-size, size*2, size*2),
                            0.3, 5.5, 3)
            pts = [(cx+size-2, cy-size+4),
                   (cx+size+4, cy-size-2),
                   (cx+size+6, cy-size+6)]
            pygame.draw.polygon(surface, WHITE, pts)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # show_score()  --- HUD overlay
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_score(self):
        panel = pygame.Surface((SCREEN_WIDTH, 45), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 130))
        self.screen.blit(panel, (0, 0))

        score_t  = self.font_small.render(
            f"Score: {self.monkey.get_score()}", True, YELLOW)
        level_t  = self.font_small.render(
            f"Level: {self.level} / 20", True, WHITE)
        hi_t     = self.font_small.render(
            f"Best: {self.high_score}", True, GOLD)
        ban_t    = self.font_small.render(
            f"Bananas: {self.monkey.bananas_collected}", True, YELLOW)

        self.screen.blit(score_t, (10, 10))
        self.screen.blit(level_t, (SCREEN_WIDTH//2 - 55, 10))
        self.screen.blit(hi_t,    (SCREEN_WIDTH - 145, 10))
        self.screen.blit(ban_t,   (SCREEN_WIDTH//2 + 110, 10))

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # show_menu()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_menu(self):
        while True:
            self.screen.fill(DARK_BG)

            # Title banner
            banner = pygame.Surface((SCREEN_WIDTH, 120))
            banner.fill((30, 30, 70))
            self.screen.blit(banner, (0, 70))

            # Decorative stars
            for sx, sy in [(60,30),(150,55),(700,25),(740,60),(770,35)]:
                pygame.draw.circle(self.screen, YELLOW, (sx, sy), 2)

            title = self.font_large.render("MONKEY ADVENTURE", True, YELLOW)
            sub   = self.font_small.render("Run, Jump & Collect Bananas!", True, WHITE)
            hs    = self.font_small.render(
                f"High Score: {self.high_score}", True, GOLD)

            self.screen.blit(title,
                (SCREEN_WIDTH//2 - title.get_width()//2, 82))
            self.screen.blit(sub,
                (SCREEN_WIDTH//2 - sub.get_width()//2,  148))
            self.screen.blit(hs,
                (SCREEN_WIDTH//2 - hs.get_width()//2,   182))

            # Monkey sprite on the left of the title
            if self.images["monkey"]:
                mk = pygame.transform.scale(self.images["monkey"], (55, 55))
                self.screen.blit(mk,
                    (SCREEN_WIDTH//2 - title.get_width()//2 - 65, 88))

            # Banana sprite on the right
            if self.images["banana"]:
                bn = pygame.transform.scale(self.images["banana"], (40, 48))
                self.screen.blit(bn,
                    (SCREEN_WIDTH//2 + title.get_width()//2 + 20, 90))

            self.btn_play.draw(self.screen)
            self.btn_instr.draw(self.screen)
            self.btn_exit.draw(self.screen)

            # Small icons on the buttons
            self._draw_icon(self.screen, "play",    self.btn_play.rect.left  + 28, self.btn_play.rect.centery)
            self._draw_icon(self.screen, "book",    self.btn_instr.rect.left + 28, self.btn_instr.rect.centery)
            self._draw_icon(self.screen, "x",       self.btn_exit.rect.left  + 28, self.btn_exit.rect.centery)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if self.btn_play.click(event):
                    return "play"
                if self.btn_instr.click(event):
                    return "instructions"
                if self.btn_exit.click(event):
                    self._quit()

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # show_instructions()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_instructions(self):
        lines = [
            ("HOW TO PLAY",                               self.font_medium, YELLOW),
            ("",                                           self.font_small,  WHITE),
            ("SPACE or UP ARROW  ->  Jump",                self.font_small,  WHITE),
            ("P  ->  Pause / Unpause",                     self.font_small,  WHITE),
            ("ESC  ->  Return to Main Menu",               self.font_small,  WHITE),
            ("",                                           self.font_small,  WHITE),
            ("Collect bananas  =  +10 points each",        self.font_small,  YELLOW),
            ("Avoid Fire, Rock and Spike obstacles!",      self.font_small,  (255,120,60)),
            ("",                                           self.font_small,  WHITE),
            ("Survive long enough to advance levels.",     self.font_small,  WHITE),
            ("Beat all 20 levels to win!",                 self.font_small,  GOLD),
            ("",                                           self.font_small,  WHITE),
            ("Level bonus = Level x 50 points",            self.font_tiny,   (180,180,180)),
        ]
        while True:
            self.screen.fill(DARK_BG)

            # Header bar
            pygame.draw.rect(self.screen, (30,30,70), (0, 0, SCREEN_WIDTH, 55))

            y = 15
            for text, font, colour in lines:
                surf = font.render(text, True, colour)
                self.screen.blit(surf,
                    (SCREEN_WIDTH//2 - surf.get_width()//2, y))
                y += font.size("A")[1] + 8

            self.btn_instr_back.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if self.btn_instr_back.click(event):
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # pause_game()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def pause_game(self):
        self._pause_music()   # freeze music while paused

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("-- PAUSED --", True, YELLOW)
        self.screen.blit(title,
            (SCREEN_WIDTH//2 - title.get_width()//2, 160))

        self.btn_resume.draw(self.screen)
        self.btn_menu.draw(self.screen)
        self.btn_quit.draw(self.screen)

        # Icons
        self._draw_icon(self.screen, "play",  self.btn_resume.rect.left + 28, self.btn_resume.rect.centery)
        self._draw_icon(self.screen, "home",  self.btn_menu.rect.left   + 28, self.btn_menu.rect.centery)
        self._draw_icon(self.screen, "x",     self.btn_quit.rect.left   + 28, self.btn_quit.rect.centery)

        pygame.display.flip()

        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self._resume_music()
                        return "resume"
                if self.btn_resume.click(event):
                    self._resume_music()
                    return "resume"
                if self.btn_menu.click(event):
                    self._stop_music()
                    return "menu"
                if self.btn_quit.click(event):
                    self._quit()

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # game_over()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def game_over(self):
        self._stop_music()
        self._play_sound("gameover")

        score = self.monkey.get_score()
        new_record = False
        if score > self.high_score:
            self.high_score = score
            self._save_high_score(self.high_score)
            new_record = True

        while True:
            self.screen.fill(DARK_RED)

            # Flashing top bar
            pygame.draw.rect(self.screen, (150, 0, 0),
                             (0, 0, SCREEN_WIDTH, 60))

            go_t = self.font_large.render("GAME OVER", True, (255, 80, 80))
            sc_t = self.font_medium.render(f"Score:  {score}", True, WHITE)
            hi_t = self.font_medium.render(f"Best:   {self.high_score}", True, GOLD)
            lv_t = self.font_small.render(
                f"You reached Level {self.level}", True, WHITE)

            self.screen.blit(go_t,
                (SCREEN_WIDTH//2 - go_t.get_width()//2, 10))
            self.screen.blit(sc_t,
                (SCREEN_WIDTH//2 - sc_t.get_width()//2, 175))
            self.screen.blit(hi_t,
                (SCREEN_WIDTH//2 - hi_t.get_width()//2, 218))
            self.screen.blit(lv_t,
                (SCREEN_WIDTH//2 - lv_t.get_width()//2, 268))

            if new_record:
                nr = self.font_medium.render("*** NEW HIGH SCORE! ***", True, YELLOW)
                self.screen.blit(nr,
                    (SCREEN_WIDTH//2 - nr.get_width()//2, 296))

            self.btn_retry.draw(self.screen)
            self.btn_back.draw(self.screen)

            self._draw_icon(self.screen, "refresh",
                            self.btn_retry.rect.left + 28, self.btn_retry.rect.centery)
            self._draw_icon(self.screen, "home",
                            self.btn_back.rect.left  + 28, self.btn_back.rect.centery)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if self.btn_retry.click(event):
                    return "retry"
                if self.btn_back.click(event):
                    return "menu"

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # show_victory()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_victory(self):
        self._stop_music()
        self._play_sound("levelup")

        score = self.monkey.get_score()
        if score > self.high_score:
            self.high_score = score
            self._save_high_score(self.high_score)

        while True:
            self.screen.fill(DARK_GRN)

            # Gold header bar
            pygame.draw.rect(self.screen, (180, 140, 0),
                             (0, 0, SCREEN_WIDTH, 60))

            lines = [
                self.font_large.render("*** YOU WIN! ***",              True, GOLD),
                self.font_medium.render("Congratulations!",              True, WHITE),
                self.font_medium.render("You completed all 20 levels!",  True, YELLOW),
                self.font_small.render(f"Final Score: {score}",          True, WHITE),
                self.font_small.render(
                    f"Bananas collected: {self.monkey.bananas_collected}", True, YELLOW),
            ]
            y = 70
            for surf in lines:
                self.screen.blit(surf,
                    (SCREEN_WIDTH//2 - surf.get_width()//2, y))
                y += surf.get_height() + 14

            self.btn_retry.draw(self.screen)
            self.btn_back.draw(self.screen)

            self._draw_icon(self.screen, "refresh",
                            self.btn_retry.rect.left + 28, self.btn_retry.rect.centery)
            self._draw_icon(self.screen, "home",
                            self.btn_back.rect.left  + 28, self.btn_back.rect.centery)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if self.btn_retry.click(event):
                    return "retry"
                if self.btn_back.click(event):
                    return "menu"

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # increase_level()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def increase_level(self):
        self.monkey.add_level_bonus(self.level)
        self.level += 1
        self.distance_counter = 0

        new_speed = self._base_speed()
        count     = self._obstacle_count()
        types     = ["fire", "rock", "spike"]

        while len(self.obstacles) < count:
            t = types[len(self.obstacles) % 3]
            self.obstacles.append(
                Obstacle(t, self.images[t], speed=new_speed))
        while len(self.obstacles) > count:
            self.obstacles.pop()

        for obs in self.obstacles:
            obs.set_speed(new_speed)
            obs.reset()
        for ban in self.bananas:
            ban.set_speed(new_speed)

        self._play_sound("levelup")
        self._show_level_flash()

    def _show_level_flash(self):
        for _ in range(90):
            self.screen.fill(DARK_BG)

            # Difficulty label
            if   self.level <= 5:  diff, colour = "EASY",   (80, 200, 80)
            elif self.level <= 10: diff, colour = "MEDIUM",  YELLOW
            elif self.level <= 15: diff, colour = "HARD",    ORANGE
            else:                  diff, colour = "EXPERT!", RED

            msg  = self.font_large.render(f"LEVEL  {self.level}!", True, YELLOW)
            sub  = self.font_medium.render("Get Ready!", True, WHITE)
            diff_s = self.font_small.render(diff, True, colour)

            self.screen.blit(msg,
                (SCREEN_WIDTH//2 - msg.get_width()//2,  180))
            self.screen.blit(sub,
                (SCREEN_WIDTH//2 - sub.get_width()//2,  248))
            self.screen.blit(diff_s,
                (SCREEN_WIDTH//2 - diff_s.get_width()//2, 288))

            pygame.display.flip()
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # check_collision()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def check_collision(self):
        monkey_rect = self.monkey.rect.inflate(-20, -20)

        for obs in self.obstacles:
            if monkey_rect.colliderect(obs.rect.inflate(-10, -10)):
                return True

        for ban in self.bananas:
            if monkey_rect.colliderect(ban.rect):
                self.monkey.collect_banana()
                self._play_sound("collect")
                ban.reset()

        return False

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _reset_game()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _reset_game(self):
        self.level            = 1
        self.distance_counter = 0
        self.bg_x1 = 0
        self.bg_x2 = SCREEN_WIDTH
        self.monkey.reset_position()
        self.monkey.set_score(0)
        self.monkey.bananas_collected = 0
        self.obstacles = [
            Obstacle("fire", self.images["fire"], speed=self._base_speed()),
        ]
        self.bananas = [
            Banana(self.images["banana"], speed=self._base_speed()),
            Banana(self.images["banana"], speed=self._base_speed()),
        ]

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _draw_progress_bar()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _draw_progress_bar(self):
        LEVEL_DISTANCE = 1800
        progress = min(self.distance_counter / LEVEL_DISTANCE, 1.0)
        bar_w    = int((SCREEN_WIDTH - 40) * progress)

        pygame.draw.rect(self.screen, GREY,
                         (20, SCREEN_HEIGHT - 20, SCREEN_WIDTH - 40, 12),
                         border_radius=6)
        pygame.draw.rect(self.screen, GREEN,
                         (20, SCREEN_HEIGHT - 20, bar_w, 12),
                         border_radius=6)
        label = self.font_tiny.render(
            f"Level {self.level} Progress", True, WHITE)
        self.screen.blit(label, (22, SCREEN_HEIGHT - 36))

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # play_game() --- main gameplay loop
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def play_game(self):
        LEVEL_DISTANCE = 1800
        self._start_music()   # begin looping background music

        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.monkey.run()
                        self._play_sound("jump")
                    if event.key == pygame.K_p:
                        result = self.pause_game()
                        if result == "menu":
                            return "menu"
                    if event.key == pygame.K_ESCAPE:
                        return "menu"

            self.monkey.update()

            for obs in self.obstacles:
                obs.move()
                if obs.is_off_screen():
                    obs.reset()

            for ban in self.bananas:
                ban.move()
                if ban.is_off_screen():
                    ban.reset()

            self.distance_counter += 1
            if self.distance_counter >= LEVEL_DISTANCE:
                if self.level >= 20:
                    return self.show_victory()
                else:
                    self.increase_level()

            if self.check_collision():
                return self.game_over()

            self._draw_background()

            for ban in self.bananas:
                ban.draw(self.screen)
            for obs in self.obstacles:
                obs.draw(self.screen)

            self.monkey.draw(self.screen)
            self.show_score()
            self._draw_progress_bar()

            pygame.display.flip()

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # run() --- master loop
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def run(self):
        while True:
            action = self.show_menu()
            if action == "instructions":
                self.show_instructions()
                continue
            if action == "play":
                self._reset_game()
                while True:
                    result = self.play_game()
                    if result == "retry":
                        self._reset_game()
                    else:
                        break

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # _quit()
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _quit(self):
        pygame.quit()
        sys.exit()

import tkinter as tk
import random
import math
import os
import sys
import json
from PIL import Image, ImageTk, ImageSequence

WIDTH = 900
HEIGHT = 600
FPS = 60

PLAYER_SIZE = 90
SAVE_FILE = "save.json"
SETTINGS_FILE = "settings.json"


def resource_path(name):
    """Ищет файл рядом со скриптом или внутри .exe (PyInstaller)."""
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in ("", ".png", ".gif", ".jpg", ".jpeg", ".webp"):
        path = os.path.join(base_dir, name + ext) if ext else os.path.join(base_dir, name)
        if os.path.exists(path):
            return path
    return None


def user_data_path(filename):
    """Путь для сохранений — всегда рядом с .exe / .py."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


THEMES = {
    "dark": {
        "menu_bg": "#0e1a2a",
        "accent_hover": "#ffffff",
        "btn_play": "#1f4e6b",
        "btn_danger": "#6b2e2e",
        "btn_cancel": "#1f4e6b",
        "text": "#ffffff",
        "text_dim": "#7aa8c8",
        "hud": "#8ff0ff",
        "overlay": "#000000",
    },
    "light": {
        "menu_bg": "#ffffff",
        "accent_hover": "#000000",
        "btn_play": "#3a7fb5",
        "btn_danger": "#b53a3a",
        "btn_cancel": "#3a7fb5",
        "text": "#0e1a2a",
        "text_dim": "#5a6a80",
        "hud": "#1f4e6b",
        "overlay": "#ffffff",
    },
}

COLOR_PRESETS = [
    ("#8ff0ff", "Голубой"),
    ("#ffe066", "Жёлтый"),
    ("#ff5a5a", "Красный"),
    ("#8aff8a", "Зелёный"),
    ("#d88aff", "Фиолетовый"),
    ("#ff8ad8", "Розовый"),
    ("#ffa54a", "Оранжевый"),
    ("#ffffff", "Белый"),
]

WALL_TOP = 110
FLOOR_TOP = 470

CAGE_X = 70
CAGE_Y = 390
CAGE_W = 160
CAGE_H = 110

DOOR_X = 220
DOOR_Y = 240
DOOR_W = 90
DOOR_H = 230

STORY_DELAY = 30 * FPS
KROLO_SCENE_DURATION = 15 * FPS

CASTLE_DOOR_W = 130
CASTLE_DOOR_H = 200

SEGMENT_LENGTH = 2400

BOSS_DURATION = 60 * FPS

BREAK_DURATION = 4 * FPS


class SkibidiGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Скибиди ТРП: Путешествие по мультивселенным")
        self.root.resizable(False, False)
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0, bg="black")
        self.canvas.pack()

        self.keys = set()
        self.state = "menu"
        self.loading_progress = 0
        self.player_x = WIDTH // 2
        self.player_y = 520
        self.player_speed = 5
        self.tick = 0
        self.play_time = 0
        self.autosave_timer = 0

        self.theme_name = "dark"
        self.accent_color = "#8ff0ff"

        self.mellchar_img = None
        self.mellchar_dialog_img = None
        self.mellchar2_img = None
        self.mellchar2_dialog_img = None
        self.mellchar3_img = None
        self.mellchar3_dialog_img = None
        self.mellchar4_img = None
        self.mellchar4_dialog_img = None
        self.mellchar5_img = None
        self.mellchar5_dialog_img = None
        self.mellloadback_img = None
        self.load_mellchar()
        self.load_mellchar2()
        self.load_mellchar3()
        self.load_mellchar4()
        self.load_mellchar5()
        self.load_mellloadback()
        self.load_settings()

        self.hamster_fed = 0
        self.hamster_hunger = 0
        self.hamster_joy = 0
        self.hamster_bounce = 0

        self.hint_text = ""
        self.hint_timer = 0

        self.title_active = False
        self.title_timer = 0
        self.title_text = "Квартира Крола"
        self.title_callback = None

        self.story_timer = 0
        self.story_stage = 0
        self.location = "krol_room"
        self.door_cooldown = 0

        self.tunnel_stage = 0
        self.tunnel_x = 0

        self.door_code = random.randint(10, 99)
        self.code_input = ""
        self.code_solved = False
        self.code_attempts = 0
        self.code_hint_shown = False

        self.post_terminal_dialogue_shown = False

        self.minigame_score = 0
        self.minigame_target = 50
        self.minigame_black_dots = []
        self.minigame_red_dots = []
        self.minigame_spawn_timer = 0
        self.minigame_red_spawn_timer = 0
        self.minigame_done = False
        self.minigame_intro_shown = False

        self.has_key = False
        self.key_inserted = False

        self.boss_active = False
        self.boss_timer = 0
        self.boss_swords = []
        self.boss_sword_spawn_timer = 20
        self.boss_isa_intro_done = False
        self.boss_finished = False

        self.post_boss_phase = 0
        self.post_boss_timer = 0
        self.post_boss_actors_visible = False
        self.isa_visible = False

        self.break_timer = 0
        self.break_phase = 0
        self.break_flash = 0

        self.credits_timer = 0
        self.credits_scroll = HEIGHT + 100

        self.final_dialogue_shown = False

        self.dialogue_active = False
        self.dialogue_queue = []
        self.dialogue_current = ""
        self.dialogue_char_index = 0
        self.dialogue_char_timer = 0
        self.dialogue_speaker = "Крол"
        self.dialogue_done_callback = None

        self.visited_empty_room = False
        self.visited_tartenok_room = False
        self.tartenok_talked = False

        self.objective = None
        self.door_opened = False
        self.room_completed = False
        self.black_screen = False
        self.black_timer = 0
        self.scream_shown = False

        self.cutscene_active = False
        self.cutscene_frames = []
        self.cutscene_frame_index = 0
        self.cutscene_frame_timer = 0
        self.cutscene_total_timer = 0
        self.cutscene_frame_delay = 999999
        self.cutscene_duration = 0
        self.cutscene_callback = None
        self.cutscene_has_file = False

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        self.confirm_btn_rect = None
        self.confirm_btn_text = None
        self.confirm_progress_rect = None
        self.confirm_btn_x = 0
        self.confirm_btn_y = 0
        self.confirm_btn_w = 200
        self.confirm_btn_h = 60
        self.confirm_escape_time = None
        self.confirm_escape_duration = 5 * 1000
        self.confirm_hold_start = None
        self.confirm_hold_required = 3000
        self.confirm_hold_progress = 0

        self.no_btn_rect = None
        self.no_btn_text = None

        self.show_menu()

    def theme(self):
        return THEMES[self.theme_name]

    def settings_path(self):
        return user_data_path(SETTINGS_FILE)

    def save_settings(self):
        try:
            with open(self.settings_path(), "w", encoding="utf-8") as f:
                json.dump({"theme": self.theme_name, "accent_color": self.accent_color}, f)
        except Exception as e:
            print("Ошибка сохранения настроек:", e)

    def load_settings(self):
        if not os.path.exists(self.settings_path()):
            return
        try:
            with open(self.settings_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.theme_name = data.get("theme", "dark")
            if self.theme_name not in THEMES:
                self.theme_name = "dark"
            self.accent_color = data.get("accent_color", "#8ff0ff")
        except Exception as e:
            print("Ошибка загрузки настроек:", e)

    def save_path(self):
        return user_data_path(SAVE_FILE)

    def has_save(self):
        return os.path.exists(self.save_path())

    def save_game(self):
        data = {
            "player_x": self.player_x,
            "player_y": self.player_y,
            "play_time": self.play_time,
            "hamster_fed": self.hamster_fed,
            "hamster_hunger": self.hamster_hunger,
            "door_opened": self.door_opened,
            "room_completed": self.room_completed,
            "story_stage": self.story_stage,
            "location": self.location,
            "visited_empty_room": self.visited_empty_room,
            "visited_tartenok_room": self.visited_tartenok_room,
            "tartenok_talked": self.tartenok_talked,
            "tunnel_stage": self.tunnel_stage,
            "door_code": self.door_code,
            "code_solved": self.code_solved,
            "post_terminal_dialogue_shown": self.post_terminal_dialogue_shown,
            "minigame_done": self.minigame_done,
            "has_key": self.has_key,
            "key_inserted": self.key_inserted,
            "boss_finished": self.boss_finished,
            "post_boss_phase": self.post_boss_phase,
            "isa_visible": self.isa_visible,
            "final_dialogue_shown": self.final_dialogue_shown,
        }
        try:
            with open(self.save_path(), "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            print("Ошибка сохранения:", e)

    def load_game(self):
        try:
            with open(self.save_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.player_x = data.get("player_x", WIDTH // 2)
            self.player_y = data.get("player_y", 520)
            self.play_time = data.get("play_time", 0)
            self.hamster_fed = data.get("hamster_fed", 0)
            self.hamster_hunger = data.get("hamster_hunger", 0)
            self.door_opened = data.get("door_opened", False)
            self.room_completed = data.get("room_completed", False)
            self.story_stage = data.get("story_stage", 0)
            self.location = data.get("location", "krol_room")
            self.visited_empty_room = data.get("visited_empty_room", False)
            self.visited_tartenok_room = data.get("visited_tartenok_room", False)
            self.tartenok_talked = data.get("tartenok_talked", False)
            self.tunnel_stage = data.get("tunnel_stage", 0)
            self.door_code = data.get("door_code", random.randint(10, 99))
            self.code_solved = data.get("code_solved", False)
            self.post_terminal_dialogue_shown = data.get("post_terminal_dialogue_shown", False)
            self.minigame_done = data.get("minigame_done", False)
            self.has_key = data.get("has_key", False)
            self.key_inserted = data.get("key_inserted", False)
            self.boss_finished = data.get("boss_finished", False)
            self.post_boss_phase = data.get("post_boss_phase", 0)
            self.isa_visible = data.get("isa_visible", False)
            self.final_dialogue_shown = data.get("final_dialogue_shown", False)
            return True
        except Exception as e:
            print("Ошибка загрузки:", e)
            return False

    def delete_save(self):
        try:
            if os.path.exists(self.save_path()):
                os.remove(self.save_path())
        except Exception as e:
            print("Ошибка удаления сохранения:", e)

    def load_mellchar(self):
        path = resource_path("mellchar")
        if path:
            try:
                pil = Image.open(path).convert("RGBA")
                pil = pil.resize((PLAYER_SIZE, PLAYER_SIZE), Image.LANCZOS)
                self.mellchar_img = ImageTk.PhotoImage(pil)

                pil2 = Image.open(path).convert("RGBA")
                pil2 = pil2.resize((100, 100), Image.LANCZOS)
                self.mellchar_dialog_img = ImageTk.PhotoImage(pil2)
            except Exception as e:
                print("Ошибка загрузки mellchar:", e)

    def load_mellchar2(self):
        path = resource_path("mellchar2")
        if path:
            try:
                pil = Image.open(path).convert("RGBA")
                pil = pil.resize((PLAYER_SIZE, PLAYER_SIZE), Image.LANCZOS)
                self.mellchar2_img = ImageTk.PhotoImage(pil)

                pil2 = Image.open(path).convert("RGBA")
                pil2 = pil2.resize((100, 100), Image.LANCZOS)
                self.mellchar2_dialog_img = ImageTk.PhotoImage(pil2)
            except Exception as e:
                print("Ошибка загрузки mellchar2:", e)

    def load_mellchar3(self):
        path = resource_path("mellchar3")
        if path:
            try:
                pil = Image.open(path).convert("RGBA")
                pil = pil.resize((PLAYER_SIZE, PLAYER_SIZE), Image.LANCZOS)
                self.mellchar3_img = ImageTk.PhotoImage(pil)

                pil2 = Image.open(path).convert("RGBA")
                pil2 = pil2.resize((100, 100), Image.LANCZOS)
                self.mellchar3_dialog_img = ImageTk.PhotoImage(pil2)
            except Exception as e:
                print("Ошибка загрузки mellchar3:", e)

    def load_mellchar4(self):
        path = resource_path("mellchar4")
        if path:
            try:
                pil = Image.open(path).convert("RGBA")
                pil = pil.resize((PLAYER_SIZE, PLAYER_SIZE), Image.LANCZOS)
                self.mellchar4_img = ImageTk.PhotoImage(pil)

                pil2 = Image.open(path).convert("RGBA")
                pil2 = pil2.resize((100, 100), Image.LANCZOS)
                self.mellchar4_dialog_img = ImageTk.PhotoImage(pil2)
            except Exception as e:
                print("Ошибка загрузки mellchar4:", e)

    def load_mellchar5(self):
        path = resource_path("mellchar5")
        if path:
            try:
                pil = Image.open(path).convert("RGBA")
                pil = pil.resize((PLAYER_SIZE, PLAYER_SIZE), Image.LANCZOS)
                self.mellchar5_img = ImageTk.PhotoImage(pil)

                pil2 = Image.open(path).convert("RGBA")
                pil2 = pil2.resize((100, 100), Image.LANCZOS)
                self.mellchar5_dialog_img = ImageTk.PhotoImage(pil2)
            except Exception as e:
                print("Ошибка загрузки mellchar5:", e)

    def load_mellloadback(self):
        path = resource_path("mellloadback")
        if path:
            try:
                pil = Image.open(path).convert("RGBA")
                pil = pil.resize((WIDTH, HEIGHT), Image.LANCZOS)
                self.mellloadback_img = ImageTk.PhotoImage(pil)
            except Exception as e:
                print("Ошибка загрузки mellloadback:", e)

    def on_key_press(self, event):
        self.keys.add(event.keysym.lower())
        key = event.keysym.lower()

        if self.state == "game":
            if self.cutscene_active:
                if key in ("space", "return", "escape", "e", "у", "cyrillic_em", "cyrillic_u"):
                    self.skip_cutscene()
                return
            if self.title_active:
                if key in ("space", "return", "escape", "e", "у", "cyrillic_em", "cyrillic_u"):
                    self.skip_title()
                return

            if self.location == "credits":
                if key in ("space", "return", "escape", "e", "у", "cyrillic_em", "cyrillic_u"):
                    self.show_menu()
                return

            if self.location == "tunnel_terminal" and not self.code_solved:
                if key in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                    if len(self.code_input) < 2:
                        self.code_input += key
                    return
                elif key in ("backspace",):
                    self.code_input = self.code_input[:-1]
                    return
                elif key in ("return", "enter", "kp_enter"):
                    self.submit_code()
                    return

            if (self.location == "key_door_room"
                    and self.has_key
                    and not self.key_inserted
                    and not self.dialogue_active
                    and key in ("e", "у", "cyrillic_em", "cyrillic_u", "return", "space")):
                self.insert_key()
                return

            if key == "escape":
                self.save_game()
                self.show_menu()
            elif self.dialogue_active and key in ("space", "return", "e", "у", "cyrillic_em", "cyrillic_u"):
                self.advance_dialogue()

        elif self.state == "confirm" and key == "escape":
            self.close_confirm()
        elif self.state == "settings" and key == "escape":
            self.show_menu()

    def on_key_release(self, event):
        self.keys.discard(event.keysym.lower())

    def clear(self):
        self.canvas.delete("all")

    def submit_code(self):
        if len(self.code_input) != 2:
            self.show_hint("Введи 2 цифры и нажми Enter")
            return
        self.code_attempts += 1
        try:
            entered = int(self.code_input)
        except:
            self.code_input = ""
            return

        if entered == self.door_code:
            self.code_solved = True
            self.code_input = ""
            self.save_game()
            self.show_hint("ДВЕРЬ ОТКРЫТА!")
        else:
            self.code_input = ""
            self.show_hint("Неверный код. Попробуй снова.")

    def insert_key(self):
        self.key_inserted = True
        self.save_game()
        self.show_hint("Ключ вставлен. Дверь открывается...")
        self.root.after(800, self.start_isa_dialogue)

    def start_isa_dialogue(self):
        self.boss_isa_intro_done = True
        self.isa_visible = True
        self.start_dialogue([
            ("Крол", "о, Иса!!! привет!!"),
            ("Иса", "ты кто?"),
            ("Крол", "а, точно"),
            ("Крол", "(рассказал)"),
            ("Иса", "что только не придумают бурвы для захвата замка."),
            ("Крол", "ч-что?"),
        ], self.after_isa_intro_dialogue)

    def after_isa_intro_dialogue(self):
        self.dialogue_active = False
        self.dialogue_queue = []
        self.dialogue_done_callback = None
        self.start_boss_fight()

    def start_boss_fight(self):
        self.location = "boss_isa"
        self.boss_active = True
        self.boss_timer = 0
        self.boss_swords = []
        self.boss_sword_spawn_timer = 20
        self.player_x = 150
        self.player_y = HEIGHT // 2
        self.dialogue_active = False
        self.dialogue_queue = []
        self.dialogue_done_callback = None
        self.save_game()

    def boss_respawn(self):
        self.player_x = 150
        self.player_y = HEIGHT // 2
        self.boss_swords = []

    def spawn_boss_sword(self):
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            sx = -30
            sy = random.randint(100, HEIGHT - 100)
            tx = random.randint(WIDTH // 2, WIDTH - 100)
            ty = random.randint(100, HEIGHT - 100)
        elif side == "right":
            sx = WIDTH + 30
            sy = random.randint(100, HEIGHT - 100)
            tx = random.randint(100, WIDTH // 2)
            ty = random.randint(100, HEIGHT - 100)
        elif side == "top":
            sx = random.randint(100, WIDTH - 100)
            sy = -30
            tx = random.randint(100, WIDTH - 100)
            ty = random.randint(HEIGHT // 2, HEIGHT - 100)
        else:
            sx = random.randint(100, WIDTH - 100)
            sy = HEIGHT + 30
            tx = random.randint(100, WIDTH - 100)
            ty = random.randint(100, HEIGHT // 2)

        if random.random() < 0.4:
            tx = self.player_x
            ty = self.player_y

        angle = math.atan2(ty - sy, tx - sx)
        speed = random.uniform(4.5, 7.5)

        self.boss_swords.append({
            "x": sx, "y": sy,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "angle": angle,
            "life": 300,
        })

    def update_boss_fight(self):
        if self.location != "boss_isa":
            return
        if not self.boss_active:
            return
        if self.dialogue_active:
            return

        self.boss_timer += 1
        self.boss_sword_spawn_timer += 1

        if self.boss_sword_spawn_timer >= 22:
            self.boss_sword_spawn_timer = 0
            self.spawn_boss_sword()
            if random.random() < 0.3:
                self.spawn_boss_sword()

        new_swords = []
        for s in self.boss_swords:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["life"] -= 1

            if s["life"] <= 0:
                continue
            if s["x"] < -80 or s["x"] > WIDTH + 80 or s["y"] < -80 or s["y"] > HEIGHT + 80:
                continue

            if math.hypot(self.player_x - s["x"], self.player_y - s["y"]) < 45:
                self.boss_respawn()
                return

            new_swords.append(s)

        self.boss_swords = new_swords

        if self.boss_timer >= BOSS_DURATION:
            self.boss_active = False
            self.boss_finished = True
            self.boss_swords = []
            self.post_boss_phase = 0
            self.save_game()
            self.start_dialogue([
                ("Крол", "..."),
                ("Крол", "куда он делся?!"),
                ("Крол", "и что это вообще было.."),
            ], self.after_boss_dialogue)

    def after_boss_dialogue(self):
        self.post_boss_phase = 1
        self.post_boss_timer = 0
        self.post_boss_actors_visible = True
        self.isa_visible = False
        self.save_game()

        self.root.after(1500, self.start_ashot_just_dialogue)

    def start_ashot_just_dialogue(self):
        self.start_dialogue([
            ("Крол", "вы.. ашот, джаст... это вы убили ису?"),
            ("Ашот", "он не умер, мы телепортировали его подальше."),
            ("Крол", "спасибо... а вы мне верите?"),
            ("Джаст", "да, мы уже встречали как к нам приходил кто то с другой вселенной"),
            ("Крол", "как вы узнали, что я тоже с другой?"),
            ("Ашот", "подслушали"),
            ("Крол", "понятно.. а как мне попасть назад?"),
            ("Джаст", "прошлый исчез после того как увидел себя"),
            ("Крол", "странно, разве это не создаст парадокс?"),
            ("Ашот", "пара-ра-до.. что?"),
            ("Крол", "а.. ну.. забей"),
        ], self.after_ashot_just_dialogue)

    def after_ashot_just_dialogue(self):
        self.start_dialogue([
            ("Крол", "(мне надо найти.. себя, вариантов нет, надо идти к двери)"),
        ], self.start_final_phase)

    def start_final_phase(self):
        self.post_boss_phase = 2
        self.post_boss_actors_visible = False
        self.isa_visible = False
        self.save_game()
        self.show_hint("Иди к двери →")

    def start_universe_break(self):
        self.location = "universe_break"
        self.break_timer = 0
        self.break_phase = 0
        self.break_flash = 0
        self.save_game()

    def finish_universe_break(self):
        self.location = "krol_room"
        self.player_x = WIDTH // 2
        self.player_y = FLOOR_TOP + 30
        self.door_cooldown = 90
        self.break_timer = 0
        self.black_screen = False
        self.save_game()
        self.start_title("Квартира Крола", self.after_return_home)

    def after_return_home(self):
        if self.final_dialogue_shown:
            return
        self.final_dialogue_shown = True
        self.save_game()
        self.start_dialogue([
            ("Крол", "... я... многое должен обдумать... я дома... дома.."),
            ("Крол", "так. похоже, я реально увидел себя и телепортировался назад."),
            ("Крол", "но почему другой я выглядел как я сейчас, если все остальные там старого стиля... хххмммм."),
            ("Крол", "может, я увидел в нем себя и мой мозг заменил его на нового.. да, навернре так.."),
            ("Крол", "не понятно только почемму там не было семена, зендера и воздуха, ну ладно, не весь замок прошел, можт где то были."),
            ("Крол", "они говорили, что уже видели кого то с другой вселенной.. надо было спросить кого.."),
            ("Крол", "стоп, их текущие виды были до появления семена и воздуха, это поясняет их отсутствие,"),
            ("Крол", "а зендер.. где зендер.. хм.. зендер любил ливать, может, в той вселенной он покинул замок.."),
            ("Крол", "ладно, вернемся к тому кто пришел с моей вселенной.. почему же я не спросил кто это был.. ну.."),
            ("Крол", "стоп.. если это старое стрп.. то там был сускет.............."),
            ("Крол", "может, он и пришел к ним и увидел себя, но вернулся не назад, а попал в другую вселенную?"),
            ("Крол", "а где сус кет сам там.. может, он уже ушел оттуда? там же тоже течет время..."),
            ("Крол", "... сложно.. надо отдохнуть"),
        ], self.start_credits)

    def start_credits(self):
        self.location = "credits"
        self.credits_timer = 0
        self.credits_scroll = HEIGHT + 100
        self.save_game()

    def draw_credits(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", outline="")

        lines = [
            ("─" * 30, "#444444", 20),
            ("", "", 10),
            ("КОДИЛ", "#ffe066", 28),
            ("Крол", "#ffffff", 16),
            ("", "", 20),
            ("МОНТАЖИЛ", "#ffe066", 28),
            ("Крол", "#ffffff", 16),
            ("", "", 20),
            ("КАТ-СЦЕНА", "#ffe066", 28),
            ("Крол", "#ffffff", 16),
            ("", "", 20),
            ("СЮЖЕТ", "#ffe066", 28),
            ("Крол", "#ffffff", 16),
            ("", "", 20),
            ("ОСОБАЯ БЛАГОДАРНОСТЬ", "#ffe066", 22),
            ("Крол", "#ffffff", 16),
            ("", "", 20),
            ("ГРАФИКА", "#ffe066", 22),
            ("Крол", "#ffffff", 16),
            ("", "", 20),
            ("ЗВУК", "#ffe066", 22),
            ("Крол", "#ffffff", 16),
            ("", "", 20),
            ("ИДЕЯ", "#ffe066", 22),
            ("Крол", "#ffffff", 16),
            ("", "", 20),
            ("РЕЖИССЁР", "#ffe066", 22),
            ("Крол", "#ffffff", 16),
            ("", "", 40),
            ("В ГЛАВНЫХ РОЛЯХ", "#ffe066", 22),
            ("Крол", "#ffffff", 16),
            ("Иса", "#8a8a9a", 14),
            ("Тартенок", "#8a8a9a", 14),
            ("Ашот", "#8a8a9a", 14),
            ("Джаст", "#8a8a9a", 14),
            ("Хомяк", "#8a8a9a", 14),
            ("Степан", "#8a8a9a", 14),
            ("", "", 40),
            ("─" * 30, "#444444", 20),
            ("", "", 20),
            ("2026", "#ffffff", 20),
            ("СЕНТЯБРЬ", "#8a8a9a", 16),
            ("", "", 60),
            ("КОНЕЦ ПЕРВОЙ ГЛАВЫ", "#8ff0ff", 20),
            ("", "", 100),
        ]

        y = self.credits_scroll
        for text, color, size in lines:
            if 200 < y < HEIGHT - 40 and text:
                self.canvas.create_text(WIDTH // 2, y,
                                        text=text,
                                        fill=color,
                                        font=("Courier New", size, "bold"))
            y += size + 12

        # затемнение сверху и снизу, чтобы текст выезжал из черноты
        self.canvas.create_rectangle(0, 0, WIDTH, 55, fill="#000000", outline="")
        self.canvas.create_rectangle(0, HEIGHT - 40, WIDTH, HEIGHT, fill="#000000", outline="")

        # фиксированный заголовок сверху
        self.canvas.create_text(WIDTH // 2, 60,
                                text="ГЛАВА 1",
                                fill="#8a8a9a", font=("Courier New", 16, "bold"))
        self.canvas.create_text(WIDTH // 2, 95,
                                text="СКИБИДИ ТРП",
                                fill="#8ff0ff", font=("Impact", 36, "bold"))
        self.canvas.create_text(WIDTH // 2, 135,
                                text="Путешествие по мультивселенным",
                                fill="#ffffff", font=("Courier New", 16, "bold"))
        self.canvas.create_text(WIDTH // 2, 165,
                                text="Замок СТРП",
                                fill="#c88aff", font=("Courier New", 14, "bold"))
        self.canvas.create_line(200, 190, WIDTH - 200, 190, fill="#444444", width=1)

        self.canvas.create_text(WIDTH - 20, HEIGHT - 20,
                                text="[ПРОБЕЛ] пропустить титры",
                                fill="#444444", font=("Courier New", 10),
                                anchor="se")

    def draw_universe_break(self):
        if self.location != "universe_break":
            return

        self.break_timer += 1
        t = self.break_timer

        palette = ["#1a0a2a", "#2a0a1a", "#0a1a2a", "#2a1a0a", "#0a2a1a", "#1a0a0a"]
        idx = (t // 3) % len(palette)
        bg_color = palette[idx]
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=bg_color, outline="")

        for i in range(0, HEIGHT, 20):
            if random.random() < 0.3:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                self.canvas.create_line(0, i, WIDTH, i,
                                        fill=f"#{r:02x}{g:02x}{b:02x}",
                                        width=random.randint(1, 3))

        for _ in range(random.randint(3, 8)):
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(0, HEIGHT)
            w = random.randint(50, 400)
            h = random.randint(20, 150)
            colors = ["#ff2b2b", "#2bff2b", "#2b2bff", "#ffff2b", "#ff2bff", "#2bffff", "#ffffff"]
            c = random.choice(colors)
            self.canvas.create_rectangle(x1, y1, x1 + w, y1 + h,
                                         fill=c, outline="", stipple="gray50")

        doubles = [
            (WIDTH // 2, HEIGHT // 2, 1.0),
            (WIDTH // 2 - 200, HEIGHT // 2 - 60, 0.7),
            (WIDTH // 2 + 200, HEIGHT // 2 + 40, 0.8),
            (WIDTH // 2 - 100, HEIGHT // 2 + 120, 0.6),
            (WIDTH // 2 + 80, HEIGHT // 2 - 130, 0.65),
        ]

        for i, (dx, dy, scale) in enumerate(doubles):
            wobble_x = math.sin(t * 0.15 + i) * 15
            wobble_y = math.cos(t * 0.18 + i) * 10
            px = dx + wobble_x
            py = dy + wobble_y

            if self.mellchar_img is not None:
                self.canvas.create_image(px, py, image=self.mellchar_img)
            else:
                s = int(PLAYER_SIZE * scale)
                self.canvas.create_rectangle(px - s // 2, py - s // 2,
                                             px + s // 2, py + s // 2,
                                             fill="#e74c3c", outline="#000", width=2)

        if t > 30:
            for i, ch in enumerate("ЧТО ЭТО"):
                wobble = math.sin(t * 0.3 + i) * 30
                self.canvas.create_text(WIDTH // 2 - 200 + i * 60 + wobble,
                                        100 + math.cos(t * 0.2 + i) * 20,
                                        text=ch,
                                        fill=random.choice(["#ff2b2b", "#ffffff", "#2b2bff"]),
                                        font=("Courier New", random.randint(24, 40), "bold"))

        half = BREAK_DURATION // 2
        if t > half:
            progress = (t - half) / half
            progress = min(1.0, progress)
            alpha_int = int(progress * 255)
            if alpha_int > 0:
                self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT,
                                             fill=f"#{alpha_int:02x}{alpha_int:02x}{alpha_int:02x}",
                                             outline="")

        if t >= BREAK_DURATION:
            self.finish_universe_break()

    def update_universe_break(self):
        if self.location != "universe_break":
            return

    def draw_boss_fight(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#12060a", outline="")

        for i in range(0, HEIGHT, 50):
            shade = 40 + int(10 * math.sin(i * 0.1))
            self.canvas.create_line(0, i, WIDTH, i, fill=f"#{shade:02x}{shade // 2:02x}{shade // 2:02x}", width=1)
        for j in range(0, WIDTH, 50):
            shade = 40 + int(10 * math.sin(j * 0.1))
            self.canvas.create_line(j, 0, j, HEIGHT, fill=f"#{shade:02x}{shade // 2:02x}{shade // 2:02x}", width=1)

        if self.isa_visible:
            isa_x = WIDTH - 180
            isa_y = 200
            if self.mellchar3_img is not None:
                self.canvas.create_image(isa_x, isa_y, image=self.mellchar3_img)
            else:
                s = PLAYER_SIZE
                self.canvas.create_rectangle(isa_x - s // 2, isa_y - s // 2,
                                             isa_x + s // 2, isa_y + s // 2,
                                             fill="#ff3a5a", outline="#000", width=2)
                self.canvas.create_text(isa_x, isa_y, text="ИСА",
                                        fill="#fff", font=("Courier New", 16, "bold"))

        if self.post_boss_actors_visible:
            ashot_x = WIDTH - 220
            ashot_y = 220
            just_x = WIDTH - 100
            just_y = 220

            if self.mellchar4_img is not None:
                self.canvas.create_image(ashot_x, ashot_y, image=self.mellchar4_img)
            else:
                s = PLAYER_SIZE
                self.canvas.create_rectangle(ashot_x - s // 2, ashot_y - s // 2,
                                             ashot_x + s // 2, ashot_y + s // 2,
                                             fill="#8aff8a", outline="#000", width=2)
                self.canvas.create_text(ashot_x, ashot_y, text="АШОТ",
                                        fill="#000", font=("Courier New", 14, "bold"))

            if self.mellchar5_img is not None:
                self.canvas.create_image(just_x, just_y, image=self.mellchar5_img)
            else:
                s = PLAYER_SIZE
                self.canvas.create_rectangle(just_x - s // 2, just_y - s // 2,
                                             just_x + s // 2, just_y + s // 2,
                                             fill="#8ff0ff", outline="#000", width=2)
                self.canvas.create_text(just_x, just_y, text="ДЖАСТ",
                                        fill="#000", font=("Courier New", 14, "bold"))

        if self.post_boss_phase == 2 and not self.post_boss_actors_visible:
            door_x1 = WIDTH - 180
            door_y1 = 120
            door_x2 = WIDTH - 60
            door_y2 = 320

            pulse = abs(math.sin(self.tick * 0.08))
            outline_color = f"#{int(100 + pulse * 155):02x}{int(100 + pulse * 155):02x}ff"
            self.canvas.create_rectangle(door_x1, door_y1, door_x2, door_y2,
                                         fill="#0a0a12", outline=outline_color, width=4)

            cx = (door_x1 + door_x2) // 2
            cy = (door_y1 + door_y2) // 2
            for r, col in [(60, "#1a1a3a"), (45, "#2a1a4a"), (30, "#3a2a6a"), (15, "#5a3a9a")]:
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                        fill=col, outline="")

            self.canvas.create_text(cx, door_y1 - 20,
                                    text="ДВЕРЬ",
                                    fill=outline_color, font=("Courier New", 14, "bold"))

        self.draw_player()

        for s in self.boss_swords:
            x1 = s["x"] - math.cos(s["angle"]) * 22
            y1 = s["y"] - math.sin(s["angle"]) * 22
            x2 = s["x"] + math.cos(s["angle"]) * 22
            y2 = s["y"] + math.sin(s["angle"]) * 22
            self.canvas.create_line(x1, y1, x2, y2, fill="#e8e8f0", width=6)
            self.canvas.create_line(x1, y1, x2, y2, fill="#ffffff", width=2)
            hx = s["x"] - math.cos(s["angle"]) * 26
            hy = s["y"] - math.sin(s["angle"]) * 26
            self.canvas.create_oval(hx - 4, hy - 4, hx + 4, hy + 4,
                                    fill="#8a6a00", outline="#000")

        if self.boss_active:
            self.canvas.create_text(WIDTH // 2, HEIGHT - 45,
                                    text="я не могу сражаться со своим другом...",
                                    fill="#ffffff", font=("Courier New", 16, "bold"))

    def start_minigame(self):
        self.location = "minigame"
        self.minigame_score = 0
        self.minigame_done = False
        self.minigame_black_dots = []
        self.minigame_red_dots = []
        self.minigame_spawn_timer = 0
        self.minigame_red_spawn_timer = 0
        self.save_game()

        if not self.minigame_intro_shown:
            self.minigame_intro_shown = True
            self.start_dialogue([
                ("Крол", "это что и почему тут столько головоломок... ладно, щас сделаю.."),
            ], None)

    def spawn_black_dot(self):
        x = random.randint(80, WIDTH - 80)
        y = random.randint(120, HEIGHT - 80)
        self.minigame_black_dots.append({"x": x, "y": y, "r": 22, "life": 240})

    def spawn_red_dot(self):
        x = random.randint(80, WIDTH - 80)
        y = random.randint(120, HEIGHT - 80)
        self.minigame_red_dots.append({"x": x, "y": y, "r": 24, "life": 180})

    def update_minigame(self):
        if self.dialogue_active:
            return
        if self.minigame_done:
            return

        self.minigame_spawn_timer += 1
        self.minigame_red_spawn_timer += 1

        if self.minigame_spawn_timer >= 12 and len(self.minigame_black_dots) < 12:
            self.minigame_spawn_timer = 0
            self.spawn_black_dot()

        if self.minigame_red_spawn_timer >= 90 and len(self.minigame_red_dots) < 2:
            self.minigame_red_spawn_timer = 0
            self.spawn_red_dot()

        new_black = []
        for d in self.minigame_black_dots:
            d["life"] -= 1
            if d["life"] > 0:
                new_black.append(d)
        self.minigame_black_dots = new_black

        new_red = []
        for d in self.minigame_red_dots:
            d["life"] -= 1
            if d["life"] > 0:
                new_red.append(d)
        self.minigame_red_dots = new_red

        if self.minigame_score >= self.minigame_target:
            self.minigame_done = True
            self.minigame_black_dots = []
            self.minigame_red_dots = []
            self.has_key = True
            self.save_game()
            self.start_dialogue([
                ("Крол", "фух.. готово. и что это... ключ?"),
                ("Крол", "наверное надо куда-то его вставить. идём дальше."),
            ], self.after_minigame)

    def after_minigame(self):
        self.location = "key_door_room"
        self.player_x = WIDTH // 2
        self.player_y = FLOOR_TOP + 30
        self.door_cooldown = 60
        self.save_game()

    def draw_minigame(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#08080c", outline="")

        for i in range(0, HEIGHT, 60):
            shade = 30 + int(10 * math.sin(i * 0.1))
            self.canvas.create_line(0, i, WIDTH, i, fill=f"#{shade:02x}{shade:02x}{shade + 5:02x}", width=1)
        for j in range(0, WIDTH, 60):
            shade = 30 + int(10 * math.sin(j * 0.1))
            self.canvas.create_line(j, 0, j, HEIGHT, fill=f"#{shade:02x}{shade:02x}{shade + 5:02x}", width=1)

        for d in self.minigame_black_dots:
            self.canvas.create_oval(d["x"] - d["r"], d["y"] - d["r"],
                                    d["x"] + d["r"], d["y"] + d["r"],
                                    fill="#0a0a0a", outline="#555555", width=3)

        for d in self.minigame_red_dots:
            self.canvas.create_oval(d["x"] - d["r"], d["y"] - d["r"],
                                    d["x"] + d["r"], d["y"] + d["r"],
                                    fill="#5a0a0a", outline="#ff2b2b", width=3)

        self.canvas.create_text(WIDTH // 2, 40,
                                text="СОБЕРИ 50 ЧЁРНЫХ",
                                fill="#8ff0ff", font=("Courier New", 20, "bold"))

        self.canvas.create_text(WIDTH // 2, 75,
                                text=f"Счёт: {self.minigame_score} / {self.minigame_target}",
                                fill="#ffffff", font=("Courier New", 18, "bold"))

        self.canvas.create_text(WIDTH // 2, HEIGHT - 30,
                                text="Клик по чёрным = +1   |   Клик по красным = -10",
                                fill="#8a8a9a", font=("Courier New", 12))

    def minigame_on_click(self, event):
        if self.location != "minigame":
            return
        if self.dialogue_active:
            return
        if self.minigame_done:
            return

        x, y = event.x, event.y

        for d in list(self.minigame_red_dots):
            if math.hypot(x - d["x"], y - d["y"]) < d["r"]:
                self.minigame_score = max(0, self.minigame_score - 10)
                self.minigame_red_dots.remove(d)
                return

        for d in list(self.minigame_black_dots):
            if math.hypot(x - d["x"], y - d["y"]) < d["r"]:
                self.minigame_score += 1
                self.minigame_black_dots.remove(d)
                return

    def draw_key_door_room(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#0a0a12", outline="")

        for i in range(0, HEIGHT, 50):
            shade = 35 + int(10 * math.sin(i * 0.1))
            self.canvas.create_line(0, i, WIDTH, i, fill=f"#{shade:02x}{shade:02x}{shade + 10:02x}", width=1)
        for j in range(0, WIDTH, 50):
            shade = 35 + int(10 * math.sin(j * 0.1))
            self.canvas.create_line(j, 0, j, HEIGHT, fill=f"#{shade:02x}{shade:02x}{shade + 10:02x}", width=1)

        self.canvas.create_rectangle(0, FLOOR_TOP, WIDTH, HEIGHT, fill="#1a1a24", outline="")
        self.canvas.create_line(0, FLOOR_TOP, WIDTH, FLOOR_TOP, fill="#000000", width=4)

        door_w = 200
        door_h = 280
        door_x = WIDTH // 2 - door_w // 2
        door_y = FLOOR_TOP - door_h

        if self.key_inserted:
            door_color = "#1a3a1a"
            door_outline = "#8aff8a"
        else:
            door_color = "#1a1a24"
            door_outline = "#5a5a6a"

        self.canvas.create_rectangle(door_x, door_y, door_x + door_w, door_y + door_h,
                                     fill=door_color, outline=door_outline, width=4)

        lock_cx = door_x + door_w // 2
        lock_cy = door_y + door_h // 2 - 20
        lock_color = "#8aff8a" if self.key_inserted else "#8a8a5a"
        self.canvas.create_rectangle(lock_cx - 30, lock_cy - 20, lock_cx + 30, lock_cy + 30,
                                     fill="#0a0a12", outline=lock_color, width=3)
        self.canvas.create_oval(lock_cx - 8, lock_cy - 8, lock_cx + 8, lock_cy + 8,
                                fill=lock_color, outline="")
        self.canvas.create_rectangle(lock_cx - 3, lock_cy + 5, lock_cx + 3, lock_cy + 18,
                                     fill=lock_color, outline="")

        if self.key_inserted:
            self.canvas.create_text(lock_cx, lock_cy + 5, text="🔑",
                                    font=("Arial", 28))

        self.canvas.create_text(WIDTH // 2, 40, text="ДВЕРЬ",
                                fill="#8a8a9a", font=("Courier New", 20, "bold"))

        if self.has_key and not self.key_inserted:
            self.canvas.create_text(WIDTH // 2, HEIGHT - 50,
                                    text="Нажми E чтобы вставить ключ",
                                    fill="#ffe066", font=("Courier New", 16, "bold"))
        elif self.key_inserted:
            self.canvas.create_text(WIDTH // 2, HEIGHT - 50,
                                    text="Дверь открыта...",
                                    fill="#8aff8a", font=("Courier New", 16, "bold"))
        else:
            self.canvas.create_text(WIDTH // 2, HEIGHT - 50,
                                    text="Нужен ключ",
                                    fill="#8a8a9a", font=("Courier New", 14))

        if self.has_key:
            self.canvas.create_text(WIDTH - 60, 40, text="🔑",
                                    fill="#ffe066", font=("Arial", 24))

    def draw_default_background(self):
        t = self.theme()
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=t["menu_bg"], outline="")
        for i in range(0, WIDTH, 4):
            if self.theme_name == "light":
                shade = 220 + int(15 * math.sin(i * 0.05))
                color = f"#{shade:02x}{shade:02x}{min(255, shade + 5):02x}"
            else:
                shade = 20 + int(15 * math.sin(i * 0.05))
                color = f"#{shade:02x}{shade:02x}{shade + 20:02x}"
            self.canvas.create_line(i, 0, i, HEIGHT, fill=color)

        for sx, sy, r in [(150, 120, 40), (700, 180, 60), (450, 90, 30), (820, 400, 50)]:
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r,
                                    fill=t["menu_bg"], outline=self.accent_color, width=2)

    def draw_menu_background(self):
        if self.mellloadback_img is not None:
            self.canvas.create_image(WIDTH // 2, HEIGHT // 2, image=self.mellloadback_img)
        else:
            self.draw_default_background()

    def show_menu(self):
        self.state = "menu"
        self.title_active = False
        self.dialogue_active = False
        self.dialogue_queue = []
        self.black_screen = False
        self.scream_shown = False
        self.objective = None
        self.cutscene_active = False
        self.cutscene_frames = []
        self.credits_timer = 0
        self.credits_scroll = HEIGHT + 100
        self.clear()
        self.draw_menu_background()
        self.draw_menu_ui()
        self.root.after(50, self.tick_menu)

    def draw_button(self, tag, x1, y1, x2, y2, label, color, callback, font_size=20):
        t = self.theme()
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=self.accent_color,
                                            width=3, tags=tag)
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=label, fill=t["text"],
                                font=("Courier New", font_size, "bold"), tags=tag)
        self.canvas.tag_bind(tag, "<Button-1>", lambda e, cb=callback: cb())
        self.canvas.tag_bind(tag, "<Enter>",
                             lambda e, r=rect: self.canvas.itemconfig(r, outline=t["accent_hover"]))
        self.canvas.tag_bind(tag, "<Leave>",
                             lambda e, r=rect: self.canvas.itemconfig(r, outline=self.accent_color))
        return rect

    def draw_menu_ui(self):
        t = self.theme()
        self.canvas.create_text(WIDTH // 2, 110, text="СКИБИДИ ТРП", fill=self.accent_color,
                                font=("Impact", 72, "bold"))
        self.canvas.create_text(WIDTH // 2, 185, text="Путешествие по мультивселенным", fill=t["text"],
                                font=("Courier New", 20, "bold"))

        buttons = []
        if self.has_save():
            buttons.append(("ПРОДОЛЖИТЬ", self.continue_game, t["btn_play"]))
            buttons.append(("НОВАЯ ИГРА", self.open_confirm, t["btn_danger"]))
        else:
            buttons.append(("ИГРАТЬ", self.new_game, t["btn_play"]))
        buttons.append(("НАСТРОЙКИ", self.open_settings, t["btn_cancel"]))

        start_y = 260
        step = 75
        for i, (label, callback, color) in enumerate(buttons):
            y1 = start_y + i * step
            y2 = y1 + 60
            self.draw_button(f"btn_{i}", WIDTH // 2 - 160, y1, WIDTH // 2 + 160, y2, label, color, callback)

        self.canvas.create_text(WIDTH // 2, HEIGHT - 40, text="v0.1  alpha  build", fill=t["text_dim"],
                                font=("Courier New", 12))

    def tick_menu(self):
        if self.state != "menu":
            return
        self.tick += 1
        self.clear()
        self.draw_menu_background()
        self.draw_menu_ui()
        self.root.after(50, self.tick_menu)

    def new_game(self):
        self.delete_save()
        self.player_x = WIDTH // 2
        self.player_y = 520
        self.play_time = 0
        self.hamster_fed = 0
        self.hamster_hunger = 0
        self.door_opened = False
        self.room_completed = False
        self.black_screen = False
        self.scream_shown = False
        self.objective = None
        self.dialogue_active = False
        self.dialogue_queue = []
        self.story_timer = 0
        self.story_stage = 0
        self.location = "krol_room"
        self.door_cooldown = 0
        self.visited_empty_room = False
        self.visited_tartenok_room = False
        self.tartenok_talked = False
        self.tunnel_stage = 0
        self.tunnel_x = 0
        self.door_code = random.randint(10, 99)
        self.code_input = ""
        self.code_solved = False
        self.code_attempts = 0
        self.code_hint_shown = False
        self.post_terminal_dialogue_shown = False
        self.minigame_score = 0
        self.minigame_done = False
        self.minigame_intro_shown = False
        self.minigame_black_dots = []
        self.minigame_red_dots = []
        self.has_key = False
        self.key_inserted = False
        self.boss_active = False
        self.boss_timer = 0
        self.boss_swords = []
        self.boss_sword_spawn_timer = 20
        self.boss_isa_intro_done = False
        self.boss_finished = False
        self.post_boss_phase = 0
        self.post_boss_timer = 0
        self.post_boss_actors_visible = False
        self.isa_visible = False
        self.break_timer = 0
        self.break_phase = 0
        self.credits_timer = 0
        self.credits_scroll = HEIGHT + 100
        self.final_dialogue_shown = False
        self.start_loading()

    def continue_game(self):
        if self.load_game():
            self.start_loading()
        else:
            self.new_game()

    def open_settings(self):
        self.state = "settings"
        self.clear()
        self.draw_menu_background()
        self.draw_settings_ui()

    def draw_settings_ui(self):
        t = self.theme()
        panel_x1 = WIDTH // 2 - 380
        panel_x2 = WIDTH // 2 + 380
        panel_y1 = 40
        panel_y2 = HEIGHT - 40
        self.canvas.create_rectangle(panel_x1, panel_y1, panel_x2, panel_y2,
                                     fill=t["menu_bg"], outline=self.accent_color, width=3)

        self.canvas.create_text(WIDTH // 2, 90, text="НАСТРОЙКИ", fill=self.accent_color,
                                font=("Impact", 42, "bold"))
        self.canvas.create_text(panel_x1 + 40, 165, text="Тема:", fill=t["text"],
                                font=("Courier New", 18, "bold"), anchor="w")

        theme_btn_y = 200
        for i, (name, label) in enumerate([("dark", "ТЁМНАЯ"), ("light", "СВЕТЛАЯ")]):
            x1 = panel_x1 + 40 + i * 200
            x2 = x1 + 180
            tag = f"theme_{name}"
            color = self.accent_color if self.theme_name == name else t["btn_cancel"]
            self.canvas.create_rectangle(x1, theme_btn_y, x2, theme_btn_y + 55,
                                         fill=color, outline=self.accent_color, width=2, tags=tag)
            self.canvas.create_text((x1 + x2) // 2, theme_btn_y + 27, text=label, fill=t["text"],
                                    font=("Courier New", 16, "bold"), tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>", lambda e, n=name: self.set_theme(n))

        self.canvas.create_text(panel_x1 + 40, 295, text="Цвет интерфейса:", fill=t["text"],
                                font=("Courier New", 18, "bold"), anchor="w")

        preset_y = 330
        cols = 4
        size = 70
        gap = 20
        start_x = panel_x1 + 40
        for i, (color, _) in enumerate(COLOR_PRESETS):
            row = i // cols
            col = i % cols
            x1 = start_x + col * (size + gap)
            y1 = preset_y + row * (size + gap)
            x2 = x1 + size
            y2 = y1 + size
            tag = f"preset_{i}"
            outline = "#ffffff" if color == self.accent_color else self.accent_color
            width = 4 if color == self.accent_color else 2
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline,
                                         width=width, tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>", lambda e, c=color: self.set_accent(c))

        back_y1 = panel_y2 - 70
        back_y2 = panel_y2 - 15
        self.draw_button("back_btn", WIDTH // 2 - 120, back_y1, WIDTH // 2 + 120, back_y2,
                         "НАЗАД", t["btn_cancel"], self.show_menu, font_size=18)

    def set_theme(self, name):
        self.theme_name = name
        self.save_settings()
        self.clear()
        self.draw_menu_background()
        self.draw_settings_ui()

    def set_accent(self, color):
        self.accent_color = color
        self.save_settings()
        self.clear()
        self.draw_menu_background()
        self.draw_settings_ui()

    def open_confirm(self):
        self.state = "confirm"
        self.clear()
        self.draw_menu_background()
        t = self.theme()

        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=t["overlay"], outline="", stipple="gray50")
        self.canvas.create_rectangle(WIDTH // 2 - 320, HEIGHT // 2 - 170, WIDTH // 2 + 320, HEIGHT // 2 + 170,
                                     fill=t["menu_bg"], outline=t["btn_danger"], width=3)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 120, text="ВНИМАНИЕ!", fill=t["btn_danger"],
                                font=("Impact", 32, "bold"))
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 70,
                                text="Весь прогресс будет удалён.\nТы точно уверен?",
                                fill=t["text"], font=("Courier New", 15, "bold"), justify="center")

        self.confirm_btn_x = WIDTH // 2 - 160
        self.confirm_btn_y = HEIGHT // 2 + 70
        self.confirm_escape_time = self.root.after(self.confirm_escape_duration, self.confirm_stop_escaping)
        self.confirm_hold_start = None
        self.confirm_hold_progress = 0

        self.no_btn_x = WIDTH // 2 + 160
        self.no_btn_y = HEIGHT // 2 + 70
        self.no_btn_w = 200
        self.no_btn_h = 60

        self.canvas.bind("<Motion>", self.confirm_on_motion)
        self.canvas.bind("<ButtonPress-1>", self.confirm_on_press)
        self.canvas.bind("<ButtonRelease-1>", self.confirm_on_release)

        self.draw_confirm_buttons()

    def draw_confirm_buttons(self):
        for obj in (self.confirm_btn_rect, self.confirm_btn_text, self.confirm_progress_rect,
                    self.no_btn_rect, self.no_btn_text):
            if obj:
                self.canvas.delete(obj)

        t = self.theme()
        x, y = self.confirm_btn_x, self.confirm_btn_y
        w, h = self.confirm_btn_w, self.confirm_btn_h

        self.confirm_btn_rect = self.canvas.create_rectangle(
            x - w // 2, y - h // 2, x + w // 2, y + h // 2,
            fill=t["btn_danger"], outline=t["btn_danger"], width=2
        )
        self.confirm_progress_rect = self.canvas.create_rectangle(
            x - w // 2 + 2, y + h // 2 - 8, x - w // 2 + 2, y + h // 2 - 2,
            fill=self.accent_color, outline=""
        )
        label = "ДЕРЖИ..." if self.confirm_hold_start is not None else "УДАЛИТЬ ВСЁ"
        self.confirm_btn_text = self.canvas.create_text(x, y, text=label, fill=t["text"],
                                                        font=("Courier New", 14, "bold"))

        nx, ny = self.no_btn_x, self.no_btn_y
        nw, nh = self.no_btn_w, self.no_btn_h
        self.no_btn_rect = self.canvas.create_rectangle(
            nx - nw // 2, ny - nh // 2, nx + nw // 2, ny + nh // 2,
            fill=t["btn_cancel"], outline=self.accent_color, width=2, tags="no_btn"
        )
        self.no_btn_text = self.canvas.create_text(nx, ny, text="НЕТ, ОТМЕНА", fill=t["text"],
                                                   font=("Courier New", 14, "bold"), tags="no_btn")
        self.canvas.tag_bind("no_btn", "<Button-1>", lambda e: self.close_confirm())
        self.canvas.tag_bind("no_btn", "<Enter>",
                             lambda e: self.canvas.itemconfig(self.no_btn_rect, outline=t["accent_hover"]))
        self.canvas.tag_bind("no_btn", "<Leave>",
                             lambda e: self.canvas.itemconfig(self.no_btn_rect, outline=self.accent_color))

    def confirm_on_motion(self, event):
        if self.state != "confirm" or self.confirm_escape_time is None:
            return
        x, y = event.x, event.y
        bx, by = self.confirm_btn_x, self.confirm_btn_y
        w, h = self.confirm_btn_w, self.confirm_btn_h
        margin = 80
        if bx - w // 2 - margin < x < bx + w // 2 + margin and by - h // 2 - margin < y < by + h // 2 + margin:
            angle = math.atan2(by - y, bx - x)
            new_x = bx + math.cos(angle) * 180
            new_y = by + math.sin(angle) * 120
            new_x = max(w // 2 + 20, min(WIDTH - w // 2 - 20, new_x))
            new_y = max(h // 2 + 20, min(HEIGHT - h // 2 - 20, new_y))
            self.confirm_btn_x = new_x
            self.confirm_btn_y = new_y
            self.draw_confirm_buttons()

    def confirm_stop_escaping(self):
        self.confirm_escape_time = None
        self.draw_confirm_buttons()

    def confirm_on_press(self, event):
        if self.state != "confirm":
            return
        x, y = event.x, event.y
        bx, by = self.confirm_btn_x, self.confirm_btn_y
        w, h = self.confirm_btn_w, self.confirm_btn_h
        if bx - w // 2 < x < bx + w // 2 and by - h // 2 < y < by + h // 2:
            self.confirm_hold_start = self.root.after(0, self.confirm_hold_tick)

    def confirm_on_release(self, event):
        if self.state != "confirm":
            return
        if self.confirm_hold_start is not None:
            self.root.after_cancel(self.confirm_hold_start)
            self.confirm_hold_start = None
            self.confirm_hold_progress = 0
            self.draw_confirm_buttons()

    def confirm_hold_tick(self):
        if self.state != "confirm" or self.confirm_hold_start is None:
            return
        self.confirm_hold_progress += 50
        progress = min(1.0, self.confirm_hold_progress / self.confirm_hold_required)
        x, y = self.confirm_btn_x, self.confirm_btn_y
        w, h = self.confirm_btn_w, self.confirm_btn_h
        self.canvas.coords(self.confirm_progress_rect,
                           x - w // 2 + 2, y + h // 2 - 8,
                           x - w // 2 + 2 + (w - 4) * progress, y + h // 2 - 2)
        if progress >= 1.0:
            self.confirm_hold_start = None
            self.close_confirm()
            self.new_game()
        else:
            self.confirm_hold_start = self.root.after(50, self.confirm_hold_tick)

    def close_confirm(self):
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        if self.confirm_escape_time is not None:
            self.root.after_cancel(self.confirm_escape_time)
            self.confirm_escape_time = None
        if self.confirm_hold_start is not None:
            self.root.after_cancel(self.confirm_hold_start)
            self.confirm_hold_start = None
        self.confirm_btn_rect = None
        self.confirm_btn_text = None
        self.confirm_progress_rect = None
        self.no_btn_rect = None
        self.no_btn_text = None
        self.show_menu()

    def start_loading(self):
        self.state = "loading"
        self.loading_progress = 0
        self.clear()
        self.draw_menu_background()
        t = self.theme()
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 40, text="ЗАГРУЗКА...", fill=t["text"],
                                font=("Courier New", 28, "bold"))
        self.canvas.create_rectangle(200, HEIGHT // 2, WIDTH - 200, HEIGHT // 2 + 30,
                                     outline=self.accent_color, width=2)
        self.bar = self.canvas.create_rectangle(204, HEIGHT // 2 + 4, 204, HEIGHT // 2 + 26,
                                                fill=self.accent_color, outline="")
        self.load_text = self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 70, text="0%",
                                                 fill=t["text"], font=("Courier New", 16, "bold"))
        self.root.after(80, self.loading_step)

    def loading_step(self):
        if self.state != "loading":
            return
        self.loading_progress += random.randint(2, 7)
        if self.loading_progress > 100:
            self.loading_progress = 100
        x2 = 204 + (WIDTH - 408) * (self.loading_progress / 100)
        self.canvas.coords(self.bar, 204, HEIGHT // 2 + 4, x2, HEIGHT // 2 + 26)
        self.canvas.itemconfig(self.load_text, text=f"{self.loading_progress}%")
        if self.loading_progress >= 100:
            self.root.after(400, self.start_game)
        else:
            self.root.after(80, self.loading_step)

    def start_game(self):
        self.state = "game"
        self.autosave_timer = 0
        self.door_cooldown = 90
        self.canvas.bind("<Button-1>", self.on_click)
        if self.location == "krol_room" and self.story_stage == 0:
            self.start_title("Квартира Крола", None)
        else:
            self.title_active = False

        if self.location == "boss_isa" and not self.boss_finished:
            self.boss_active = True
            self.boss_timer = 0
            self.boss_swords = []
            self.boss_sword_spawn_timer = 20
            self.player_x = 150
            self.player_y = HEIGHT // 2
            self.isa_visible = True

        self.game_loop()

    def on_click(self, event):
        if self.state != "game":
            return
        if self.cutscene_active:
            self.skip_cutscene()
            return
        if self.title_active:
            self.skip_title()
            return
        if self.dialogue_active:
            self.advance_dialogue()
            return

        if self.location == "krol_room":
            hx = CAGE_X + CAGE_W // 2
            hy = CAGE_Y + CAGE_H // 2 + 5
            if math.hypot(event.x - hx, event.y - hy) < 90:
                self.feed_hamster()

        elif self.location == "minigame":
            self.minigame_on_click(event)

    def feed_hamster(self):
        self.hamster_fed += 1
        self.hamster_hunger = 0
        self.hamster_joy = 120
        self.hamster_bounce = 30
        if self.hamster_fed == 1:
            self.show_hint("Хомяк счастлив! Хрум-хрум ✨")
        elif self.hamster_fed == 2:
            self.show_hint("Хомяк прыгает от радости! ✨")
        elif self.hamster_fed == 3:
            self.show_hint("Хомяк наелся и танцует! ✨")
        else:
            self.show_hint("Хомяк: Я БОЛЬШЕ НЕ МОГУ!!!")

    def start_title(self, text, callback):
        self.title_active = True
        self.title_timer = 0
        self.title_text = text
        self.title_callback = callback

    def skip_title(self):
        if not self.title_active:
            return
        self.title_active = False
        cb = self.title_callback
        self.title_callback = None
        if cb:
            cb()

    def draw_title(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", outline="")

        if self.title_timer < 60:
            alpha = self.title_timer / 60
        elif self.title_timer > 180:
            alpha = max(0.0, 1.0 - (self.title_timer - 180) / 60)
        else:
            alpha = 1.0

        if alpha <= 0:
            self.title_active = False
            cb = self.title_callback
            self.title_callback = None
            if cb:
                cb()
            return

        gray = int(255 * alpha)
        color = f"#{gray:02x}{gray:02x}{gray:02x}"

        self.canvas.create_text(WIDTH // 2, HEIGHT // 2,
                                text=self.title_text,
                                fill=color,
                                font=("Courier New", 44, "bold"))

        self.canvas.create_text(WIDTH - 20, HEIGHT - 20,
                                text="[ПРОБЕЛ] пропустить",
                                fill="#555555", font=("Courier New", 10),
                                anchor="se")

    def draw_room(self):
        self.canvas.create_rectangle(0, 0, WIDTH, WALL_TOP, fill="#f0f0f0", outline="")
        self.canvas.create_rectangle(0, WALL_TOP, WIDTH, FLOOR_TOP, fill="#fafafa", outline="")

        for i in range(0, WIDTH, 3):
            alpha = 240 + int(10 * math.sin(i * 0.1))
            self.canvas.create_line(i, 0, i, WALL_TOP, fill=f"#{alpha:02x}{alpha:02x}{alpha:02x}")

        self.canvas.create_line(0, WALL_TOP, WIDTH, WALL_TOP, fill="#d0d0d0", width=2)
        self.canvas.create_line(0, FLOOR_TOP, WIDTH, FLOOR_TOP, fill="#8a5a2a", width=4)

        self.canvas.create_rectangle(0, FLOOR_TOP, WIDTH, HEIGHT, fill="#a07040", outline="")
        plank_h = 45
        y = FLOOR_TOP
        row = 0
        while y < HEIGHT:
            x = -((row % 2) * 70)
            while x < WIDTH:
                base = 150 + ((row * 17 + x) % 25) - 12
                color = f"#{base + 30:02x}{base:02x}{int(base * 0.55):02x}"
                self.canvas.create_rectangle(x, y, x + 140, y + plank_h - 2,
                                             fill=color, outline="#7a4a20", width=1)
                x += 140
            y += plank_h
            row += 1

        self.draw_window(640, 210, 200, 130)
        self.draw_door(DOOR_X, DOOR_Y)
        self.draw_desk()
        self.draw_sofa(690, 380)
        self.draw_hamster_cage(CAGE_X, CAGE_Y)
        self.draw_side_table(540, 500)

    def draw_window(self, x, y, w, h):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill="#87ceeb", outline="#5a3a22", width=8)
        self.canvas.create_line(x + w // 2, y, x + w // 2, y + h, fill="#5a3a22", width=6)
        self.canvas.create_line(x, y + h // 2, x + w, y + h // 2, fill="#5a3a22", width=6)

        for i in range(4):
            star_x = x + 20 + i * 40
            self.canvas.create_line(star_x, y + 20, star_x + 8, y + 20, fill="#ffffff", width=2)
            self.canvas.create_line(star_x, y + 35, star_x + 12, y + 35, fill="#ffffff", width=2)

        self.canvas.create_oval(x + 130, y + 40, x + 160, y + 70, fill="#fff4a0", outline="")

        self.canvas.create_rectangle(x - 12, y + h, x + w + 12, y + h + 22,
                                     fill="#e8e8e8", outline="#b0b0b0", width=2)

        self.draw_cactus_on_windowsill(x + 50, y + h + 22)

    def draw_cactus_on_windowsill(self, x, y):
        pot_top = y - 8
        self.canvas.create_polygon(x - 20, pot_top, x + 20, pot_top, x + 16, pot_top + 30,
                                   x - 16, pot_top + 30, fill="#c85a3a", outline="#8a3a20", width=2)
        self.canvas.create_rectangle(x - 22, pot_top - 4, x + 22, pot_top + 2,
                                     fill="#d86a4a", outline="#8a3a20", width=2)

        self.canvas.create_rectangle(x - 12, y - 40, x + 12, pot_top,
                                     fill="#3a9a28", outline="#1e5a14", width=2)
        self.canvas.create_rectangle(x - 30, y - 25, x - 12, y - 12,
                                     fill="#3a9a28", outline="#1e5a14", width=2)
        self.canvas.create_rectangle(x - 30, y - 35, x - 22, y - 12,
                                     fill="#3a9a28", outline="#1e5a14", width=2)
        self.canvas.create_rectangle(x + 12, y - 30, x + 28, y - 17,
                                     fill="#3a9a28", outline="#1e5a14", width=2)
        self.canvas.create_rectangle(x + 20, y - 40, x + 28, y - 17,
                                     fill="#3a9a28", outline="#1e5a14", width=2)

        for i in range(3):
            ex = x - 6 + i * 6
            self.canvas.create_line(ex, y - 40, ex, y - 48, fill="#e0e0a0", width=1)

    def draw_door(self, x, y):
        if self.door_opened:
            self.canvas.create_rectangle(x, y, x + DOOR_W, y + DOOR_H,
                                         fill="#0a0a12", outline="#000000", width=3)
            self.canvas.create_rectangle(x + 8, y + 8, x + DOOR_W - 8, y + DOOR_H - 8,
                                         fill="#1a0a2a", outline="#8ff0ff", width=2)

            cx = x + DOOR_W // 2
            cy = y + DOOR_H // 2
            for r, col in [(60, "#1a1a3a"), (45, "#2a1a4a"), (30, "#3a2a6a"), (15, "#5a3a9a")]:
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                        fill=col, outline="")

            pulse = int(3 + 2 * math.sin(self.tick * 0.1))
            self.canvas.create_oval(cx - 10 - pulse, cy - 10 - pulse,
                                    cx + 10 + pulse, cy + 10 + pulse,
                                    fill="#c8a0ff", outline="#ffffff", width=2)

            self.canvas.create_rectangle(x, y, x + DOOR_W, y + DOOR_H,
                                         fill="", outline="#8ff0ff", width=3)
        else:
            door_color = "#d8d8d8"
            door_inner = "#f0f0f0"
            self.canvas.create_rectangle(x, y, x + DOOR_W, y + DOOR_H,
                                         fill=door_color, outline="#909090", width=3)
            self.canvas.create_rectangle(x + 6, y + 6, x + DOOR_W - 6, y + DOOR_H - 6,
                                         fill=door_inner, outline="#b0b0b0", width=2)
            self.canvas.create_rectangle(x + 14, y + 14, x + DOOR_W - 14, y + 100,
                                         fill="#e0e0e0", outline="#a0a0a0", width=1)
            self.canvas.create_rectangle(x + 14, y + 110, x + DOOR_W - 14, y + DOOR_H - 14,
                                         fill="#e0e0e0", outline="#a0a0a0", width=1)
            self.canvas.create_oval(x + DOOR_W - 22, y + 110, x + DOOR_W - 8, y + 130,
                                    fill="#c8c8c8", outline="#808080", width=2)

    def draw_desk(self):
        x1, y1, x2, y2 = 330, 270, 610, 440

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#ffffff", outline="#c0c0c0", width=3)
        self.canvas.create_rectangle(x1 + 6, y1 + 6, x2 - 6, y1 + 60, fill="#f0f0f0", outline="#c0c0c0", width=1)

        mx1, my1, mx2, my2 = x1 + 90, y1 + 60, x1 + 190, y1 + 130
        self.canvas.create_rectangle(mx1, my1, mx2, my2, fill="#1a1a24", outline="#000", width=3)
        self.canvas.create_rectangle(mx1 + 4, my1 + 4, mx2 - 4, my2 - 8, fill="#2a4a6a", outline="")
        self.canvas.create_text((mx1 + mx2) // 2, (my1 + my2) // 2 - 4, text=">_",
                                fill="#8ff0ff", font=("Courier New", 22, "bold"))
        self.canvas.create_rectangle(mx1 + 30, my2, mx2 - 30, my2 + 10, fill="#1a1a24", outline="#000")
        self.canvas.create_rectangle(mx1 + 10, my2 + 10, mx2 - 10, my2 + 20, fill="#1a1a24", outline="#000")

        kx1, ky1 = x1 + 40, y1 + 130
        self.canvas.create_rectangle(kx1, ky1, kx1 + 130, ky1 + 45, fill="#e0e0e0", outline="#a0a0a0", width=2)
        for row in range(3):
            for col in range(12):
                kx = kx1 + 6 + col * 10
                ky = ky1 + 6 + row * 13
                self.canvas.create_rectangle(kx, ky, kx + 8, ky + 10, fill="#ffffff", outline="#a0a0a0", width=1)

        mx1, my1 = x1 + 190, y1 + 130
        self.canvas.create_oval(mx1, my1, mx1 + 30, my1 + 45, fill="#c0c0c0", outline="#808080", width=2)

        self.draw_mug(x1 + 55, y1 + 75)

    def draw_mug(self, x, y):
        body_color = "#e8e8f0"
        outline_color = "#808090"

        self.canvas.create_oval(x - 22, y + 22, x + 22, y + 32, fill="#5a3a20", outline="")

        self.canvas.create_rectangle(x - 20, y - 20, x + 20, y + 25,
                                     fill=body_color, outline=outline_color, width=2)
        self.canvas.create_oval(x - 20, y - 26, x + 20, y - 14,
                                fill="#f5f5ff", outline=outline_color, width=2)
        self.canvas.create_oval(x - 15, y - 23, x + 15, y - 17,
                                fill="#5a3a20", outline="")

        self.canvas.create_arc(x + 18, y - 12, x + 40, y + 15, start=-80, extent=160,
                               style="arc", outline=outline_color, width=3)

        for i in range(3):
            px = x - 8 + i * 8
            py = y - 30
            t_phase = (self.tick + i * 15) % 60
            offset = int(math.sin(t_phase * 0.15) * 3)
            self.canvas.create_line(px + offset, py, px + offset - 3, py - 8,
                                    fill="#c8c8d0", width=1)
            self.canvas.create_line(px + offset - 3, py - 8, px + offset + 1, py - 16,
                                    fill="#c8c8d0", width=1)

    def draw_sofa(self, x, y):
        w, h = 200, 130

        self.canvas.create_rectangle(x + 10, y + h - 15, x + 30, y + h,
                                     fill="#3a2010", outline="#2a1008", width=1)
        self.canvas.create_rectangle(x + w - 30, y + h - 15, x + w - 10, y + h,
                                     fill="#3a2010", outline="#2a1008", width=1)

        self.canvas.create_rectangle(x, y, x + w, y + 55,
                                     fill="#7a4a2a", outline="#3a2010", width=2)
        self.canvas.create_rectangle(x + 8, y + 8, x + w - 8, y + 50,
                                     fill="#8a5a3a", outline="#4a2a10", width=1)
        self.canvas.create_line(x + w // 2, y + 8, x + w // 2, y + 50, fill="#4a2a10", width=1)

        self.canvas.create_rectangle(x - 15, y - 10, x + 25, y + 90,
                                     fill="#6a3a1a", outline="#3a2010", width=2)
        self.canvas.create_oval(x - 10, y, x + 20, y + 25,
                                fill="#8a5a3a", outline="#4a2a10", width=1)
        self.canvas.create_oval(x - 10, y + 55, x + 20, y + 80,
                                fill="#8a5a3a", outline="#4a2a10", width=1)

        self.canvas.create_rectangle(x + w - 25, y - 10, x + w + 15, y + 90,
                                     fill="#6a3a1a", outline="#3a2010", width=2)
        self.canvas.create_oval(x + w - 20, y, x + w + 10, y + 25,
                                fill="#8a5a3a", outline="#4a2a10", width=1)
        self.canvas.create_oval(x + w - 20, y + 55, x + w + 10, y + 80,
                                fill="#8a5a3a", outline="#4a2a10", width=1)

        self.canvas.create_rectangle(x + 5, y + 55, x + w - 5, y + h - 10,
                                     fill="#9a6a4a", outline="#4a2a10", width=2)

        self.canvas.create_rectangle(x + 20, y + 60, x + 95, y + h - 20,
                                     fill="#a87a5a", outline="#5a3a20", width=1)
        self.canvas.create_rectangle(x + 105, y + 60, x + 180, y + h - 20,
                                     fill="#a87a5a", outline="#5a3a20", width=1)
        self.canvas.create_line(x + 100, y + 60, x + 100, y + h - 20, fill="#5a3a20", width=1)

        self.canvas.create_oval(x + 130, y + 45, x + 165, y + 80,
                                fill="#c85a5a", outline="#8a3a3a", width=2)
        self.canvas.create_oval(x + 145, y + 55, x + 175, y + 85,
                                fill="#5a8ac8", outline="#3a5a8a", width=2)

    def draw_hamster_cage(self, x, y):
        cw, ch = CAGE_W, CAGE_H

        self.canvas.create_rectangle(x, y, x + cw, y + ch, fill="#e8f0f8", outline="#888", width=3)
        self.canvas.create_rectangle(x + 4, y + 4, x + cw - 4, y + ch - 4,
                                     fill="#f8fbff", outline="#bbb", width=1)

        for gx in range(x + 12, x + cw - 6, 16):
            self.canvas.create_line(gx, y + 4, gx, y + ch - 4, fill="#c8d8e8", width=1)
        for gy in range(y + 12, y + ch - 6, 16):
            self.canvas.create_line(x + 4, gy, x + cw - 4, gy, fill="#c8d8e8", width=1)

        self.canvas.create_rectangle(x + 8, y + ch - 30, x + cw - 8, y + ch - 6,
                                     fill="#e0d0a0", outline="#b0a070", width=1)

        hx = x + cw // 2
        hy = y + ch // 2 + 5

        if self.hamster_bounce > 0:
            hy -= int(math.sin(self.hamster_bounce * 0.3) * 8)
            self.hamster_bounce -= 1

        if self.hamster_joy > 0:
            self.hamster_joy -= 1

        self.canvas.create_oval(hx - 26, hy - 18, hx + 26, hy + 18,
                                fill="#d8a060", outline="#8a6020", width=2)
        self.canvas.create_oval(hx - 24, hy - 10, hx + 24, hy + 16,
                                fill="#e8b878", outline="")

        self.canvas.create_oval(hx - 22, hy - 26, hx - 4, hy - 8,
                                fill="#d8a060", outline="#8a6020", width=2)
        self.canvas.create_oval(hx + 4, hy - 26, hx + 22, hy - 8,
                                fill="#d8a060", outline="#8a6020", width=2)
        self.canvas.create_oval(hx - 18, hy - 22, hx - 8, hy - 12,
                                fill="#f8d8b0", outline="")
        self.canvas.create_oval(hx + 8, hy - 22, hx + 18, hy - 12,
                                fill="#f8d8b0", outline="")

        if self.hamster_joy > 0:
            self.canvas.create_arc(hx - 16, hy - 6, hx - 6, hy + 4, start=0, extent=180,
                                   style="arc", outline="#000", width=2)
            self.canvas.create_arc(hx + 6, hy - 6, hx + 16, hy + 4, start=0, extent=180,
                                   style="arc", outline="#000", width=2)
        else:
            self.canvas.create_oval(hx - 14, hy - 4, hx - 7, hy + 3, fill="#000", outline="")
            self.canvas.create_oval(hx + 7, hy - 4, hx + 14, hy + 3, fill="#000", outline="")
            self.canvas.create_oval(hx - 12, hy - 2, hx - 9, hy + 1, fill="#ffffff", outline="")
            self.canvas.create_oval(hx + 9, hy - 2, hx + 12, hy + 1, fill="#ffffff", outline="")

        if self.hamster_joy > 0:
            self.canvas.create_arc(hx - 8, hy + 2, hx + 8, hy + 14, start=180, extent=180,
                                   style="arc", outline="#8a3a3a", width=2)
        else:
            self.canvas.create_oval(hx - 4, hy + 5, hx + 4, hy + 11, fill="#ff8a8a", outline="#aa3a3a", width=1)

        self.canvas.create_line(hx - 6, hy + 12, hx - 2, hy + 10, fill="#5a3a20", width=1)
        self.canvas.create_line(hx + 6, hy + 12, hx + 2, hy + 10, fill="#5a3a20", width=1)

        self.canvas.create_oval(hx - 24, hy + 14, hx - 16, hy + 24, fill="#d8a060", outline="#8a6020", width=1)
        self.canvas.create_oval(hx + 16, hy + 14, hx + 24, hy + 24, fill="#d8a060", outline="#8a6020", width=1)

        if self.hamster_joy > 0:
            for i in range(4):
                sx = hx + 30 + i * 10
                sy = hy - 25 - i * 3 - int(math.sin((self.tick + i * 10) * 0.2) * 3)
                self.canvas.create_text(sx, sy, text="✨", font=("Arial", 14))

    def draw_side_table(self, x, y):
        self.canvas.create_rectangle(x, y, x + 80, y + 40, fill="#8a5a2a", outline="#3a2010", width=2)
        self.canvas.create_rectangle(x + 6, y + 6, x + 74, y + 34, fill="#a06a3a", outline="#3a2010", width=1)
        self.canvas.create_rectangle(x + 8, y + 40, x + 18, y + 90, fill="#6a3a1a", outline="#3a2010", width=2)
        self.canvas.create_rectangle(x + 62, y + 40, x + 72, y + 90, fill="#6a3a1a", outline="#3a2010", width=2)

        self.canvas.create_oval(x + 25, y - 20, x + 55, y + 10, fill="#ffe066", outline="#8a6a00", width=2)
        self.canvas.create_text(x + 40, y - 5, text="💡", font=("Arial", 14))

    def draw_castle(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#1a1a20", outline="")

        for i in range(0, HEIGHT, 60):
            shade = 60 + int(10 * math.sin(i * 0.1))
            self.canvas.create_line(0, i, WIDTH, i, fill=f"#{shade:02x}{shade:02x}{shade + 5:02x}", width=1)
        for j in range(0, WIDTH, 60):
            shade = 60 + int(10 * math.sin(j * 0.1))
            self.canvas.create_line(j, 0, j, HEIGHT, fill=f"#{shade:02x}{shade:02x}{shade + 5:02x}", width=1)

        self.canvas.create_rectangle(0, 0, WIDTH, 80, fill="#2a2a32", outline="")
        self.canvas.create_line(0, 80, WIDTH, 80, fill="#3a3a44", width=3)

        self.canvas.create_rectangle(0, FLOOR_TOP, WIDTH, HEIGHT, fill="#3a3a42", outline="")
        self.canvas.create_line(0, FLOOR_TOP, WIDTH, FLOOR_TOP, fill="#1a1a20", width=4)

        for i in range(0, WIDTH, 80):
            self.canvas.create_line(i, FLOOR_TOP, i, HEIGHT, fill="#2a2a32", width=1)
        for j in range(FLOOR_TOP, HEIGHT, 40):
            self.canvas.create_line(0, j, WIDTH, j, fill="#2a2a32", width=1)

        door_w = CASTLE_DOOR_W
        door_h = CASTLE_DOOR_H
        door_y = FLOOR_TOP - door_h

        left_x = 80
        center_x = WIDTH // 2 - door_w // 2
        right_x = WIDTH - 80 - door_w

        self.draw_castle_door(left_x, door_y, door_w, door_h, "ЛЕВО")
        self.draw_castle_door(center_x, door_y, door_w, door_h, "ВПЕРЁД")
        self.draw_castle_door(right_x, door_y, door_w, door_h, "ПРАВО")

        self.canvas.create_text(WIDTH // 2, 40,
                                text="ЗАМОК СТРП",
                                fill="#8a8a9a", font=("Courier New", 20, "bold"))

    def draw_castle_door(self, x, y, w, h, label):
        self.canvas.create_rectangle(x, y, x + w, y + h,
                                     fill="#0e0e12", outline="#2a2a32", width=3)
        self.canvas.create_rectangle(x + 8, y + 8, x + w - 8, y + h - 8,
                                     fill="#14141a", outline="#3a3a44", width=2)

        cx = x + w // 2
        cy = y + h // 2

        for r, col in [(50, "#1a1a22"), (35, "#242430"), (20, "#2e2e3c")]:
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill=col, outline="")

        self.canvas.create_text(cx, y - 22, text=label,
                                fill="#5a5a6a", font=("Courier New", 12, "bold"))

    def draw_tartenok_room(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#2a1a2a", outline="")

        for i in range(0, HEIGHT, 50):
            shade = 40 + int(10 * math.sin(i * 0.1))
            self.canvas.create_line(0, i, WIDTH, i, fill=f"#{shade:02x}{shade // 2:02x}{shade:02x}", width=1)

        self.canvas.create_rectangle(0, FLOOR_TOP, WIDTH, HEIGHT, fill="#4a2a4a", outline="")
        self.canvas.create_line(0, FLOOR_TOP, WIDTH, FLOOR_TOP, fill="#1a0a1a", width=4)

        for i in range(0, WIDTH, 100):
            self.canvas.create_line(i, FLOOR_TOP, i, HEIGHT, fill="#3a1a3a", width=1)

        self.canvas.create_text(WIDTH // 2, 40, text="КОМНАТА ТАРТЕНКА",
                                fill="#c88aff", font=("Courier New", 20, "bold"))

        tartenok_x = WIDTH // 2
        tartenok_y = FLOOR_TOP - PLAYER_SIZE // 2

        if self.mellchar2_img is not None:
            self.canvas.create_image(tartenok_x, tartenok_y, image=self.mellchar2_img)
        else:
            s = PLAYER_SIZE
            self.canvas.create_rectangle(tartenok_x - s // 2, tartenok_y - s // 2,
                                         tartenok_x + s // 2, tartenok_y + s // 2,
                                         fill="#c88aff", outline="#000", width=2)
            self.canvas.create_text(tartenok_x, tartenok_y,
                                    text="?", fill="#000",
                                    font=("Courier New", 32, "bold"))

        exit_x = 30
        exit_y = HEIGHT - 70
        self.canvas.create_rectangle(exit_x, exit_y, exit_x + CASTLE_DOOR_W, exit_y + 55,
                                     fill="#1a0a1a", outline="#c88aff", width=2)
        self.canvas.create_text(exit_x + CASTLE_DOOR_W // 2, exit_y + 27,
                                text="← В ЗАМОК", fill="#c88aff",
                                font=("Courier New", 12, "bold"))

    def draw_empty_room(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#1a1a20", outline="")

        for i in range(0, HEIGHT, 60):
            shade = 50 + int(10 * math.sin(i * 0.1))
            self.canvas.create_line(0, i, WIDTH, i, fill=f"#{shade:02x}{shade:02x}{shade:02x}", width=1)

        self.canvas.create_rectangle(0, FLOOR_TOP, WIDTH, HEIGHT, fill="#3a3a42", outline="")
        self.canvas.create_line(0, FLOOR_TOP, WIDTH, FLOOR_TOP, fill="#1a1a20", width=4)

        self.canvas.create_text(WIDTH // 2, 40, text="ПУСТАЯ КОМНАТА",
                                fill="#5a5a6a", font=("Courier New", 20, "bold"))

        exit_x = 30
        exit_y = HEIGHT - 70
        self.canvas.create_rectangle(exit_x, exit_y, exit_x + CASTLE_DOOR_W, exit_y + 55,
                                     fill="#0e0e12", outline="#5a5a6a", width=2)
        self.canvas.create_text(exit_x + CASTLE_DOOR_W // 2, exit_y + 27,
                                text="← В ЗАМОК", fill="#8a8a9a",
                                font=("Courier New", 12, "bold"))

    def get_segment_style(self, stage):
        if stage == 0:
            return {
                "bg": "#0a0a0e", "outline": "#3a2a1a", "wall": "#1a1008",
                "lamp": "#ff8a3a", "label": "РЖАВЫЙ СЕГМЕНТ",
                "label_color": "#a06a3a", "floor": "#1a1008",
            }
        elif stage == 1:
            return {
                "bg": "#06080e", "outline": "#1a2a4a", "wall": "#0a1424",
                "lamp": "#3aa0ff", "label": "СИНИЙ СЕГМЕНТ",
                "label_color": "#3aa0ff", "floor": "#0a1424",
            }
        elif stage == 2:
            return {
                "bg": "#0e0606", "outline": "#4a1a1a", "wall": "#240808",
                "lamp": "#ff3a3a", "label": "АВАРИЙНЫЙ СЕГМЕНТ",
                "label_color": "#ff3a3a", "floor": "#240808",
            }
        elif stage == 3:
            return {
                "bg": "#06120a", "outline": "#1a4a2a", "wall": "#082410",
                "lamp": "#3aff8a", "label": "ЗЕЛЁНЫЙ СЕГМЕНТ",
                "label_color": "#3aff8a", "floor": "#082410",
            }
        else:
            return {
                "bg": "#0c0616", "outline": "#3a1a6a", "wall": "#1a0830",
                "lamp": "#c88aff", "label": "ФИОЛЕТОВЫЙ СЕГМЕНТ",
                "label_color": "#c88aff", "floor": "#1a0830",
            }

    def draw_tunnel(self):
        style = self.get_segment_style(self.tunnel_stage)

        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=style["bg"], outline="")

        for i in range(0, HEIGHT, 40):
            shade = 25 + int(5 * math.sin(i * 0.1 + self.tick * 0.05))
            self.canvas.create_line(0, i, WIDTH, i, fill=f"#{shade:02x}{shade:02x}{shade + 3:02x}", width=1)

        tunnel_top = 200
        tunnel_bottom = 480
        tunnel_left = 60
        tunnel_right = WIDTH - 60

        self.canvas.create_rectangle(tunnel_left, tunnel_top, tunnel_right, tunnel_bottom,
                                     fill=style["wall"], outline=style["outline"], width=3)

        for i in range(tunnel_left + 30, tunnel_right - 30, 60):
            self.canvas.create_line(i, tunnel_top + 20, i, tunnel_bottom - 20,
                                    fill=style["outline"], width=1)

        for j in range(tunnel_top + 30, tunnel_bottom - 20, 40):
            self.canvas.create_line(tunnel_left + 20, j, tunnel_right - 20, j,
                                    fill=style["outline"], width=1)

        for i in range(8):
            px = tunnel_left + 100 + i * 90
            pulse = abs(math.sin(self.tick * 0.05 + i * 0.7))
            base_color = style["lamp"]
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)
            rr = int(r * (0.4 + 0.6 * pulse))
            gg = int(g * (0.4 + 0.6 * pulse))
            bb = int(b * (0.4 + 0.6 * pulse))
            color = f"#{rr:02x}{gg:02x}{bb:02x}"
            self.canvas.create_oval(px - 6, tunnel_top + 15, px + 6, tunnel_top + 27,
                                    fill=color, outline="")
            self.canvas.create_oval(px - 6, tunnel_bottom - 27, px + 6, tunnel_bottom - 15,
                                    fill=color, outline="")

        self.canvas.create_rectangle(tunnel_left, tunnel_bottom - 5, tunnel_right, tunnel_bottom + 5,
                                     fill=style["floor"], outline=style["outline"], width=1)

        progress = self.tunnel_x / SEGMENT_LENGTH
        bar_x = 200
        bar_y = HEIGHT - 35
        bar_w = WIDTH - 400
        bar_h = 10

        self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_w, bar_y + bar_h,
                                     fill="#1a1a20", outline=style["label_color"], width=2)
        self.canvas.create_rectangle(bar_x + 2, bar_y + 2,
                                     bar_x + 2 + (bar_w - 4) * progress, bar_y + bar_h - 2,
                                     fill=style["label_color"], outline="")

        self.canvas.create_text(WIDTH // 2, 40,
                                text=style["label"],
                                fill=style["label_color"], font=("Courier New", 20, "bold"))

        arrow_x = tunnel_right - 40
        arrow_y = tunnel_bottom + 60
        pulse2 = abs(math.sin(self.tick * 0.1))
        rr = int(100 + pulse2 * 155)
        arrow_color = f"#{rr:02x}{rr:02x}ff"
        self.canvas.create_polygon(arrow_x - 25, arrow_y, arrow_x + 25, arrow_y,
                                   arrow_x, arrow_y + 25,
                                   fill=arrow_color, outline="")

        self.canvas.create_text(WIDTH // 2, HEIGHT - 60,
                                text="Иди вперёд...",
                                fill=style["label_color"], font=("Courier New", 12))

        if self.has_key:
            self.canvas.create_text(WIDTH - 60, 40,
                                    text="🔑",
                                    fill="#ffe066", font=("Courier New", 24, "bold"))

    def draw_tunnel_terminal(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#08080c", outline="")

        for i in range(0, HEIGHT, 40):
            shade = 25 + int(5 * math.sin(i * 0.1 + self.tick * 0.05))
            self.canvas.create_line(0, i, WIDTH, i, fill=f"#{shade:02x}{shade:02x}{shade + 3:02x}", width=1)

        if self.code_solved:
            door_color = "#1a3a1a"
            door_outline = "#8aff8a"
        else:
            door_color = "#2a1a1a"
            door_outline = "#5a3a3a"

        door_w = 260
        door_h = 260
        door_x = WIDTH // 2 - door_w // 2
        door_y = 110

        self.canvas.create_rectangle(door_x, door_y, door_x + door_w, door_y + door_h,
                                     fill=door_color, outline=door_outline, width=4)

        lock_cx = door_x + door_w // 2
        lock_cy = door_y + door_h // 2 - 30
        lock_color = "#8aff8a" if self.code_solved else "#5a3a3a"
        self.canvas.create_rectangle(lock_cx - 35, lock_cy - 25, lock_cx + 35, lock_cy + 35,
                                     fill="#1a1a20", outline=lock_color, width=3)
        self.canvas.create_arc(lock_cx - 22, lock_cy - 60, lock_cx + 22, lock_cy - 10,
                               start=0, extent=180, style="arc",
                               outline=lock_color, width=4)
        self.canvas.create_oval(lock_cx - 8, lock_cy - 8, lock_cx + 8, lock_cy + 8,
                                fill=lock_color, outline="")
        self.canvas.create_rectangle(lock_cx - 3, lock_cy + 5, lock_cx + 3, lock_cy + 20,
                                     fill=lock_color, outline="")

        term_x = WIDTH // 2 - 130
        term_y = HEIGHT - 110

        self.canvas.create_rectangle(term_x, term_y, term_x + 260, term_y + 80,
                                     fill="#0a0a12", outline="#8a6aff", width=3)

        if self.code_solved:
            self.canvas.create_text(term_x + 130, term_y + 40,
                                    text="ОТКРЫТО",
                                    fill="#8aff8a", font=("Courier New", 26, "bold"))
        else:
            self.canvas.create_text(term_x + 130, term_y + 18,
                                    text="ВВЕДИ КОД (2 цифры)",
                                    fill="#8a6aff", font=("Courier New", 11, "bold"))

            display = self.code_input.ljust(2, "_")
            self.canvas.create_text(term_x + 130, term_y + 50,
                                    text=" ".join(display),
                                    fill="#ffffff", font=("Courier New", 34, "bold"))

            self.canvas.create_text(term_x + 130, term_y + 92,
                                    text="Enter — проверить",
                                    fill="#5a5a8a", font=("Courier New", 10))

        self.canvas.create_text(WIDTH // 2, 40, text="ТЕРМИНАЛ",
                                fill="#8a6aff", font=("Courier New", 20, "bold"))

        exit_x = 30
        exit_y = HEIGHT - 70
        self.canvas.create_rectangle(exit_x, exit_y, exit_x + CASTLE_DOOR_W, exit_y + 55,
                                     fill="#0e0e12", outline="#5a5a6a", width=2)
        self.canvas.create_text(exit_x + CASTLE_DOOR_W // 2, exit_y + 27,
                                text="← НАЗАД", fill="#8a8a9a",
                                font=("Courier New", 12, "bold"))

        if self.code_solved:
            self.canvas.create_text(WIDTH // 2, HEIGHT - 150,
                                    text="Дверь открыта. Подойди к ней.",
                                    fill="#8aff8a", font=("Courier New", 14, "bold"))

    def draw_player(self):
        x, y = self.player_x, self.player_y
        if self.mellchar_img is not None:
            self.canvas.create_image(x, y, image=self.mellchar_img, tags="player")
        else:
            s = PLAYER_SIZE
            self.canvas.create_rectangle(x - s // 2, y - s // 2, x + s // 2, y + s // 2,
                                         fill=self.accent_color, outline="#000", width=2, tags="player")

    def draw_objective(self):
        if self.objective:
            self.canvas.create_text(WIDTH // 2, 40, text=f"ЦЕЛЬ: {self.objective}",
                                    fill="#ffe066", font=("Courier New", 16, "bold"))

    def draw_dialogue_box(self):
        if not self.dialogue_active:
            return

        box_h = 160
        box_y = HEIGHT - box_h
        self.canvas.create_rectangle(0, box_y, WIDTH, HEIGHT,
                                     fill="#000000", outline="#ffffff", width=3)

        avatar_x = 20
        avatar_y = box_y + 20
        avatar_size = 100

        self.canvas.create_rectangle(avatar_x, avatar_y,
                                     avatar_x + avatar_size, avatar_y + avatar_size,
                                     fill="#1a1a24", outline="#ffffff", width=2)

        avatar_img = self.mellchar_dialog_img
        if self.dialogue_speaker == "Тартенок" and self.mellchar2_dialog_img is not None:
            avatar_img = self.mellchar2_dialog_img
        elif self.dialogue_speaker == "Иса" and self.mellchar3_dialog_img is not None:
            avatar_img = self.mellchar3_dialog_img
        elif self.dialogue_speaker == "Ашот" and self.mellchar4_dialog_img is not None:
            avatar_img = self.mellchar4_dialog_img
        elif self.dialogue_speaker == "Джаст" and self.mellchar5_dialog_img is not None:
            avatar_img = self.mellchar5_dialog_img

        if avatar_img is not None:
            self.canvas.create_image(avatar_x + avatar_size // 2,
                                     avatar_y + avatar_size // 2,
                                     image=avatar_img)
        else:
            self.canvas.create_rectangle(avatar_x + 10, avatar_y + 10,
                                         avatar_x + avatar_size - 10, avatar_y + avatar_size - 10,
                                         fill="#8ff0ff", outline="")

        self.canvas.create_text(avatar_x + avatar_size + 20, box_y + 20,
                                text=self.dialogue_speaker,
                                fill="#ffe066", font=("Courier New", 20, "bold"),
                                anchor="nw")

        self.canvas.create_line(avatar_x + avatar_size + 20, box_y + 50,
                                WIDTH - 20, box_y + 50, fill="#444444", width=1)

        visible_text = self.dialogue_current[:self.dialogue_char_index]
        self.canvas.create_text(avatar_x + avatar_size + 20, box_y + 65,
                                text=visible_text,
                                fill="#ffffff", font=("Courier New", 16),
                                anchor="nw", width=WIDTH - avatar_size - 60,
                                justify="left")

        self.canvas.create_text(WIDTH - 20, HEIGHT - 20,
                                text="[ЛКМ / ПРОБЕЛ] далее",
                                fill="#666666", font=("Courier New", 10),
                                anchor="se")

    def draw_black_screen(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", outline="")

    def show_hint(self, text):
        self.hint_text = text
        self.hint_timer = 120

    def draw_hint(self):
        if self.hint_timer > 0:
            self.canvas.create_rectangle(WIDTH // 2 - 300, 130, WIDTH // 2 + 300, 175,
                                         fill="#000000", outline=self.accent_color, width=2)
            self.canvas.create_text(WIDTH // 2, 152, text=self.hint_text,
                                    fill=self.accent_color, font=("Courier New", 14, "bold"))

    def start_dialogue(self, lines, callback=None):
        self.dialogue_queue = list(lines)
        self.dialogue_active = True
        self.dialogue_done_callback = callback
        self.dialogue_char_index = 0
        self.dialogue_char_timer = 0
        if self.dialogue_queue:
            self.dialogue_speaker, self.dialogue_current = self.dialogue_queue.pop(0)

    def advance_dialogue(self):
        if self.dialogue_char_index < len(self.dialogue_current):
            self.dialogue_char_index = len(self.dialogue_current)
            return

        if self.dialogue_queue:
            self.dialogue_speaker, self.dialogue_current = self.dialogue_queue.pop(0)
            self.dialogue_char_index = 0
            self.dialogue_char_timer = 0
        else:
            self.dialogue_active = False
            cb = self.dialogue_done_callback
            self.dialogue_done_callback = None
            if cb:
                cb()

    def switch_location(self, new_location, title_text, spawn_x=None, spawn_y=None):
        self.location = new_location
        if spawn_x is None:
            spawn_x = WIDTH // 2
        if spawn_y is None:
            spawn_y = FLOOR_TOP + 30
        self.player_x = spawn_x
        self.player_y = spawn_y
        self.door_cooldown = 90
        self.save_game()

        if title_text:
            self.start_title(title_text, self.after_location_enter)

    def after_location_enter(self):
        if self.location == "empty_room" and not self.visited_empty_room:
            self.visited_empty_room = True
            self.save_game()
            self.start_dialogue([
                ("Крол", "мгм, тут пусто, прям пусто, но... уютно, ладно пойду дальше."),
            ], None)

        elif self.location == "tartenok_room" and not self.visited_tartenok_room:
            self.visited_tartenok_room = True
            self.save_game()
            self.start_dialogue([
                ("Крол", "(мысли) ТАРТ? а он то тут почему... что за бред..."),
                ("Крол", "(мысли) он и выглядит как раньше.. похоже, я реально в другой вселенной.."),
                ("Крол", "(мысли) ладно, поговорю с \"тартом\""),
            ], self.after_tartenok_first_dialogue)

    def after_tartenok_first_dialogue(self):
        self.root.after(500, self.start_tartenok_talk)

    def start_tartenok_talk(self):
        if self.tartenok_talked:
            return
        self.tartenok_talked = True
        self.save_game()
        self.start_dialogue([
            ("Крол", "тартенок... привет?"),
            ("Тартенок", "ты..... кто?"),
            ("Крол", "ээам.. крол."),
            ("Тартенок", "КРОЛ? ЧТО С ТОБОЙ. разве ты не заперт на крыше?"),
            ("Крол", "..."),
            ("Крол", "(крол всё рассказал)"),
            ("Тартенок", "че......"),
            ("Крол", "ддаа.. вот так..."),
            ("Тартенок", "ты.. не мой крол?"),
            ("Крол", "да."),
            ("Тартенок", "..."),
            ("Крол", "..."),
        ], None)

    def check_door(self):
        if self.dialogue_active:
            return
        if self.black_screen:
            return
        if self.cutscene_active:
            return
        if self.title_active:
            return
        if self.door_cooldown > 0:
            return
        if self.location == "credits":
            return

        if self.location == "krol_room":
            if not self.door_opened:
                return
            if self.room_completed:
                return
            door_cx = DOOR_X + DOOR_W // 2
            door_bottom = DOOR_Y + DOOR_H
            if abs(self.player_x - door_cx) < 80 and self.player_y > door_bottom - 100:
                self.enter_door()

        elif self.location == "strp_castle":
            door_w = CASTLE_DOOR_W
            left_cx = 80 + door_w // 2
            center_cx = WIDTH // 2
            right_cx = WIDTH - 80 - door_w // 2

            if abs(self.player_x - left_cx) < 45:
                self.switch_location("tartenok_room", "Комната Тартенка",
                                     spawn_x=WIDTH // 2, spawn_y=FLOOR_TOP + 25)
            elif abs(self.player_x - center_cx) < 45:
                self.tunnel_stage = 0
                self.tunnel_x = 0
                self.switch_location("tunnel", "Туннель",
                                     spawn_x=WIDTH // 2, spawn_y=FLOOR_TOP + 30)
            elif abs(self.player_x - right_cx) < 45:
                self.switch_location("empty_room", "Пустая комната",
                                     spawn_x=WIDTH // 2, spawn_y=FLOOR_TOP + 25)

        elif self.location == "tartenok_room":
            if self.player_y > HEIGHT - 80 and self.player_x < 220:
                left_cx = 80 + CASTLE_DOOR_W // 2
                self.switch_location("strp_castle", None,
                                     spawn_x=left_cx, spawn_y=FLOOR_TOP + 30)

        elif self.location == "empty_room":
            if self.player_y > HEIGHT - 80 and self.player_x < 220:
                right_cx = WIDTH - 80 - CASTLE_DOOR_W // 2
                self.switch_location("strp_castle", None,
                                     spawn_x=right_cx, spawn_y=FLOOR_TOP + 30)

        elif self.location == "tunnel":
            if self.tunnel_x >= SEGMENT_LENGTH:
                self.tunnel_x = 0
                self.player_x = 100
                self.door_cooldown = 60
                self.tunnel_stage += 1
                self.save_game()

                if self.tunnel_stage == 3:
                    self.location = "tunnel_terminal"
                    self.player_x = WIDTH // 2
                    self.player_y = FLOOR_TOP + 30
                    self.code_hint_shown = False
                    self.show_hint("Ты дошёл до терминала")
                elif self.tunnel_stage == 5:
                    self.start_minigame()
                    return
            elif self.tunnel_x < -50:
                self.switch_location("strp_castle", None,
                                     spawn_x=WIDTH // 2, spawn_y=FLOOR_TOP + 30)

        elif self.location == "tunnel_terminal":
            if self.code_solved:
                door_cx = WIDTH // 2
                if abs(self.player_x - door_cx) < 80 and self.player_y < FLOOR_TOP + 60:
                    self.tunnel_stage = 3
                    self.tunnel_x = 0
                    self.switch_location("tunnel", "Туннель — после терминала",
                                         spawn_x=WIDTH // 2, spawn_y=FLOOR_TOP + 30)
                    if not self.post_terminal_dialogue_shown:
                        self.post_terminal_dialogue_shown = True
                        self.start_dialogue([
                            ("Крол", "есть, я сделал это.. так, тут опять идти.. ладно.."),
                            ("Крол", "куда я вообще иду? ну.. выбора все равно нет."),
                        ], None)
            else:
                if self.player_y > HEIGHT - 80 and self.player_x < 220:
                    self.switch_location("strp_castle", None,
                                         spawn_x=WIDTH // 2, spawn_y=FLOOR_TOP + 30)

        elif self.location == "boss_isa":
            if self.post_boss_phase == 2 and not self.post_boss_actors_visible:
                door_cx = WIDTH - 120
                door_cy = 220
                if (abs(self.player_x - door_cx) < 90
                        and abs(self.player_y - door_cy) < 130):
                    self.start_universe_break()

    def enter_door(self):
        self.room_completed = True
        self.objective = None
        self.save_game()
        self.black_screen = True
        self.black_timer = 0
        self.scream_shown = False

    def update_story(self):
        if self.location != "krol_room":
            return
        if self.title_active:
            return
        if self.dialogue_active:
            return
        if self.room_completed:
            return
        if self.black_screen:
            return
        if self.cutscene_active:
            return
        if self.story_stage > 0:
            return
        if self.final_dialogue_shown:
            return

        self.story_timer += 1

        if self.story_timer >= STORY_DELAY:
            self.story_stage = 1
            self.start_dialogue([
                ("Крол", "хмм. ни в стрп ни в стр ни в конторах актива нет,"),
                ("Крол", "хомяка покормил, в комп не хочу.. чем бы заняться.."),
            ], self.after_first_dialogue)

    def after_first_dialogue(self):
        self.root.after(1500, self.second_dialogue)

    def second_dialogue(self):
        if self.state != "game":
            return
        self.start_dialogue([
            ("Крол", "пойду на кухню приготовлю что нибудь."),
        ], self.after_second_dialogue)

    def after_second_dialogue(self):
        self.story_stage = 2
        self.door_opened = True
        self.objective = "Сделать еду на кухне"

    def after_scream_dialogue(self):
        self.start_cutscene("KroloSceneFRST", KROLO_SCENE_DURATION, self.after_krolo_scene)

    def after_krolo_scene(self):
        self.black_screen = False
        self.location = "strp_castle"
        self.player_x = WIDTH // 2
        self.player_y = FLOOR_TOP + 30
        self.door_cooldown = 90
        self.story_stage = 3
        self.save_game()
        self.start_title("Замок СТРП", self.after_castle_intro)

    def after_castle_intro(self):
        self.story_stage = 3
        self.start_dialogue([
            ("Крол", "почему так болит голова... что это было?!?!?!?!"),
            ("Крол", "я... телепортировался. или я.. в другой вселенной?"),
            ("Крол", "на другой планете? что это. что я."),
            ("Крол", "так, ладно, тут развилка.. схожу во все - мне надо больше знать."),
        ], None)

    def load_cutscene_frames(self, name):
        path = resource_path(name)
        if not path:
            print("[CUTSCENE] файл не найден:", name)
            return False

        ext_found = os.path.splitext(path)[1].lower()

        try:
            img = Image.open(path)
            print("[CUTSCENE] загружаю:", path)

            if ext_found == ".gif" and getattr(img, "is_animated", False):
                frames = []
                for frame in ImageSequence.Iterator(img):
                    f = frame.convert("RGBA").resize((WIDTH, HEIGHT), Image.LANCZOS)
                    frames.append(ImageTk.PhotoImage(f))
                self.cutscene_frames = frames
                durations = img.info.get("duration", 50)
                if isinstance(durations, list):
                    avg = sum(durations) / len(durations)
                else:
                    avg = durations
                self.cutscene_frame_delay = max(1, int(avg / (1000 / FPS)))
                print(f"[CUTSCENE] gif кадров: {len(frames)}, задержка: {self.cutscene_frame_delay}")
            else:
                single = img.convert("RGBA").resize((WIDTH, HEIGHT), Image.LANCZOS)
                self.cutscene_frames = [ImageTk.PhotoImage(single)]
                self.cutscene_frame_delay = 999999
                print("[CUTSCENE] статичное изображение")
            return True
        except Exception as e:
            print("[CUTSCENE] ошибка:", e)
            return False

    def start_cutscene(self, name, duration_frames, callback=None):
        self.cutscene_frames = []
        self.cutscene_frame_index = 0
        self.cutscene_frame_timer = 0
        self.cutscene_total_timer = 0
        self.cutscene_frame_delay = 999999
        self.cutscene_callback = callback
        self.cutscene_duration = duration_frames

        self.cutscene_has_file = self.load_cutscene_frames(name)
        self.cutscene_active = True
        print(f"[CUTSCENE] старт, длительность = {duration_frames} тиков ({duration_frames / FPS:.1f} сек)")

    def skip_cutscene(self):
        if not self.cutscene_active:
            return
        print("[CUTSCENE] пропуск")
        self.cutscene_active = False
        self.cutscene_frames = []
        cb = self.cutscene_callback
        self.cutscene_callback = None
        if cb:
            cb()

    def draw_cutscene(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", outline="")

        if self.cutscene_has_file and self.cutscene_frames:
            frame = self.cutscene_frames[self.cutscene_frame_index % len(self.cutscene_frames)]
            self.canvas.create_image(WIDTH // 2, HEIGHT // 2, image=frame)
        else:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 40,
                                    text="KroloSceneFRST",
                                    fill="#8ff0ff",
                                    font=("Courier New", 42, "bold"))
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20,
                                    text="[ сцена без файла ]",
                                    fill="#666666",
                                    font=("Courier New", 16))
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 60,
                                    text="положи KroloSceneFRST.gif / .png рядом с игрой",
                                    fill="#444444", font=("Courier New", 12))

        remaining = max(0, (self.cutscene_duration - self.cutscene_total_timer) // FPS)
        self.canvas.create_rectangle(WIDTH - 190, HEIGHT - 40, WIDTH - 20, HEIGHT - 15,
                                     fill="#000000", outline="#333333", width=1)
        self.canvas.create_text(WIDTH - 105, HEIGHT - 27,
                                text=f"[ПРОБЕЛ] пропустить · {remaining}с",
                                fill="#888888", font=("Courier New", 10))

    def game_loop(self):
        if self.state != "game":
            return
        self.tick += 1
        self.play_time += 1
        self.autosave_timer += 1

        if self.door_cooldown > 0:
            self.door_cooldown -= 1

        if self.tick % (FPS * 20) == 0 and not self.black_screen and not self.cutscene_active:
            self.hamster_hunger += 1

        if self.cutscene_active:
            self.cutscene_total_timer += 1

            if len(self.cutscene_frames) > 1:
                self.cutscene_frame_timer += 1
                if self.cutscene_frame_timer >= self.cutscene_frame_delay:
                    self.cutscene_frame_timer = 0
                    self.cutscene_frame_index += 1

            if self.cutscene_total_timer >= self.cutscene_duration:
                print(f"[CUTSCENE] завершена за {self.cutscene_total_timer} тиков")
                self.cutscene_active = False
                cb = self.cutscene_callback
                self.cutscene_callback = None
                if cb:
                    cb()
                self.root.after(1000 // FPS, self.game_loop)
                return

            self.clear()
            self.draw_cutscene()
            self.root.after(1000 // FPS, self.game_loop)
            return

        if self.title_active:
            self.title_timer += 1
            self.clear()
            self.draw_title()
            self.root.after(1000 // FPS, self.game_loop)
            return

        if self.black_screen:
            self.black_timer += 1
            if self.black_timer > 60 and not self.scream_shown:
                self.scream_shown = True
                self.start_dialogue([
                    ("Крол", "ЧТО ЗА-"),
                ], self.after_scream_dialogue)
            self.clear()
            self.draw_black_screen()
            self.draw_dialogue_box()
            self.root.after(1000 // FPS, self.game_loop)
            return

        if self.location == "universe_break":
            self.clear()
            self.draw_universe_break()
            self.root.after(1000 // FPS, self.game_loop)
            return

        if self.location == "credits":
            self.credits_timer += 1
            self.credits_scroll -= 1.2
            self.clear()
            self.draw_credits()
            self.root.after(1000 // FPS, self.game_loop)
            return

        if self.location == "minigame":
            self.update_minigame()

        if self.location == "boss_isa":
            self.update_boss_fight()

        if self.dialogue_active:
            self.dialogue_char_timer += 1
            if self.dialogue_char_timer >= 2:
                self.dialogue_char_timer = 0
                if self.dialogue_char_index < len(self.dialogue_current):
                    self.dialogue_char_index += 1
        else:
            can_move = True
            if self.location == "krol_room" and self.room_completed and not self.final_dialogue_shown:
                can_move = False
            if self.location == "minigame":
                can_move = False

            if can_move:
                if self.location == "tunnel":
                    if "a" in self.keys or "ф" in self.keys or "left" in self.keys:
                        self.tunnel_x -= self.player_speed
                    if "d" in self.keys or "в" in self.keys or "right" in self.keys:
                        self.tunnel_x += self.player_speed
                    if "w" in self.keys or "ц" in self.keys or "up" in self.keys:
                        self.player_y -= self.player_speed
                    if "s" in self.keys or "ы" in self.keys or "down" in self.keys:
                        self.player_y += self.player_speed
                    self.tunnel_x = max(-100, min(SEGMENT_LENGTH + 50, self.tunnel_x))
                else:
                    if "a" in self.keys or "ф" in self.keys or "left" in self.keys:
                        self.player_x -= self.player_speed
                    if "d" in self.keys or "в" in self.keys or "right" in self.keys:
                        self.player_x += self.player_speed
                    if "w" in self.keys or "ц" in self.keys or "up" in self.keys:
                        self.player_y -= self.player_speed
                    if "s" in self.keys or "ы" in self.keys or "down" in self.keys:
                        self.player_y += self.player_speed

        half = PLAYER_SIZE // 2
        if self.location != "tunnel":
            if self.location == "boss_isa":
                self.player_x = max(half, min(WIDTH - half, self.player_x))
                self.player_y = max(half, min(HEIGHT - half, self.player_y))
            elif self.location == "tunnel_terminal":
                self.player_x = max(half, min(WIDTH - half, self.player_x))
                self.player_y = max(FLOOR_TOP - 80, min(HEIGHT - half, self.player_y))
            else:
                self.player_x = max(half, min(WIDTH - half, self.player_x))
                self.player_y = max(FLOOR_TOP + 20, min(HEIGHT - half, self.player_y))

        if self.autosave_timer >= FPS * 5:
            self.autosave_timer = 0
            self.save_game()

        if (self.location == "tunnel_terminal"
                and not self.code_hint_shown
                and not self.dialogue_active
                and self.player_y > HEIGHT - 120
                and abs(self.player_x - WIDTH // 2) < 200):
            self.code_hint_shown = True
            self.start_dialogue([
                ("Крол", "хм.. кода нигде не было, но тут всего 2 цифры угадать, думаю, смогу подобрать на угад."),
            ], None)

        self.update_story()
        self.check_door()

        if self.hint_timer > 0:
            self.hint_timer -= 1

        self.clear()

        if self.location == "krol_room":
            self.draw_room()
        elif self.location == "strp_castle":
            self.draw_castle()
        elif self.location == "tartenok_room":
            self.draw_tartenok_room()
        elif self.location == "empty_room":
            self.draw_empty_room()
        elif self.location == "tunnel":
            self.draw_tunnel()
        elif self.location == "tunnel_terminal":
            self.draw_tunnel_terminal()
        elif self.location == "minigame":
            self.draw_minigame()
        elif self.location == "key_door_room":
            self.draw_key_door_room()
        elif self.location == "boss_isa":
            self.draw_boss_fight()

        if self.location not in ("minigame", "boss_isa"):
            self.draw_player()

        self.draw_objective()
        self.draw_hint()
        self.draw_dialogue_box()

        self.root.after(1000 // FPS, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = SkibidiGame(root)
    root.mainloop()
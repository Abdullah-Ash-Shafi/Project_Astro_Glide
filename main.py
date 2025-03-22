from kivy import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

import random
from sys import platform
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Line, Quad, Triangle, Rectangle
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout) :
    from transforms import transform, transform_perspective, transform_2D
    from user_actions import on_touch_up, on_touch_down, keyboard_closed, on_keyboard_up, on_keyboard_down
    #zoom_factor = NumericProperty(1.5)  # Adjust this value for zooming

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty()
    perspective_point_y = NumericProperty()

    V_NB_LINES = 10
    V_LINES_SPACING = 0.30     # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 8
    H_LINES_SPACING = 0.20    # percentage in screen height
    horizontal_lines = []

    SPEED_Y = 0.7
    current_offset_y = 0

    SPEED_X = 3
    current_speed_x = 0
    current_offset_x = 0
    current_y_loop = 0

    NB_TILES = 10
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0,0), (0,0), (0,0)]

    state_game_over = False
    state_game_has_started = False

    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_title = StringProperty("START")
    score = NumericProperty(0)
    Score_txt = StringProperty("Score : " + "0")

    z_a = NumericProperty(0)
    score_font_size = NumericProperty(0)
    img_opacity = NumericProperty(1)
    opacity_controller = 0.006
    angle = NumericProperty(0)
    background_img = StringProperty("")

    # TO DO : Make an Array , Where all image will be maintained
    bg_images = ["images/bg101.webp", "images/bg102.jpg", "images/bg103.jpg", "images/bg108.jpg"]

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None


    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.init_audio()
        self.reset_game()


        if self.is_desktop() :
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down = self.on_keyboard_down)
            self.keyboard.bind(on_key_up = self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0/60.0)
        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = .6


    def reset_game(self) :
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.z_a = 0
        self.img_opacity = 1
        self.SPEED_Y = 0.7
        self.score = 0
        self.Score_txt = "Score : " + "0"
        self.background_img = self.bg_images[0]

        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()

        self.state_game_over = False


    def is_desktop(self) :
        if platform in ('linux', 'win32', 'macosx') :
            return True
        return False


    def init_vertical_lines(self):
        with self.canvas :
            Color(1,1,1,0.5)
            for i in range(self.V_NB_LINES) :
                self.vertical_lines.append(Line())


    def init_tiles(self) :
        with self.canvas :
            Color(1, 1, 1, 0.5)
            for _ in range(self.NB_TILES):
                self.tiles.append(Quad())


    def init_ship(self) :
        with self.canvas :
            Color(0, 0, 0)
            self.ship = Triangle()



    def update_ship(self) :
        center_x = self.width/2
        base_y = self.height * self.SHIP_BASE_Y
        ship_width = self.SHIP_WIDTH * self.width
        ship_height = self.height * self.SHIP_HEIGHT

        self.ship_coordinates[0] = center_x - ship_width / 2, base_y
        self.ship_coordinates[1] = center_x, base_y + ship_height
        self.ship_coordinates[2] = center_x + ship_width/2, base_y

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]



    def check_ship_collision(self):
        for ti_x, ti_y in self.tiles_coordinates :
            if ti_y > self.current_y_loop+1 :
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y) :
                return True
        return False



    def check_ship_collision_with_tile(self, ti_x, ti_y) :
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)
        for px, py in self.ship_coordinates :
            if xmin <= px <= xmax and ymin <= py <= ymax :
                return True
        return False


    def pre_fill_tiles_coordinates(self) :
        for i in range(10) :
            self.tiles_coordinates.append((0, i))


    def generate_tiles_coordinates(self) :
        last_tile_x, last_tile_y = 0, 0

        for i in reversed(range(len(self.tiles_coordinates))) :
            if self.tiles_coordinates[i][1] < self.current_y_loop :
                del self.tiles_coordinates[i]



        if len(self.tiles_coordinates) > 0 :
            last_tile_x, last_tile_y = self.tiles_coordinates[-1]
            last_tile_y += 1

        for i in range(len(self.tiles_coordinates), self.NB_TILES) :

            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1

            r = random.randint(0,2)

            """
            r = 0 --> straight
            r = 1 --> right
            r = 2 --> left
            """
            if last_tile_x == start_index :
                r = 1
            elif last_tile_x == (end_index-1):
                r = 2

            self.tiles_coordinates.append((last_tile_x, last_tile_y))
            if r == 1 :
                last_tile_x += 1
                self.tiles_coordinates.append((last_tile_x, last_tile_y))
                last_tile_y += 1
                self.tiles_coordinates.append((last_tile_x, last_tile_y))

            if r == 2 :
                last_tile_x -= 1
                self.tiles_coordinates.append((last_tile_x, last_tile_y))
                last_tile_y += 1
                self.tiles_coordinates.append((last_tile_x, last_tile_y))

            last_tile_y += 1


    def get_tile_coordinates(self, ti_x, ti_y) :
        ti_y -= self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x,y


    def update_tiles(self) :
        for i in range(self.NB_TILES) :
            ti_x, ti_y = self.tiles_coordinates[i]
            tile = self.tiles[i]

            xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
            xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]


    def get_line_x_from_index(self, index) :
        central_line_x = self.perspective_point_x
        spacing_x = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset*spacing_x + self.current_offset_x
        return int(line_x)


    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = int(index * spacing_y - self.current_offset_y)
        return int(line_y)

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2) + 1

        for i in range(start_index, start_index + self.V_NB_LINES) :
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]


    def init_horizontal_lines(self):
        with self.canvas :
            Color(1,1,1,0.5)
            for i in range(self.H_NB_LINES) :
                self.horizontal_lines.append(Line())


    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        x_left = self.get_line_x_from_index(start_index)
        x_right = self.get_line_x_from_index(end_index)

        for i in range(0, self.H_NB_LINES) :
            line_y = self.get_line_y_from_index(i)

            x1, y1 = self.transform(x_left, line_y)
            x2, y2 = self.transform(x_right, line_y)

            self.horizontal_lines[i].points = [x1, y1, x2, y2]


    def update(self, dt) :
        self.score_font_size = int(self.size[0]*20.0/700)
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        spacing_y = self.H_LINES_SPACING * self.height

        if not self.state_game_over and self.state_game_has_started :
            speed_y = self.SPEED_Y * self.height/100
            self.current_offset_y += speed_y * time_factor

            speed_x = self.current_speed_x * self.width/100
            self.current_offset_x += speed_x * time_factor

            self.z_a += 0.11
            #if self.z_a > 400 :
            #self.angle += 0.1




            while self.current_offset_y >= spacing_y :
                self.current_offset_y = 0
                self.current_y_loop += 1
                self.score = self.current_y_loop # set score
                self.Score_txt = "Score : " + str(self.current_y_loop)
                self.generate_tiles_coordinates()

                # Image Opacity Controlling
                if self.current_y_loop > 20:
                    self.img_opacity -= self.opacity_controller

                # Speed Increasing
                if self.current_y_loop == 20:
                    self.SPEED_Y *= 2

                # Background Image Changing
                if self.current_y_loop == 200 :
                    # self.background_img = self.bg_images[1]
                    # self.background_img = "images/bg109.webp"
                    self.background_img = "images/bg110.png"
                    self.opacity_controller *= -1
                    self.z_a = 0


            if not self.check_ship_collision() :
                # print("|_G_A_M_E__O_V_E_R_|")
                self.menu_title = "G  A  M  E    O  V  E  R"
                self.menu_button_title = "RESTART"
                self.state_game_over = True
                self.menu_widget.opacity = 1
                self.sound_music1.stop()
                self.sound_gameover_impact.play()
                Clock.schedule_once(self.play_game_over_voice_sound, 3)


    def play_game_over_voice_sound(self, dt) :
        if self.state_game_over :
            self.sound_gameover_voice.play()


    def on_menu_button_pressed(self) :
        if self.state_game_over :
            self.sound_gameover_impact.stop()
            self.sound_restart.play()
        else :
            self.sound_begin.play()
        #self.sound_music1.loop = True
        self.sound_music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        # print("op")

class GalaxyApp(App) :
    pass

GalaxyApp().run()
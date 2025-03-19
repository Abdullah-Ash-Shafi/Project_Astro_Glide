from sys import platform
from kivy.app import App
from kivy.graphics import Color, Line
from kivy.core.window import Window
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget



class MainWidget(Widget) :
    perspective_point_x = NumericProperty()
    perspective_point_y = NumericProperty()

    V_NB_LINES = 8
    V_LINES_SPACING = 0.20     # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 8
    H_LINES_SPACING = 0.15    # percentage in screen height
    horizontal_lines = []

    SPEED_Y = 6
    current_offset_y = 0

    SPEED_X = 6
    current_speed_x = 0
    current_offset_x = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()

        if self.is_desktop() :
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down = self.on_keyboard_down)
            self.keyboard.bind(on_key_up = self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0/60.0)


    def keyboard_closed(self) :
        self.keyboard.unbind(on_key_down = self.on_keyboard_down)
        self.keyboard.unbind(on_key_up = self.on_keyboard_up)
        self.keyboard = None


    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left' :
            self.current_speed_x = self.SPEED_X
        elif keycode[1] == 'right' :
            self.current_speed_x = -self.SPEED_X

        return True


    def on_keyboard_up(self, keyboard, keycode):
        self.current_speed_x = 0

        return True


    def is_desktop(self) :
        if platform in ('linux', 'win32', 'macosx') :
            return True
        return False

    def on_parent(self, widget, parent):
        pass


    def on_size(self, *args):
        pass


    def on_perspective_point_x(self, widget, value):
        pass


    def on_perspective_point_y(self, widget, value):
        pass


    def on_touch_down(self, touch):
        if touch.x < self.width/2 :
            self.current_speed_x = self.SPEED_X
        else :
            self.current_speed_x = -self.SPEED_X



    def on_touch_up(self, touch):
        self.current_speed_x = 0


    def init_vertical_lines(self):
        with self.canvas :
            Color(1,1,1,0.5)
            for i in range(self.V_NB_LINES) :
                self.vertical_lines.append(Line())


    def update_vertical_lines(self):
        central_line_x = int(self.width/2)
        offset = -int(self.V_NB_LINES/2) + 0.5  # Add 0.5 for making then line into the middle
        spacing_x = self.V_LINES_SPACING*self.width

        for i in range(0, self.V_NB_LINES) :
            line_x = int(central_line_x + offset*spacing_x + self.current_offset_x)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]

            offset += 1


    def init_horizontal_lines(self):
        with self.canvas :
            Color(1,1,1,0.5)
            for i in range(self.H_NB_LINES) :
                self.horizontal_lines.append(Line())


    def update_horizontal_lines(self):
        central_line_x = int(self.width/2)
        offset = -int(self.V_NB_LINES/2) + 0.5  # Add 0.5 for making then line into the middle
        spacing_x = self.V_LINES_SPACING*self.width

        half_roadspace = (-1*offset) * spacing_x

        x_left = central_line_x - half_roadspace + self.current_offset_x
        x_right = central_line_x + half_roadspace + self.current_offset_x
        spacing_y = self.H_LINES_SPACING * self.height

        for i in range(0, self.H_NB_LINES) :
            line_y = int((i+1) * spacing_y - self.current_offset_y)

            x1, y1 = self.transform(x_left, line_y)
            x2, y2 = self.transform(x_right, line_y)

            self.horizontal_lines[i].points = [x1, y1, x2, y2]


    def update(self, dt) :
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()

        spacing_y = self.H_LINES_SPACING * self.height
        self.current_offset_y += self.SPEED_Y * time_factor
        self.current_offset_x += self.current_speed_x * time_factor

        if self.current_offset_y >= spacing_y :
            self.current_offset_y = 0


    def transform(self, x, y):
        return self.transform_perspective(x, y)
        #return self.transform_2D(x, y)


    def transform_2D(self, x, y):
        return (x,y)


    def transform_perspective(self, x, y):
        lin_y = (y/self.height)*self.perspective_point_y

        if lin_y > self.perspective_point_y :
            lin_y = self.perspective_point_y

        diff_x = x-self.perspective_point_x
        diff_y = self.perspective_point_y-lin_y

        factor_y = diff_y/self.perspective_point_y
        factor_y = pow(factor_y, 2)
        """
            1 when diff_y == self.height (at the low point)
            .
            .
            0 when diff_y = 0 (self.perspective_point_y == tr_y)
        """

        tr_x = self.perspective_point_x + diff_x * factor_y
        tr_y = (1 - factor_y) * self.perspective_point_y

        return int(tr_x), int(tr_y)


class GalaxyApp(App) :
    pass

GalaxyApp().run()
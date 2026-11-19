from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
import math, random, os

WIDTH, HEIGHT = 800, 600
Window.size = (WIDTH, HEIGHT)

THEMES = [
    ((0.29, 0.68, 0.31, 1), (0.21, 0.55, 0.23, 1)),
    ((0.12, 0.58, 0.95, 1), (0.08, 0.39, 0.75, 1)),
    ((0.61, 0.15, 0.68, 1), (0.48, 0.12, 0.63, 1)),
    ((1, 0.59, 0, 1), (0.96, 0.48, 0, 1)),
    ((0.92, 0.25, 0.47, 1), (0.76, 0.09, 0.35, 1)),
    ((0, 0.73, 0.83, 1), (0, 0.59, 0.65, 1)),
]

class SnakeGame(Widget):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.speed = 5.5
        self.control_mode = 'mouse'
        self.last_mouse_x, self.last_mouse_y = 600, 300
        self.reset_game()
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_interval(self.update, 1/60.0)

    def reset_game(self):
        self.head_x, self.head_y = 400, 300
        # --- STARTING ME CHHOTA - SIRF 15 DABBE ---
        self.snake_body = [[400 - i*10, 300] for i in range(15)]
        self.base_length = 15
        self.segment_dist = 10  # Dabbe thode door-door, chipkenge nahi
        self.angle = 0.0
        self.target_angle = 0.0
        self.score = 0
        self.game_over = False
        self.control_mode = 'mouse'
        self.touch_x, self.touch_y = 600, 300  # Cursor aage rakha, Sir pe nahi
        self.food_x = random.randint(40, WIDTH-40)
        self.food_y = random.randint(40, HEIGHT-40)
        self.app_ref.hide_restart()

    def on_mouse_pos(self, window, pos):
        # Mouse thoda sa hila toh ignore karo, warna Keyboard se Mouse pe aa jata tha
        dx = pos[0] - self.last_mouse_x
        dy = pos[1] - self.last_mouse_y
        if math.sqrt(dx*dx + dy*dy) < 3:
            return
        self.last_mouse_x, self.last_mouse_y = pos[0], pos[1]
        # Agar Keyboard se chala rahe ho toh Mouse tabhi lo jab Mouse kafi door hila ho
        if self.control_mode == 'keyboard':
            # Keyboard se Mouse pe aane ke liye Mouse ko 40px se zyada hilana padega
            if math.sqrt(dx*dx + dy*dy) < 40:
                return
        self.touch_x, self.touch_y = pos[0], pos[1]
        self.control_mode = 'mouse'

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if self.game_over:
            return
        if key in (276, 97):
            self.target_angle = math.pi
            self.control_mode = 'keyboard'
        elif key in (275, 100):
            self.target_angle = 0.0
            self.control_mode = 'keyboard'
        elif key in (273, 119):
            self.target_angle = -math.pi / 2
            self.control_mode = 'keyboard'
        elif key in (274, 115):
            self.target_angle = math.pi / 2
            self.control_mode = 'keyboard'

    def on_touch_down(self, touch):
        self.touch_x, self.touch_y = touch.x, touch.y
        self.control_mode = 'mouse'
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        self.touch_x, self.touch_y = touch.x, touch.y
        self.control_mode = 'mouse'
        return super().on_touch_move(touch)

    def update(self, dt):
        if not self.game_over:
            if self.control_mode == 'mouse':
                # --- DEAD ZONE - Cursor Sir ke paas ho toh Seedha jao, Ghumo mat ---
                dx = self.touch_x - self.head_x
                dy = self.touch_y - self.head_y
                dist_to_cursor = math.sqrt(dx*dx + dy*dy)
                if dist_to_cursor > 20:  # 20px se door ho tabhi mudo
                    self.target_angle = math.atan2(dy, dx)

            diff = self.target_angle - self.angle
            if diff < -math.pi: diff += math.pi*2
            if diff > math.pi: diff -= math.pi*2
            # 0.15 se 0.22 kiya - Ab jaldi mudega, Slow nahi lagega
            self.angle += diff * 0.22

            self.head_x += math.cos(self.angle) * self.speed
            self.head_y += math.sin(self.angle) * self.speed

            if self.head_x > WIDTH: self.head_x = 0
            if self.head_x < 0: self.head_x = WIDTH
            if self.head_y > HEIGHT: self.head_y = 0
            if self.head_y < 0: self.head_y = HEIGHT

            self.snake_body.insert(0, [self.head_x, self.head_y])
            if len(self.snake_body) > self.base_length:
                self.snake_body.pop()

            for i in range(1, len(self.snake_body)):
                prev = self.snake_body[i-1]
                curr = self.snake_body[i]
                dx = curr[0]-prev[0]; dy = curr[1]-prev[1]
                dist = math.sqrt(dx*dx+dy*dy)
                if dist > self.segment_dist:
                    curr[0] = prev[0] + dx/dist*self.segment_dist
                    curr[1] = prev[1] + dy/dist*self.segment_dist

            if math.sqrt((self.head_x-self.food_x)**2 + (self.head_y-self.food_y)**2) < 20:
                self.food_x = random.randint(40, WIDTH-40)
                self.food_y = random.randint(40, HEIGHT-40)
                # --- 1 KHANA = 1 DABBA ---
                self.base_length += 1
                self.score += 1
                self.app_ref.update_labels()

            # --- POONCH CHECK - 15 se badha ke 30 kiya, beech me galat Game Over nahi hoga ---
            for i in range(30, len(self.snake_body)):
                px = self.snake_body[i][0]-self.head_x
                py = self.snake_body[i][1]-self.head_y
                if math.sqrt(px*px+py*py) < 9:
                    self.game_over = True
                    self.app_ref.on_game_over(self.score)
                    break

        self.draw()

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.10, 0.18, 0.10, 1)
            Rectangle(pos=(0,0), size=(WIDTH, HEIGHT))
            Color(1, 0.2, 0.2, 1)
            Ellipse(pos=(self.food_x-8, self.food_y-8), size=(16,16))
            theme_idx = (self.score // 50) % len(THEMES)
            SHADE_1, SHADE_2 = THEMES[theme_idx]
            for i in range(len(self.snake_body)-1, -1, -1):
                curr = self.snake_body[i]
                radius = 12
                if i > len(self.snake_body)*0.5:
                    factor = (len(self.snake_body)-i)/(len(self.snake_body)*0.5)
                    radius = 12*factor
                if radius < 3: radius = 3
                Color(* (SHADE_1 if i%2==0 else SHADE_2))
                Ellipse(pos=(curr[0]-radius, curr[1]-radius), size=(radius*2, radius*2))
                if i == 0:
                    Color(1,1,1,1)
                    lx = curr[0] + math.cos(self.angle-0.5)*7
                    ly = curr[1] + math.sin(self.angle-0.5)*7
                    Ellipse(pos=(lx-3, ly-3), size=(6,6))
                    rx = curr[0] + math.cos(self.angle+0.5)*7
                    ry = curr[1] + math.sin(self.angle+0.5)*7
                    Ellipse(pos=(rx-3, ry-3), size=(6,6))
                    Color(1, 0.34, 0.13, 1)
                    sx = curr[0] + math.cos(self.angle)*10
                    sy = curr[1] + math.sin(self.angle)*10
                    tx = curr[0] + math.cos(self.angle)*16
                    ty = curr[1] + math.sin(self.angle)*16
                    Line(points=[sx, sy, tx, ty], width=2)

class SnakeApp(App):
    def build(self):
        self.highscore = self.load_highscore()
        layout = FloatLayout()
        self.game = SnakeGame(self, size=(WIDTH, HEIGHT), pos=(0,0))
        layout.add_widget(self.game)
        self.score_label = Label(text=f'Score: 0   |   High Score: {self.highscore}',
            pos_hint={'x':0.02, 'top':0.98}, size_hint=(None, None), size=(400,40),
            font_size=22, bold=True, color=(1,1,1,1), halign='left')
        layout.add_widget(self.score_label)
        self.over_label = Label(text='', pos_hint={'center_x':0.5, 'center_y':0.6},
            size_hint=(None, None), size=(400,100), font_size=50, bold=True, color=(1,0.2,0.2,1))
        layout.add_widget(self.over_label)
        self.restart_btn = Button(text='RESTART 🔄', pos_hint={'center_x':0.5, 'center_y':0.4},
            size_hint=(None, None), size=(220, 60), font_size=22, bold=True,
            background_color=(0.2, 0.8, 0.2, 1))
        self.restart_btn.bind(on_press=self.do_restart)
        self.restart_btn.opacity = 0
        self.restart_btn.disabled = True
        layout.add_widget(self.restart_btn)
        return layout

    def load_highscore(self):
        try:
            if os.path.exists('highscore.txt'):
                with open('highscore.txt','r') as f:
                    return int(f.read().strip() or 0)
        except: pass
        return 0

    def save_highscore(self):
        try:
            with open('highscore.txt','w') as f:
                f.write(str(self.highscore))
        except: pass

    def update_labels(self):
        self.score_label.text = f'Score: {self.game.score}   |   High Score: {self.highscore}'

    def on_game_over(self, score):
        if score > self.highscore:
            self.highscore = score
            self.save_highscore()
        self.score_label.text = f'Score: {score}   |   High Score: {self.highscore}'
        self.over_label.text = 'GAME OVER!'
        self.restart_btn.opacity = 1
        self.restart_btn.disabled = False

    def hide_restart(self):
        if hasattr(self, 'over_label'):
            self.over_label.text = ''
            self.restart_btn.opacity = 0
            self.restart_btn.disabled = True
            self.update_labels()

    def do_restart(self, instance):
        self.game.reset_game()

if __name__ == '__main__':
    SnakeApp().run()

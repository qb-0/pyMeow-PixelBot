import pyMeow as pm
from configparser import ConfigParser


class Aimbot:
    def __init__(self):
        self.config = dict()
        self.region = dict()
        self.enemy_in_fov = bool()
        self.paused = bool()
        self.colors = {
            "blue": pm.get_color("skyblue"),
            "red": pm.get_color("red"),
            "orange": pm.get_color("orange"),
        }

    def read_config(self):
        c = ConfigParser()
        c.read("config.ini")
        try:
            self.config = {
                "fps": c.getint("Main", "fps"),
                "draw_fps": c.getboolean("Main", "draw_fps"),
                "color": pm.get_color(c.get("Main", "color")),
                "similarity": c.getint("Main", "similarity"),
                "fov": c.getint("Main", "fov"),
                "pause_btn": c.getint("Main", "pause_btn"),
                "autoaim": c.getboolean("Aimbot", "autoaim"),
                "aimkey": c["Aimbot"]["aimkey"],
                "mark_color": pm.get_color(c.get("Aimbot", "mark_color")),
                "smooth": c.getint("Aimbot", "smooth"),
            }
        except Exception as e:
            quit(f"config.ini missing or invalid ({e})")

    def run(self):
        pm.overlay_init(fps=self.config["fps"])
        self.region = {
            "x": pm.get_screen_width() // 2 - self.config["fov"] // 2,
            "y": pm.get_screen_height() // 2 - self.config["fov"] // 2,
        }
        self.main_loop()

    def main_loop(self):
        while pm.overlay_loop():
            pixel = self.scan_pixel()
            self.enemy_in_fov = len(pixel) > 10
            pm.begin_drawing()
            if self.config["draw_fps"]:
                pm.draw_fps(0, 0)
            self.draw_fov()
            self.check_pause()
            if not self.paused:
                if self.enemy_in_fov:
                    bounds = self.calc_bounds(pixel)
                    self.draw_bounds(bounds)
                    aim_point = self.calc_aim_point(bounds)
                    if self.config["autoaim"]:
                        self.aim(aim_point, self.config["smooth"])
                    elif pm.mouse_pressed(self.config["aimkey"]):
                        self.aim(aim_point, self.config["smooth"])
            else:
                pm.draw_text(
                    text="Pause",
                    posX=pm.get_screen_width() // 2 - pm.measure_text("Pause", 20) // 2,
                    posY=(pm.get_screen_height() // 2) - 10,
                    fontSize=20,
                    color=self.colors["orange"]
                )
            pm.end_drawing()

    def draw_fov(self):
        pm.draw_rectangle_rounded_lines(
            posX=self.region["x"],
            posY=self.region["y"],
            width=self.config["fov"],
            height=self.config["fov"],
            roundness=0.1,
            segments=5,
            color=self.colors["red"] if self.enemy_in_fov else self.colors["blue"],
            lineThick=1.2
        )

    def scan_pixel(self):
        return list(pm.pixel_search_colors(
            x=self.region["x"],
            y=self.region["y"],
            width=self.config["fov"],
            height=self.config["fov"],
            colors=[self.config["color"]],
            similarity=self.config["similarity"]
        ))
    
    def calc_bounds(self, pixel):
        minX, minY = float("inf"), float("inf")
        maxX, maxY = float("-inf"), float("-inf")

        for p in pixel:
            minX = min(minX, p["x"])
            minY = min(minY, p["y"])
            maxX = max(maxX, p["x"])
            maxY = max(maxY, p["y"])

        return {"x": minX, "y": minY, "width": maxX - minX, "height": maxY - minY}

    def draw_bounds(self, bounds):
        pm.draw_rectangle_lines(
            posX=self.region["x"] + bounds["x"],
            posY=self.region["y"] + bounds["y"],
            width=bounds["width"],
            height=bounds["height"],
            color=self.config["mark_color"],
            lineThick=1.2,
        )

    def calc_aim_point(self, bounds):
        point = {
            "x": self.region["x"] + bounds["x"] + bounds["width"] // 2,
            "y": self.region["y"] + bounds["y"] + bounds["height"] // 2
        }
        pm.draw_circle(
            centerX=point["x"],
            centerY=point["y"],
            radius=5,
            color=self.config["mark_color"]
        )
        return point

    def aim(self, point, smooth):
        """
        This might require a mouse driver depending on the game
        """
        pm.mouse_move(
            x=(point["x"] - pm.get_screen_width() // 2) // smooth,
            y=(point["y"] - pm.get_screen_height() // 2) // smooth,
            relative=True
        )

    def check_pause(self):
        if pm.key_pressed(self.config["pause_btn"]):
            self.paused = not self.paused


if __name__ == "__main__":
    aimbot = Aimbot()
    aimbot.read_config()
    aimbot.run()
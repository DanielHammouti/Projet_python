import time
import math
from Settings.setup import Resources
from Controller.init_assets import draw_hitbox, HALF_TILE_SIZE
from Controller.isometric_utils import tile_to_screen
from Controller.drawing import draw_healthBar
import pygame

class Entity:
    id = 0
    def __init__(
        self, 
        x, 
        y, 
        team, 
        acronym, 
        size, 
        max_hp, 
        cost=Resources(food=0, gold=0, wood=0),
        walkable=False,
        hitbox=0
    ):
        self.x = x
        self.y = y
        self.team = team
        self.acronym = acronym
        self.size = size
        self.max_hp = max_hp
        self.cost = cost
        self.walkable = walkable
        
        self.hp = max_hp
        self.hitbox = hitbox if hitbox > 0 else size/2
        self.last_damage_time = 0
        self.last_clicked_time = 0

        self.state = 0
        self.current_frame = 0
        self.frame_duration = 0
        self.cooldown_frame = None

        self.death_timer = 0
        self.death_duration = 5

        self.entity_id = Entity.id
        Entity.id += 1

    def isAlive(self):
        if self.hp > 0:
            return True
        return False

    def notify_damage(self):
        self.last_damage_time = time.time()

    def notify_clicked(self):
        self.last_clicked_time = time.time()

    def should_draw_health_bar(self):
        if not hasattr(self, 'hp') or self.hp <= 0 or self.max_hp is None or self.max_hp <= 0:
            return False
        current_time = time.time()
        return ((current_time - self.last_damage_time) < self.HEALTH_BAR_DISPLAY_DURATION) or \
               ((current_time - self.last_clicked_time) < self.HEALTH_BAR_DISPLAY_DURATION)

    def get_health_ratio(self):
        """Returns the ratio between current HP and max HP."""
        if not self.max_hp:
            return 0
        return max(0.0, self.hp / self.max_hp)

    def display_hitbox(self, screen, screen_width, screen_height, camera):
        corner_distance = self.size / 2.0
        corners = [
            (self.x - corner_distance, self.y - corner_distance),
            (self.x - corner_distance, self.y + corner_distance),
            (self.x + corner_distance, self.y + corner_distance),
            (self.x + corner_distance, self.y - corner_distance)
        ]
        
        screen_corners = []
        for corner in corners:
            x_screen, y_screen = tile_to_screen(
                corner[0], 
                corner[1], 
                HALF_TILE_SIZE, 
                HALF_TILE_SIZE / 2, 
                camera, 
                screen_width, 
                screen_height
            )
            screen_corners.append((x_screen, y_screen))
        
        draw_hitbox(screen, screen_corners, camera.zoom)

    def display_range(self, screen, screen_width, screen_height, camera):
        if hasattr(self, 'attack_range') and self.attack_range:
            center = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
            range_iso = self.attack_range / math.cos(math.radians(45))
            width =  range_iso * camera.zoom * HALF_TILE_SIZE 
            height = range_iso * camera.zoom * HALF_TILE_SIZE / 2
            x = center[0] - width // 2
            y = center[1] - height // 2 
            pygame.draw.ellipse(screen, (255, 0, 0), (x, y, width, height), 1)
            #pygame.draw.rect(screen, (0, 255, 0), (x, y, width, height), 1)

    def display_healthbar(self, screen, screen_width, screen_height, camera, color=(0,200,0)):
        """Displays the entity's health bar above its position."""
        if self.hp <= 0 or not self.max_hp:
            return  # do not draw if dead or max_hp is invalid
        
        ratio = self.get_health_ratio()
        if ratio <= 0.0:
            return
        
        # Screen coordinates
        sx, sy = tile_to_screen(
            self.x, 
            self.y, 
            HALF_TILE_SIZE, 
            HALF_TILE_SIZE / 2, 
            camera, 
            screen_width, 
            screen_height
        )

        draw_healthBar(screen, sx, sy, ratio, color)
import math
import pygame
import random
from AiUtils.aStar import a_star
from Entity.Entity import Entity
from Entity.Building import Building
from Settings.setup import FRAMES_PER_UNIT, HALF_TILE_SIZE,TILE_SIZE, ALLOWED_ANGLES, ATTACK_RANGE_EPSILON, UNIT_HITBOX
from Controller.isometric_utils import tile_to_screen, get_direction, get_snapped_angle, normalize
from Controller.init_assets import draw_sprite, draw_hitbox, draw_path

class Unit(Entity):
    def __init__(
        self,
        x,
        y,
        team,
        acronym,
        max_hp,
        cost,
        attack_power,
        attack_range,
        attack_speed,
        speed,
        training_time
        ):
        super().__init__(x=x, y=y, team=team, acronym=acronym, size=1, max_hp=max_hp, cost=cost, walkable=True, hitbox=UNIT_HITBOX)
        
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.attack_speed = attack_speed
        self.attack_timer = 0
        self.follow_timer = 0
        self.target = None
        
        self.speed = speed
        self.training_time = training_time
        self.path = []
        self.collision_timer = 0

        self.frames = FRAMES_PER_UNIT
        self.direction = 0

    # ---------------- Update Unit ---------------
    def update(self, game_map, dt):
        if self.isAlive():
            self.setIdle()
            self.seekAttack(game_map, dt)
            self.seekCollision(game_map, dt)
            self.seekMove(game_map, dt)
        else:
            self.death(game_map, dt)

    # ---------------- Controller ----------------
    def setIdle(self):
        if self.state !=0:
            self.state = 0
        self.cooldown_frame = None

    def set_target(self, target):
        if target and target.team != None and target.isAlive() and target.entity_id != self.entity_id and target.team != self.team:
            self.target = target
            return
        self.target = None

    def kill(self):
        self.state = 3
        self.cooldown_frame = None
        self.target = None
        self.path = []
        self.current_frame = 0
        self.hp = 0

    # ---------------- Move Logic ----------------
    def seekMove(self, game_map, dt, ALLOWED_ANGLES=ALLOWED_ANGLES):
        if self.path:
            self.state = 1

            target_tile = self.path[0]        
            snapped_angle = get_snapped_angle(((self.x, self.y)), (target_tile[0], target_tile[1]))
            self.direction = get_direction(snapped_angle)
            diff = [target_tile[0] - self.x, target_tile[1] - self.y]
            diff = normalize(diff)
            if diff:
                step = [component * dt *  self.speed for component in diff]

            self.x += step[0]
            self.y += step[1]

            dx = target_tile[0] - self.x
            dy = target_tile[1] - self.y
                
            if abs(dx) <= abs(step[0]) and abs(dy) <= abs(step[1]):
                self.path.pop(0)
                game_map.remove_entity(self)
                game_map.add_entity(self, self.x, self.y)

            return self.path

    def seekCollision(self, game_map, dt):
        if not self.path:
            rounded_position = (round(self.x), round(self.y))
            entities = game_map.grid.get(rounded_position, None)
            if entities:
                for entity in entities:
                    if entity.entity_id != self.entity_id:
                        distance = math.dist((entity.x, entity.y), (self.x, self.y))
                        hitbox_difference = distance - abs(self.hitbox  + entity.hitbox)
                        if hitbox_difference < 0:
                            diff = [self.x - entity.x, self.y - entity.y]
                            diff = normalize(diff)
                            if diff:
                                scaled_diff = [component * self.hitbox/2 for component in diff]
                                self.path.insert(0, (self.x + scaled_diff[0], self.y + scaled_diff[1]))
            return True

    # ---------------- Attack Logic ----------------
    def seekAttack(self, game_map, dt):
        if self.target and self.target.isAlive():
            distance = math.dist((self.x, self.y), (self.target.x, self.target.y)) - self.target.hitbox - self.attack_range

            if distance <= 0 :
                self.state = 2
                self.direction = get_direction(get_snapped_angle((self.x, self.y), (self.target.x, self.target.y))) 
                if self.attack_timer == 0:
                    self.current_frame = 0
                    self.path = []
                
                elif self.current_frame == self.frames - 1:
                    self.cooldown_frame = self.current_frame
                    
                self.attack_timer += dt
                if self.attack_timer >= self.attack_speed:
                    self.target.hp -= self.attack_power
                    self.attack_timer = 0
                    self.cooldown_frame = None
            else :
                if self.path:
                    self.path = [self.path[0]] + a_star(self, (round(self.target.x), round(self.target.y)), game_map)
                else:
                    self.path = a_star(self, (round(self.target.x), round(self.target.y)), game_map)

                self.attack_timer = 0
        else: 
            self.target = None

    # ---------------- Death Logic ----------------
    def death(self, game_map, dt):
        if self.death_timer == 0:
            self.kill()
        
        if self.current_frame == self.frames - 1 and self.state == 3:
            self.cooldown_frame = self.current_frame
        
        if self.death_timer > self.death_duration and self.state == 3:
            self.state = 4
            self.current_frame = 0
            self.cooldown_frame = None

        if self.state == 4 and  self.current_frame == self.frames - 1:
            self.state = 7
        self.death_timer+=dt

    # ---------------- Display Logic ----------------
    def display(self, screen, screen_width, screen_height, camera, dt):
        self.frame_duration += dt
        frame_time = 1.0 / self.frames
        if self.frame_duration >= frame_time:
            self.frame_duration -= frame_time
            self.current_frame = (self.current_frame + 1) % self.frames

        if self.cooldown_frame:
            self.current_frame = self.cooldown_frame

        sx, sy = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, 'units', sx, sy, camera.zoom, state=self.state, frame=self.current_frame, direction=self.direction)

    def display_hitbox(self, screen, screen_width, screen_height, camera):
        center = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        hitbox_iso = self.hitbox / math.cos(math.radians(45))
        width =  hitbox_iso * camera.zoom * HALF_TILE_SIZE
        height = hitbox_iso * camera.zoom * HALF_TILE_SIZE / 2
        x = center[0] - width // 2
        y = center[1] - height // 2 
        pygame.draw.ellipse(screen, (255, 255, 255), (x, y, width, height), 1)
        #pygame.draw.rect(screen, (0, 0, 255), (x, y, width, height), 1)
    
    def display_path(self, screen, screen_width, screen_height, camera):
        unit_position = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        color = ((self.entity_id * 30) % 255, (self.entity_id*20) % 255, (self.entity_id*2) % 255)
        transformed_path = [unit_position, *[ tile_to_screen(x, y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height) for x, y in self.path ] ]
        draw_path(screen, unit_position, transformed_path, camera.zoom, color)
    
    def display_path(self, screen, screen_width, screen_height, camera):
        unit_position = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        color = ((self.entity_id * 30) % 255, (self.entity_id*20) % 255, (self.entity_id*2) % 255)
        transformed_path = [unit_position, *[ tile_to_screen(x, y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height) for x, y in self.path ] ]
        draw_path(screen, unit_position, transformed_path, camera.zoom, color)
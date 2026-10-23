import os

import pygame
from pygame import Surface
from pytmx import TiledMap

from temple.temple import Temple
from temple.tiled_maps import Renderer
from utils.vectors import FloorPosition


class Game(object):
    # Game Initialisation
    def __init__(self) -> None:
        self.surface: Surface = pygame.display.set_mode((320, 320), pygame.SCALED)
        self.renderer: Renderer = Renderer()
        self.running: bool = False
        self.dirty: bool = False

        self.temple: Temple = Temple()
        self.temple.generate_floor()
        print(self.temple.current_floor)
        self.current_room: FloorPosition = self.temple.current_floor.centre

    # Game Methods
    def draw(self, tiled_map: TiledMap) -> None:
        temporary_surface = pygame.Surface((320, 320))
        self.renderer.render_map(tiled_map, temporary_surface)
        pygame.transform.smoothscale(temporary_surface, self.surface.get_size(), self.surface)

        f = pygame.font.Font(pygame.font.get_default_font(), 10)
        print([door for door in self.temple.current_floor[self.current_room].doors])
        i = f.render(f"""Floor: {self.temple.floor_number}
{self.temple.current_floor[self.current_room]}
{", ".join([door.direction for door in self.temple.current_floor[self.current_room].doors if door.to.position != self.current_room])}""", True,
                     (0, 0, 0))
        self.surface.blit(i, (0, 0))

    def handle_input(self) -> None:
        try:
            event = pygame.event.wait()

            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            self.running = False
                        case pygame.K_UP:
                            self.current_room += FloorPosition(0, -1)
                            self.dirty = True
                        case pygame.K_RIGHT:
                            self.current_room += FloorPosition(1, 0)
                            self.dirty = True
                        case pygame.K_DOWN:
                            self.current_room += FloorPosition(0, 1)
                            self.dirty = True
                        case pygame.K_LEFT:
                            self.current_room += FloorPosition(-1, 0)
                            self.dirty = True
                        case pygame.K_d:
                            self.temple.generate_floor()
                            print(self.temple.current_floor)
                            self.current_room: FloorPosition = self.temple.current_floor.centre
                            self.dirty = True

        except KeyboardInterrupt:
            self.running = False

    def run(self):
        self.dirty = True
        self.running = True

        while self.running:
            self.handle_input()

            if self.dirty:
                if tiled_map := self.temple.current_floor[self.current_room].tmx_data:
                    self.draw(tiled_map)
                else:
                    self.running = False
                self.dirty = False
                pygame.display.flip()


os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
Game().run()

#Bugra Baygul 20190705005-072

import pygame
import os
class SoundManager:
    def __init__(self, muted=False):

        pygame.mixer.init()
        self.muted = muted
        self.current_music = None

        self.gameover_sound = self.loadsound("gameover.mp3")
        self.clear_sound = self.loadsound("clear.mp3")
        self.rotate_sound = self.loadsound("rotate.mp3") #that class createad to manage sound effects for different situations
        self.draw_sound = self.loadsound("draw.mp3")
        self.win_sound = self.loadsound("win.mp3")
        self.aiate_sound = self.loadsound("aiate.mp3")

    def loadsound(self, filename):

        try:
            return pygame.mixer.Sound(filename)
        except Exception as e:
            print(f"error loading {filename}:", e)
            return None

    def playsound(self, sound):

        if not self.muted and sound is not None:
            sound.play()
    def playmusic(self, filename):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0 if self.muted else 1)
            self.current_music = filename
        except Exception as e:
            print("errormusic:", e) #deneme
    def mute(self):
        self.muted = not self.muted
        pygame.mixer.music.set_volume(0 if self.muted else 1)

import pygame
import time

class Sound:
    def __init__(self):
        pygame.mixer.init(frequency=44100)
        pygame.mixer.music.load("/home/pi/Desktop/aqua-disco.mp3")
        self.coin = pygame.mixer.Sound("sound/mario_coin_sound.wav")
        self.horn = pygame.mixer.Sound("sound/air-horn-club-sample_1.wav")

    def play(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play(-1)
        
    def pause(self):
        pygame.mixer.music.pause()

    def play_turn(self):
        self.coin.play()

    def play_fail(self):
        self.horn.play()

if __name__=='__main__':
    print ('Program is starting ... ')
    snd = Sound()
    snd.play()
    time.sleep(2)
    snd.play_fail()
    time.sleep(2)
    snd.pause()
    time.sleep(2)
    snd.play()
    time.sleep(2)

# while pygame.mixer.music.get_busy() == True:
#     time.sleep(4)
#     print('playing')
#     s.play()
"""
Enhanced Audio Manager with Sound Generation
"""

import pygame
import os
import numpy as np
import wave
import struct
import math
import config


class SoundGenerator:
    """Generate sound effects programmatically"""
    
    @staticmethod
    def generate_sine_wave(frequency, duration, volume=0.5, sample_rate=44100):
        """Generate a simple sine wave"""
        num_samples = int(duration * sample_rate)
        samples = []
        
        for i in range(num_samples):
            t = i / sample_rate
            # Envelope for fade in/out
            envelope = 1.0
            if i < sample_rate * 0.01:
                envelope = i / (sample_rate * 0.01)
            elif i > num_samples - sample_rate * 0.05:
                envelope = (num_samples - i) / (sample_rate * 0.05)
            
            sample = volume * envelope * math.sin(2 * math.pi * frequency * t)
            samples.append(int(sample * 32767))
        
        return samples
    
    @staticmethod
    def generate_coin_sound():
        """Generate coin collection sound"""
        sample_rate = 44100
        duration = 0.15
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            freq = 880 + 440 * t / duration  # Rising frequency
            envelope = 1.0 - t / duration
            sample = envelope * 0.3 * math.sin(2 * math.pi * freq * t)
            sample += envelope * 0.2 * math.sin(2 * math.pi * freq * 2 * t)
            samples.append(int(sample * 32767))
        
        return samples
    
    @staticmethod
    def generate_jump_sound():
        """Generate jump sound"""
        sample_rate = 44100
        duration = 0.2
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            freq = 300 + 200 * (1 - t / duration)  # Falling then rising
            envelope = 1.0 - t / duration
            sample = envelope * 0.4 * math.sin(2 * math.pi * freq * t)
            samples.append(int(sample * 32767))
        
        return samples
    
    @staticmethod
    def generate_crash_sound():
        """Generate crash/hit sound"""
        sample_rate = 44100
        duration = 0.5
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            envelope = max(0, 1.0 - t / duration * 2)
            # White noise + low frequency
            noise = (np.random.random() - 0.5) * envelope * 0.6
            rumble = envelope * 0.3 * math.sin(2 * math.pi * 80 * t)
            samples.append(int((noise + rumble) * 32767))
        
        return samples
    
    @staticmethod
    def generate_powerup_sound():
        """Generate power-up collection sound"""
        sample_rate = 44100
        duration = 0.4
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            freq1 = 440 + 880 * t / duration
            freq2 = 660 + 440 * t / duration
            envelope = 0.8 - 0.6 * t / duration
            sample = envelope * 0.25 * math.sin(2 * math.pi * freq1 * t)
            sample += envelope * 0.25 * math.sin(2 * math.pi * freq2 * t)
            samples.append(int(sample * 32767))
        
        return samples
    
    @staticmethod
    def generate_slide_sound():
        """Generate slide sound"""
        sample_rate = 44100
        duration = 0.15
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            freq = 200 + 100 * math.sin(t * 30)
            envelope = 0.6 - 0.4 * t / duration
            sample = envelope * 0.3 * math.sin(2 * math.pi * freq * t)
            samples.append(int(sample * 32767))
        
        return samples
    
    @staticmethod
    def generate_swoosh_sound():
        """Generate lane switch swoosh sound"""
        sample_rate = 44100
        duration = 0.12
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            freq = 150 + 300 * t / duration
            envelope = 0.5 * math.sin(math.pi * t / duration)
            sample = envelope * 0.3 * math.sin(2 * math.pi * freq * t)
            # Add noise
            noise = (np.random.random() - 0.5) * envelope * 0.2
            samples.append(int((sample + noise) * 32767))
        
        return samples
    
    @staticmethod
    def generate_near_miss_sound():
        """Generate near miss sound"""
        sample_rate = 44100
        duration = 0.2
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            freq = 600 + 200 * math.sin(t * 50)
            envelope = 1.0 - t / duration
            sample = envelope * 0.25 * math.sin(2 * math.pi * freq * t)
            samples.append(int(sample * 32767))
        
        return samples
    
    @staticmethod
    def generate_mystery_sound():
        """Generate mystery box opening sound"""
        sample_rate = 44100
        duration = 0.6
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            freq1 = 440 * (1 + 0.5 * t / duration)
            freq2 = 880 * (1 + 0.5 * t / duration)
            freq3 = 1320 * (1 + 0.5 * t / duration)
            envelope = 0.7 - 0.5 * t / duration
            sample = envelope * 0.15 * math.sin(2 * math.pi * freq1 * t)
            sample += envelope * 0.15 * math.sin(2 * math.pi * freq2 * t)
            sample += envelope * 0.1 * math.sin(2 * math.pi * freq3 * t)
            samples.append(int(sample * 32767))
        
        return samples
    
    @staticmethod
    def save_wav(samples, filename, sample_rate=44100):
        """Save samples to WAV file"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with wave.open(filename, 'w') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                
                for sample in samples:
                    wav.writeframes(struct.pack('<h', max(-32767, min(32767, sample))))
            
            return True
        except Exception as e:
            print(f"Error saving WAV: {e}")
            return False


class AudioManager:
    """Enhanced audio manager with sound effects"""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.sounds = {}
        
        self._ensure_sounds_exist()
        self._load_sounds()
    
    def _ensure_sounds_exist(self):
        """Generate sound files if they don't exist"""
        sounds_dir = config.SOUNDS_PATH
        os.makedirs(sounds_dir, exist_ok=True)
        
        sound_generators = {
            'coin.wav': SoundGenerator.generate_coin_sound,
            'jump.wav': SoundGenerator.generate_jump_sound,
            'crash.wav': SoundGenerator.generate_crash_sound,
            'powerup.wav': SoundGenerator.generate_powerup_sound,
            'slide.wav': SoundGenerator.generate_slide_sound,
            'swoosh.wav': SoundGenerator.generate_swoosh_sound,
            'near_miss.wav': SoundGenerator.generate_near_miss_sound,
            'mystery.wav': SoundGenerator.generate_mystery_sound,
        }
        
        for filename, generator in sound_generators.items():
            filepath = os.path.join(sounds_dir, filename)
            if not os.path.exists(filepath):
                print(f"Generating sound: {filename}")
                samples = generator()
                SoundGenerator.save_wav(samples, filepath)
    
    def _load_sounds(self):
        """Load all sound effects"""
        sounds_dir = config.SOUNDS_PATH
        
        sound_files = ['coin', 'jump', 'crash', 'powerup', 'slide', 'swoosh', 'near_miss', 'mystery']
        
        for name in sound_files:
            filepath = os.path.join(sounds_dir, f"{name}.wav")
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                except Exception as e:
                    print(f"Error loading sound {name}: {e}")
    
    def play_sound(self, name):
        """Play a sound effect"""
        if name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(self.sfx_volume)
            sound.play()
    
    def play_music(self):
        """Play background music"""
        music_file = os.path.join(config.MUSIC_PATH, 'background.ogg')
        
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # Loop
            except Exception as e:
                print(f"Error playing music: {e}")
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))

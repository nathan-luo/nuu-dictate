import threading
import time
import wave
import pyaudio
import os
import winsound
from datetime import datetime
from pathlib import Path
import configparser
import pyperclip
from pynput import keyboard
from openai import OpenAI


class VoiceToTextApp:
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        self.audio_stream = None
        self.hotkey_listener = None
        self.openai_client = None
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        
        # Setup directories
        self.recordings_dir = Path.home() / "Documents" / "VoiceRecordings"
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Load config
        self.load_config()
        
        # Setup hotkey listener
        self.setup_hotkey_listener()
        
    def load_config(self):
        config = configparser.ConfigParser()
        config_file = Path("config.ini")
        
        if config_file.exists():
            config.read(config_file)
            api_key = config.get('openai', 'api_key', fallback=None)
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        else:
            print("Config file not found. Create config.ini with OpenAI API key.")
            
    def setup_hotkey_listener(self):
        def on_hotkey():
            if self.recording:
                self.stop_recording()
            else:
                self.start_recording()
        
        # Win+Shift+V hotkey (Windows: <cmd> = Windows key)
        hotkey = keyboard.GlobalHotKeys({
            '<cmd>+<shift>+v': on_hotkey
        })
        
        self.hotkey_listener = hotkey
        self.hotkey_listener.start()
        
    def play_sound(self, sound_type):
        """Play system sound for recording feedback"""
        try:
            if sound_type == "start":
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            elif sound_type == "stop":
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            # Fallback beep if winsound fails
            print('\a')  # Terminal bell
        
    def start_recording(self):
        if self.recording:
            return
            
        self.recording = True
        self.audio_frames = []
        
        # Play start sound
        self.play_sound("start")
        
        # Start audio stream
        self.audio_stream = self.audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        # Start recording in separate thread
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()
        
    def record_audio(self):
        while self.recording:
            try:
                data = self.audio_stream.read(self.chunk_size)
                self.audio_frames.append(data)
            except Exception as e:
                print(f"Recording error: {e}")
                break
                
    def stop_recording(self):
        if not self.recording:
            return
            
        self.recording = False
        
        # Play stop sound
        self.play_sound("stop")
        
        # Stop audio stream
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            
        # Process recording
        if self.audio_frames:
            threading.Thread(target=self.process_recording).start()
            
    def process_recording(self):
        # Generate timestamp filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        wav_filename = f"{timestamp}.wav"
        txt_filename = f"{timestamp}.txt"
        
        wav_path = self.recordings_dir / wav_filename
        txt_path = self.recordings_dir / txt_filename
        
        # Save audio file
        with wave.open(str(wav_path), 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.audio.get_sample_size(self.audio_format))
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(b''.join(self.audio_frames))
            
        # Transcribe with OpenAI Whisper
        if self.openai_client:
            try:
                with open(wav_path, 'rb') as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    
                transcription = transcript.text
                
                # Save transcription
                with open(txt_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(transcription)
                    
                # Copy transcription to clipboard and paste
                pyperclip.copy(transcription)
                pyautogui.hotkey('ctrl', 'v')  # Paste the transcription
                
            except Exception as e:
                print(f"Transcription error: {e}")
        else:
            print("OpenAI client not configured")
            
    def run(self):
        print("Voice-to-text overlay started. Press Win+Shift+V to record.")
        print("Press Ctrl+C to exit.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()
            
    def cleanup(self):
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self.audio_stream:
            self.audio_stream.close()
        self.audio.terminate()


def main():
    app = VoiceToTextApp()
    app.run()


if __name__ == "__main__":
    main()

import pygame
import re
import time
import tkinter as tk
import pyautogui

# Parse the LRC file and return the lyrics
def parse_lrc(lrc_file):
    lyrics = []
    with open(lrc_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(r'\[(\d+:\d+\.\d+)\](.*)', line)
            if match:
                time_str, text = match.groups()
                minutes, seconds = map(float, time_str.split(':'))
                timestamp = minutes * 60 + seconds
                lyrics.append((timestamp, text.strip()))
    return lyrics

# Display lyrics in a GUI window
def display_lyrics_with_ui(lyrics):
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("單依純 - 續寫.mp3")
    pygame.mixer.music.play()

    # Initialize GUI window
    window = tk.Tk()
    window.title("Lyrics Display")
    label = tk.Label(window, width=40, height=5, wraplength=2000)
    label.pack(pady=20)

    start_time = time.time()  # Record the start time of playback

    index = 0

    def update_lyrics():
        nonlocal index
        if index < len(lyrics):
            timestamp, text = lyrics[index]
            if time.time() - start_time >= timestamp:
                label.config(text=text,font=('芫荽 0.94', 32))
                index += 1

        if pygame.mixer.music.get_busy():
            window.after(100, update_lyrics)  # Update every 100 milliseconds

    update_lyrics()  # Start updating the lyrics

    window.mainloop()

if __name__ == "__main__":
    lrc_file = "單依純 - 續寫.lrc"
    lyrics = parse_lrc(lrc_file)

    display_lyrics_with_ui(lyrics)

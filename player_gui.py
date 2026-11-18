"""Song Player - tkinter GUI version (extension).

Same playlist and music code as player.py, but the window is built with tkinter:
    pygame  -> only plays the sound (pygame.mixer), no pygame window
    Pillow  -> opens/resizes the album art and converts it for tkinter (ImageTk)
    tkinter -> the window, playlist box and buttons

Layout follows tk.md: pack() for the window's own widgets,
grid() inside Frames (never both in the same container).
"""

import os
import tkinter as tk

import pygame
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# The playlist: song location, information and album art link.
# ---------------------------------------------------------------------------
playlist = [
    {
        "title": "Song One",
        "artist": "Artist One",
        "album": "Album One",
        "file": "songs/song1.mp3",
        "art": "art/song1.jpg",
    },
    {
        "title": "Song Two",
        "artist": "Artist Two",
        "album": "Album Two",
        "file": "songs/song2.mp3",
        "art": "art/song2.jpg",
    },
    {
        "title": "Song Three",
        "artist": "Artist Three",
        "album": "Album Three",
        "file": "songs/song3.mp3",
        "art": "art/song3.jpg",
    },
]

DEFAULT_ART = "download.webp"
ART_SIZE = 300

# Colors
BG = "#181a21"
PANEL = "#23262f"
TEXT = "#ebebf0"
DIM = "#8c91a0"
ACCENT = "#50c88c"
ERROR = "#e65a5a"


def full_path(relative):
    return os.path.join(BASE_DIR, relative)


def load_album_art(song):
    """Open the album art with Pillow and turn it into a tkinter image."""
    path = full_path(song["art"])
    if not os.path.exists(path):
        path = full_path(DEFAULT_ART)

    image = Image.open(path).convert("RGB")
    image.thumbnail((ART_SIZE, ART_SIZE))
    return ImageTk.PhotoImage(image)


class SongPlayerApp:
    def __init__(self, window):
        self.window = window
        self.index = None
        self.paused = False
        self.playing = False
        self.art_image = None   # keep a reference or tkinter will blank the image

        window.title("Song Player")
        window.configure(bg=BG)
        window.resizable(False, False)

        # --- Left side: album art and song info (pack inside this frame) ---
        left = tk.Frame(window, bg=BG)
        left.pack(side="left", padx=20, pady=20)

        self.art_label = tk.Label(
            left, text="No song loaded", fg=DIM, bg=PANEL,
            width=ART_SIZE, height=ART_SIZE,
            image=self._blank_image(),  # gives the label a pixel size before any art loads
            compound="center",
        )
        self.art_label.pack()

        self.status_label = tk.Label(left, text="Pick a song to start", font=("Arial", 11), fg=ACCENT, bg=BG)
        self.status_label.pack(pady=(12, 0))

        self.title_label = tk.Label(left, text="", font=("Arial", 16, "bold"), fg=TEXT, bg=BG)
        self.title_label.pack()

        self.artist_label = tk.Label(left, text="", font=("Arial", 12), fg=DIM, bg=BG)
        self.artist_label.pack()

        # --- Right side: playlist and controls ---
        right = tk.Frame(window, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        tk.Label(right, text="Playlist", font=("Arial", 18, "bold"), fg=TEXT, bg=BG).pack(anchor="w")

        self.listbox = tk.Listbox(
            right, width=34, height=len(playlist) + 2,
            font=("Arial", 13), bg=PANEL, fg=TEXT,
            selectbackground=ACCENT, selectforeground=BG,
            highlightthickness=0, bd=0, activestyle="none",
        )
        for i, song in enumerate(playlist):
            self.listbox.insert("end", f"{i + 1}. {song['title']} - {song['artist']}")
        self.listbox.pack(fill="x", pady=10)
        self.listbox.bind("<Double-Button-1>", lambda e: self.play_selected())
        self.listbox.bind("<Return>", lambda e: self.play_selected())

        # Buttons in a row, using grid() inside their own frame
        controls = tk.Frame(right, bg=BG)
        controls.pack(pady=10)

        self.buttons = {}
        for col, (name, command) in enumerate([
            ("⏮ Prev", self.previous),
            ("▶ Play", self.play_selected),
            ("⏸ Pause", self.toggle_pause),
            ("Next ⏭", self.next),
        ]):
            button = tk.Button(controls, text=name, width=8, command=command, cursor="hand2")
            button.grid(row=0, column=col, padx=4)
            self.buttons[name] = button

        tk.Label(
            right, text="Double-click a song to play it.\nSpace: pause   ←/→: previous/next",
            font=("Arial", 10), fg=DIM, bg=BG, justify="left",
        ).pack(anchor="w", pady=(10, 0))

        # Keyboard shortcuts
        window.bind("<space>", lambda e: self.toggle_pause())
        window.bind("<Right>", lambda e: self.next())
        window.bind("<Left>", lambda e: self.previous())

        window.protocol("WM_DELETE_WINDOW", self.quit)
        self.check_song_end()

    def _blank_image(self):
        self._blank = tk.PhotoImage(width=ART_SIZE, height=ART_SIZE)
        return self._blank

    # --- Music controls ---
    def play(self, index):
        self.index = index % len(playlist)
        song = playlist[self.index]
        self.paused = False

        # Show the album art as soon as the song loads
        self.art_image = load_album_art(song)
        self.art_label.config(image=self.art_image, text="")

        self.title_label.config(text=song["title"])
        self.artist_label.config(text=f"{song['artist']}  ·  {song['album']}")

        # Highlight the song in the playlist
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(self.index)
        self.listbox.see(self.index)

        path = full_path(song["file"])
        if not os.path.exists(path):
            pygame.mixer.music.stop()
            self.playing = False
            self.status_label.config(text=f"Missing file: {song['file']}", fg=ERROR)
            return

        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.playing = True
        self.status_label.config(text="Now playing", fg=ACCENT)
        self.buttons["⏸ Pause"].config(text="⏸ Pause")

    def play_selected(self):
        selection = self.listbox.curselection()
        if selection:
            self.play(selection[0])
        elif self.index is None:
            self.play(0)

    def next(self):
        self.play(0 if self.index is None else self.index + 1)

    def previous(self):
        self.play(0 if self.index is None else self.index - 1)

    def toggle_pause(self):
        if not self.playing:
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.status_label.config(text="Now playing", fg=ACCENT)
            self.buttons["⏸ Pause"].config(text="⏸ Pause")
        else:
            pygame.mixer.music.pause()
            self.status_label.config(text="Paused", fg=DIM)
            self.buttons["⏸ Pause"].config(text="▶ Resume")
        self.paused = not self.paused

    def check_song_end(self):
        """Every half second, check if the song ended and move to the next one."""
        if self.playing and not self.paused and not pygame.mixer.music.get_busy():
            self.next()
        self.window.after(500, self.check_song_end)

    def quit(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.window.destroy()


def main():
    pygame.mixer.init()   # only the sound part of pygame - tkinter makes the window
    window = tk.Tk()
    SongPlayerApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()

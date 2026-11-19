"""Song Player - pygame version.

pygame plays the music and draws the window.
Pillow (PIL) opens the album art (it can read .jpg, .png AND .webp)
and resizes it before we hand it to pygame.

Controls
    1-9 / click a song   play that song
    N or Right arrow     skip to the next song
    P or Left arrow      go back to the previous song
    Space                pause / resume
    Esc                  quit
"""

import os
import pygame
from PIL import Image

# Every path is relative to the folder this file lives in,
# so the player works no matter where you run it from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# The playlist: a list of dictionaries.
# Each song keeps its file location, its information and its album art link.
# Put your 3 mp3 files in the "songs" folder and your covers in "art",
# then change the names below to match.
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

# Used when a song's album art file can't be found.
DEFAULT_ART = "download.webp"

# Window layout
WIDTH, HEIGHT = 900, 500
ART_SIZE = 360
ART_POS = (40, 70)
LIST_X = 440
LIST_Y = 110
ROW_HEIGHT = 50

# Colors
BG = (24, 26, 33)
TEXT = (235, 235, 240)
DIM = (140, 145, 160)
ACCENT = (80, 200, 140)
HIGHLIGHT = (45, 50, 64)
ERROR = (230, 90, 90)

def full_path(relative):
    return os.path.join(BASE_DIR, relative)


def load_album_art(song):
    """Open the album art with Pillow and turn it into a pygame Surface."""
    path = full_path(song["art"])
    if not os.path.exists(path):
        path = full_path(DEFAULT_ART)

    image = Image.open(path).convert("RGB")
    # Scale to fit inside ART_SIZE x ART_SIZE without stretching
    image.thumbnail((ART_SIZE, ART_SIZE))
    return pygame.image.frombytes(image.tobytes(), image.size, "RGB")


class Player:
    def __init__(self):
        self.index = None        # which song in the playlist is loaded
        self.paused = False
        self.playing = False     # True while a real song file is loaded
        self.art = None
        self.message = "Pick a song to start"

    def play(self, index):
        """Load the song at this position in the playlist and play it."""
        self.index = index % len(playlist)   # % wraps around the end
        song = playlist[self.index]
        self.art = load_album_art(song)      # show the art when the song loads
        self.paused = False

        path = full_path(song["file"])
        if not os.path.exists(path):
            pygame.mixer.music.stop()
            self.playing = False
            self.message = f"Missing file: {song['file']}"
            return

        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.playing = True
        self.message = ""

    def next(self):
        self.play(0 if self.index is None else self.index + 1)

    def previous(self):
        self.play(0 if self.index is None else self.index - 1)

    def song_finished(self):
        """True when the current song has reached its end."""
        return self.playing and not self.paused and not pygame.mixer.music.get_busy()

    def toggle_pause(self):
        if not self.playing:
            return
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused


def draw(screen, fonts, player):
    big, medium, small = fonts
    screen.fill(BG)

    # Album art (or an empty box before anything has played)
    if player.art:
        # Center the art inside its square
        x = ART_POS[0] + (ART_SIZE - player.art.get_width()) // 2
        y = ART_POS[1] + (ART_SIZE - player.art.get_height()) // 2
        screen.blit(player.art, (x, y))
    else:
        pygame.draw.rect(screen, HIGHLIGHT, (*ART_POS, ART_SIZE, ART_SIZE), border_radius=8)
        hint = medium.render("No song loaded", True, DIM)
        screen.blit(hint, hint.get_rect(center=(ART_POS[0] + ART_SIZE // 2, ART_POS[1] + ART_SIZE // 2)))

    # Now playing
    if player.index is not None:
        song = playlist[player.index]
        status = "Paused" if player.paused else "Now playing"
        screen.blit(small.render(status, True, ACCENT), (ART_POS[0], 20))
        screen.blit(medium.render(f"{song['title']} - {song['artist']}", True, TEXT), (ART_POS[0], 440))
    if player.message:
        screen.blit(small.render(player.message, True, ERROR), (ART_POS[0], 470))

    # Playlist
    screen.blit(big.render("Playlist", True, TEXT), (LIST_X, 50))
    for i, song in enumerate(playlist):
        row = pygame.Rect(LIST_X, LIST_Y + i * ROW_HEIGHT, WIDTH - LIST_X - 30, ROW_HEIGHT - 6)
        if i == player.index:
            pygame.draw.rect(screen, HIGHLIGHT, row, border_radius=6)
        color = ACCENT if i == player.index else TEXT
        screen.blit(medium.render(f"{i + 1}. {song['title']}", True, color), (row.x + 12, row.y + 4))
        screen.blit(small.render(f"{song['artist']}  ·  {song['album']}", True, DIM), (row.x + 34, row.y + 26))

    # Controls help
    help_lines = ["1-9 / click: play song", "N / Right: next   P / Left: previous", "Space: pause   Esc: quit"]
    for i, line in enumerate(help_lines):
        screen.blit(small.render(line, True, DIM), (LIST_X, 380 + i * 22))

    pygame.display.flip()


def song_at(pos):
    """Return the playlist index under the mouse, or None."""
    x, y = pos
    if x < LIST_X:
        return None
    i = (y - LIST_Y) // ROW_HEIGHT
    if y >= LIST_Y and i < len(playlist):
        return i
    return None


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Song Player")
    fonts = (pygame.font.Font(None, 40), pygame.font.Font(None, 28), pygame.font.Font(None, 22))
    clock = pygame.time.Clock()

    player = Player()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_n, pygame.K_RIGHT):
                    player.next()
                elif event.key in (pygame.K_p, pygame.K_LEFT):
                    player.previous()
                elif event.key == pygame.K_SPACE:
                    player.toggle_pause()
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    choice = event.key - pygame.K_1
                    if choice < len(playlist):
                        player.play(choice)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                choice = song_at(event.pos)
                if choice is not None:
                    player.play(choice)

        # When a song ends, move on to the next one automatically
        if player.song_finished():
            player.next()

        draw(screen, fonts, player)
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()

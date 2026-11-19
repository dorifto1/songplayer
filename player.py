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
        "title": "MASHA FUNK",
        "artist": "MASHA",
        "album": "MASHABOMBASTICPHONKCOLLETION",
        "file": "songs/song1.mp3",
        "art": "art/song1.jpg",
    },
    {
        "title": "OLD TOWN ROAD",
        "artist": "LIL NAS X",
        "album": "7",
        "file": "songs/song2.mp3",
        "art": "art/song2.jpg",
    },
    {
        "title": "JENSEN HUANG PHONK",
        "artist": "MRLEATHERJACKET^3",
        "album": "4BADDIES ",
        "file": "songs/song3.mp3",
        "art": "art/song3.png",
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

# Volume bar (click or drag on it, or use Up/Down arrows)
VOLUME_BAR = pygame.Rect(LIST_X + 90, 462, 300, 10)
VOLUME_STEP = 0.1

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
    """Open the album art with Pillow and turn it into a pygame Surface.

    Returns None if neither the song's art nor the default art can be found.
    """
    path = full_path(song["art"])
    if not os.path.exists(path):
        path = full_path(DEFAULT_ART)
    if not os.path.exists(path):
        return None

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
        self.volume = 0.7        # 0.0 = silent, 1.0 = full
        pygame.mixer.music.set_volume(self.volume)

    def set_volume(self, volume):
        """Change the volume, kept between 0.0 and 1.0."""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

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
        pygame.mixer.music.set_volume(self.volume)
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
        hint_text = "No album art" if player.index is not None else "No song loaded"
        hint = medium.render(hint_text, True, DIM)
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
    help_lines = [
        "1-9 / click: play song",
        "N / Right: next   P / Left: previous",
        "Space: pause   Up / Down: volume   Esc: quit",
    ]
    for i, line in enumerate(help_lines):
        screen.blit(small.render(line, True, DIM), (LIST_X, 380 + i * 22))

    # Volume bar: grey track, green fill, round knob
    label = small.render(f"Volume {round(player.volume * 100)}%", True, TEXT)
    screen.blit(label, label.get_rect(midleft=(LIST_X, VOLUME_BAR.centery)))
    pygame.draw.rect(screen, HIGHLIGHT, VOLUME_BAR, border_radius=5)
    filled = VOLUME_BAR.copy()
    filled.width = round(VOLUME_BAR.width * player.volume)
    pygame.draw.rect(screen, ACCENT, filled, border_radius=5)
    pygame.draw.circle(screen, TEXT, (VOLUME_BAR.x + filled.width, VOLUME_BAR.centery), 8)

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


def volume_at(x):
    """Turn a mouse x position on the volume bar into a volume (0.0 - 1.0)."""
    return (x - VOLUME_BAR.x) / VOLUME_BAR.width


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Song Player")
    fonts = (pygame.font.Font(None, 40), pygame.font.Font(None, 28), pygame.font.Font(None, 22))
    clock = pygame.time.Clock()

    player = Player()
    dragging_volume = False

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
                elif event.key == pygame.K_UP:
                    player.set_volume(player.volume + VOLUME_STEP)
                elif event.key == pygame.K_DOWN:
                    player.set_volume(player.volume - VOLUME_STEP)
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    choice = event.key - pygame.K_1
                    if choice < len(playlist):
                        player.play(choice)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # A slightly taller hit box makes the thin bar easier to grab
                if VOLUME_BAR.inflate(16, 20).collidepoint(event.pos):
                    dragging_volume = True
                    player.set_volume(volume_at(event.pos[0]))
                else:
                    choice = song_at(event.pos)
                    if choice is not None:
                        player.play(choice)

            elif event.type == pygame.MOUSEMOTION and dragging_volume:
                player.set_volume(volume_at(event.pos[0]))

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_volume = False

            elif event.type == pygame.MOUSEWHEEL:
                player.set_volume(player.volume + event.y * VOLUME_STEP / 2)

        # When a song ends, move on to the next one automatically
        if player.song_finished():
            player.next()

        draw(screen, fonts, player)
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()

Dopus provides support for using Pydantic models as parameters for tools.

Here is an example of a random song generator that uses a nested Pydantic model as the input for the `create_song` function.

Example Output:

```
Song: Moo Melody
Genre: COUNTRY
Artist: The Pasture Poets
Album: Barnyard Ballads
Release Date: 2023-10-01
```

### Full Code

```python
import os
import dotenv
dotenv.load_dotenv()

from pydantic import BaseModel
from enum import Enum

from dopus.provider import OpenAI
from dopus.core import Agent, tool

class MusicGenre(Enum):
    ROCK = "Rock"
    POP = "Pop"
    JAZZ = "Jazz"
    CLASSICAL = "Classical"
    HIPHOP = "Hip-Hop"
    COUNTRY = "Country"
    ELECTRONIC = "Electronic"
    REGGAE = "Reggae"
    BLUES = "Blues"
    METAL = "Metal"

class RandomAlbum(BaseModel):
    """
    A random album.

    Attributes:
        name (str): The name of the album.
        release_date (str): The release date of the album.
    """
    name: str
    release_date: str

class RandomArtist(BaseModel):
    """
    A random artist.

    Attributes:
        name (str): The name of the artist.
        description (str): The description of the artist.
    """
    name: str
    description: str

class RandomSong(BaseModel):
    """
    A random song.

    Attributes:
        name (str): The name of the song.
        genre (MusicGenre): The genre of the song.
        artist (RandomArtist): The artist of the song.
        album (RandomAlbum): The album of the song.
    """
    name: str
    genre: MusicGenre
    artist: RandomArtist
    album: RandomAlbum

    def __str__(self):
        return (
            f"Song: {self.name}\n"
            f"Genre: {self.genre.name}\n"
            f"Artist: {self.artist.name}\n"
            f"Album: {self.album.name}\n"
            f"Release Date: {self.album.release_date}\n"
        )

class RandomSongGenerator(Agent):

    @tool
    def create_song(self, song: RandomSong):
        """
        Generate a random song for the user.

        Args:
            song (RandomSong): The song to create.
        """
        print(song)
        self.stop()

    def prompt(self):
        return "You are a creative AI that generates random songs for the user."

provider = OpenAI(os.getenv('OPENAI_API_KEY'))
agent = RandomSongGenerator(provider)
agent.run("Create a song about cows")
```
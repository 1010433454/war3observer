import asyncio
import mmap

from war3structs.observer import ObserverGame, ObserverPlayer
from .utils import Event

class SharedMemoryFile():
  """SharedMemoryFile class

  This opens a memory mapped file at the specified offset with the
  specified size, but takes care of having the offset conform to the
  ALLOCATIONGRANULARITY for you. Read the entire file with the data()
  method.
  """

  def __init__(self, offset, size):
    self._seek_offset = offset % mmap.ALLOCATIONGRANULARITY
    self._mmap = mmap.mmap(
      -1,
      (size + self._seek_offset),
      "War3StatsObserverSharedMemory",
      offset=(offset - self._seek_offset),
      access=mmap.ACCESS_READ)

  def data(self):
    self._mmap.seek(self._seek_offset)
    return self._mmap.read()

  def close(self):
    self._mmap.close()


class Game():
  """Game class

  A game updates the state from the observer API. It also compares
  states for you, dispatching special events when it detects in-game
  actions such as a new spell being trained.
  """

  _game_size = ObserverGame.sizeof()
  _player_size = ObserverPlayer.sizeof()

  def __init__(self):
    self._game_mm = None
    self._player_mms = []

  async def _get_game_state(self):
    parsed = ObserverGame.parse(self._game_mm.data())
    del parsed._io
    return parsed

  async def _get_player_state(self, index):
    player = ObserverPlayer.parse(self._player_mms[index].data())

    # We can do some light processing here. For now, just delete the _io
    # garbage from construct as well as the counts which we don't need.
    del player._io
    del player.heroes_count
    del player.buildings_on_map_count
    del player.upgrades_completed_count
    del player.units_on_map_count
    del player.researches_in_progress_count

    for hero in player.heroes:
      del hero._io
      del hero.abilities_count
      del hero.inventory_count

      for ability in hero.abilities:
        del ability._io

      for item in hero.inventory:
        del item._io

    for building in player.buildings_on_map:
      del building._io

    for upgrade in player.upgrades_completed:
      del upgrade._io

    for unit in player.units_on_map:
      del unit._io

    return player

  def _close_players(self):
    for mm in self._player_mms:
      mm.close()
    self._player_mms = []

  def close(self):
    """Close the game's file handles and clear events"""

    if not self._game_mm is None:
      self._game_mm.close()
      self._game_mm = None

    self._close_players()

  async def update(self):
    """Update the game state"""

    if self._game_mm is None:
      self._game_mm = SharedMemoryFile(4, self._game_size)

    game_state = await self._get_game_state()

    if not game_state['is_in_game']:
      return dict(game=game_state, players=[])

    if len(self._player_mms) != game_state['players_count']:
      self._close_players()
      for i in range(0, game_state['players_count']):
        mm = SharedMemoryFile(4+self._game_size+self._player_size*i, self._player_size)
        self._player_mms.append(mm)

    tasks = []
    for index, mm in enumerate(self._player_mms):
      tasks.append(self._get_player_state(index))

    player_states = await asyncio.gather(*tasks)

    return dict(game=game_state, players=player_states)

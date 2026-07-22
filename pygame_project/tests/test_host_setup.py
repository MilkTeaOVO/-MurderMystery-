import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.host_setup import HostSetupScene


class HostSetupSceneTests(unittest.TestCase):
    def test_load_scripts(self):
        scene = HostSetupScene(None, room_code='ROOM-001')
        self.assertGreater(len(scene.scripts), 0)
        self.assertIn('《密室杀机》', scene.scripts)

    def test_selection_change(self):
        scene = HostSetupScene(None, room_code='ROOM-001')
        scene.select_next()
        self.assertGreaterEqual(scene.selected_index, 0)

    def test_update_method_exists(self):
        scene = HostSetupScene(None, room_code='ROOM-001')
        scene.update(0.016)


if __name__ == '__main__':
    unittest.main()

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.core import Game
from game.host_setup import HostSetupScene
from game.join_setup import JoinSetupScene
from scripts.lan_comm import TcpServer


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

    def test_go_back_returns_to_previous_scene(self):
        game = Game()
        self.addCleanup(game.quit)
        home_scene = game.scene
        game.set_scene(HostSetupScene(game, room_code='ROOM-001'))
        game.go_back()
        self.assertIs(game.scene, home_scene)

    def test_joined_clients_list_exists(self):
        scene = HostSetupScene(None, room_code='ROOM-001')
        self.assertIsInstance(scene.joined_clients, list)
        self.assertGreaterEqual(len(scene.joined_clients), 1)

    def test_join_setup_scene_initializes(self):
        scene = JoinSetupScene(None, room_code='ROOM-001')
        self.assertEqual(scene.input_text, 'ROOM-001')

    def test_host_scene_starts_tcp_server(self):
        scene = HostSetupScene(None, room_code='ROOM-001')
        self.addCleanup(scene.stop_network)
        self.assertIsNotNone(scene.tcp_server)
        self.assertIsInstance(scene.tcp_server, TcpServer)


if __name__ == '__main__':
    unittest.main()

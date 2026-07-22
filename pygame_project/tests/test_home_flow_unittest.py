import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.home import HomeScene


class HomeFlowTests(unittest.TestCase):
    def test_home_buttons(self):
        scene = HomeScene(None)
        self.assertIsNotNone(scene.get_button('host'))
        self.assertIsNotNone(scene.get_button('join'))

    def test_match_state(self):
        scene = HomeScene(None)
        scene.set_mode('host')
        self.assertEqual(scene.match_state['mode'], 'host')
        scene.set_mode('join')
        self.assertEqual(scene.match_state['mode'], 'join')


if __name__ == '__main__':
    unittest.main()

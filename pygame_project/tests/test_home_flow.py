from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.home import HomeScene


def test_home_buttons():
    scene = HomeScene(None)
    assert scene.get_button('host') is not None
    assert scene.get_button('join') is not None


def test_match_state():
    scene = HomeScene(None)
    scene.set_mode('host')
    assert scene.match_state['mode'] == 'host'
    scene.set_mode('join')
    assert scene.match_state['mode'] == 'join'

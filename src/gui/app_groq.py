import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from src.core.bot_groq import CityBotGroq
from src.gui.app_pyside import ModernCityBotGUI as BaseCityBotGUI, run_qt_app


class ModernCityBotGUI(BaseCityBotGUI):
    def __init__(self, *_args, **_kwargs):
        super().__init__(
            bot_factory=CityBotGroq,
            title='CityBot Groq - Assistente Inteligente',
        )


if __name__ == '__main__':
    sys.exit(run_qt_app(ModernCityBotGUI))

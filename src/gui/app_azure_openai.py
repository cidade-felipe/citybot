import os
import sys
import tkinter as tk

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
   sys.path.append(root_path)

from src.core.bot_azure_openai import CityBotAzureOpenAI
from src.gui.app_gemini import ModernCityBotGUI as BaseCityBotGUI


class ModernCityBotGUI(BaseCityBotGUI):
   def __init__(self, root):
      super().__init__(
         root,
         bot_factory=CityBotAzureOpenAI,
         title='CityBot Azure OpenAI - Assistente Inteligente',
      )


if __name__ == '__main__':
   root = tk.Tk()
   app = ModernCityBotGUI(root)
   root.mainloop()

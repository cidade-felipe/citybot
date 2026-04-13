import argparse
import sys
import os
import tkinter as tk

# Adiciona a raiz do projeto ao sys.path para garantir que o pacote src seja encontrado
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_gui(provider):
    root = tk.Tk()
    if provider == 'gemini':
        from src.gui.app_gemini import ModernCityBotGUI
    else:
        from src.gui.app_groq import ModernCityBotGUI
    ModernCityBotGUI(root)
    root.mainloop()

def run_cli(provider):
    if provider == 'gemini':
        from src.core.bot_gemini import CityBotGemini
        bot = CityBotGemini()
    else:
        from src.core.bot_groq import CityBotGroq
        bot = CityBotGroq()
    bot.menu()

def main():
    parser = argparse.ArgumentParser(description="CityBot - Assistente Inteligente Multinível")
    parser.add_argument('--provider', type=str, choices=['groq', 'gemini'], default='gemini',
                        help="Escolha o provedor de IA (groq ou gemini). Padrão: gemini")
    parser.add_argument('--mode', type=str, choices=['gui', 'cli'], default='gui',
                        help="Escolha o modo de execução (gui ou cli). Padrão: gui")
    
    args = parser.parse_args()

    if args.mode == 'gui':
        run_gui(args.provider)
    else:
        run_cli(args.provider)

if __name__ == "__main__":
    main()

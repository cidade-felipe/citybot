import argparse
import sys
import os

# Adiciona a raiz do projeto ao sys.path para garantir que o pacote src seja encontrado
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_gui(provider):
    from PySide6.QtWidgets import QApplication
    from src.gui.app_pyside import ModernCityBotGUI

    if provider == 'gemini':
        from src.core.bot_gemini import CityBotGemini
        bot_factory = CityBotGemini
        title = 'CityBot Gemini - Assistente Inteligente'
    elif provider == 'azure_openai':
        from src.core.bot_azure_openai import CityBotAzureOpenAI
        bot_factory = CityBotAzureOpenAI
        title = 'CityBot Azure OpenAI - Assistente Inteligente'
    else:
        raise ValueError(f'Provedor não suportado: {provider}')

    app = QApplication.instance() or QApplication(sys.argv)
    window = ModernCityBotGUI(bot_factory=bot_factory, title=title)
    window.show()
    return app.exec()

def run_cli(provider):
    if provider == 'gemini':
        from src.core.bot_gemini import CityBotGemini
        bot = CityBotGemini()
    elif provider == 'azure_openai':
        from src.core.bot_azure_openai import CityBotAzureOpenAI
        bot = CityBotAzureOpenAI()
    else:
        raise ValueError(f'Provedor não suportado: {provider}')
    bot.menu()

def main():
    parser = argparse.ArgumentParser(description="CityBot - Assistente Inteligente Multinível")
    parser.add_argument('--provider', type=str, choices=['gemini', 'azure_openai'], default='azure_openai',
                        help="Escolha o provedor de IA (gemini ou azure_openai). Padrão: azure_openai")
    parser.add_argument('--mode', type=str, choices=['gui', 'cli'], default='gui',
                        help="Escolha o modo de execução (gui ou cli). Padrão: gui")

    args = parser.parse_args()

    if args.mode == 'gui':
        return run_gui(args.provider)
    run_cli(args.provider)
    return 0

if __name__ == "__main__":
    sys.exit(main())

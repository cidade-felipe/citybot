import unittest
from unittest.mock import Mock, call, patch

from src.gui.app_gemini import ModernCityBotGUI as GeminiGUI
from src.gui.app_groq import ModernCityBotGUI as GroqGUI


GUI_CLASSES = (GeminiGUI, GroqGUI)


class GuiHistoryTest(unittest.TestCase):
    def test_restaura_historico_com_roles_corretos(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.bot = Mock()
                gui.bot.load_conversations.return_value = [
                    ('Pergunta', 'Resposta'),
                ]
                gui.conversation_history = []
                gui.add_message_bubble = Mock()

                gui.load_conversation_history()

                self.assertEqual(
                    gui.conversation_history,
                    [('user', 'Pergunta'), ('assistant', 'Resposta')],
                )
                self.assertEqual(
                    gui.add_message_bubble.call_args_list,
                    [
                        call('Pergunta', is_user=True, animate=False),
                        call('Resposta', is_user=False, animate=False),
                    ],
                )

    def test_limpar_conversa_remove_historico_e_preserva_perfis(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                widget = Mock()
                gui = gui_class.__new__(gui_class)
                gui.bot = Mock()
                gui.is_processing = False
                gui.messages_frame = Mock()
                gui.messages_frame.winfo_children.return_value = [widget]
                gui.conversation_history = [('user', 'Pergunta')]
                gui.current_context = 'Contexto'
                gui.context_label = Mock()
                gui.add_system_message = Mock()

                with patch(
                    f'{gui_class.__module__}.messagebox.askyesno',
                    return_value=True,
                ):
                    gui.clear_chat()

                gui.bot.limpar_conversas.assert_called_once_with()
                gui.bot.limpar_banco.assert_not_called()
                widget.destroy.assert_called_once_with()
                self.assertEqual(gui.conversation_history, [])
                self.assertEqual(gui.current_context, '')
                gui.context_label.config.assert_called_once_with(text='Chat Livre')


if __name__ == '__main__':
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch

from PySide6.QtWidgets import QDialog, QMessageBox
from src.gui.app_azure_openai import ModernCityBotGUI as AzureGUI
from src.gui.app_gemini import ModernCityBotGUI as GeminiGUI
from src.utils.scrapers import ExtractedContent


GUI_CLASSES = (GeminiGUI, AzureGUI)


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
                gui = gui_class.__new__(gui_class)
                gui.bot = Mock()
                gui.is_processing = False
                gui.conversation_history = [('user', 'Pergunta')]
                gui.current_context = 'Contexto'
                gui.context_label = Mock()
                gui.clear_message_widgets = Mock()
                gui.add_system_message = Mock()

                with patch(
                    f'{gui_class.clear_chat.__module__}.QMessageBox.question',
                    return_value=QMessageBox.StandardButton.Yes,
                ):
                    gui.clear_chat()

                gui.bot.limpar_conversas.assert_called_once_with()
                gui.bot.limpar_banco.assert_not_called()
                gui.clear_message_widgets.assert_called_once_with()
                self.assertEqual(gui.conversation_history, [])
                self.assertEqual(gui.current_context, '')
                gui.context_label.setText.assert_called_once_with('Chat Livre')

    def test_chat_livre_reseta_sessao_sem_limpar_banco(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.bot = Mock()
                gui.is_processing = False
                gui.current_context = 'Contexto anterior'
                gui.conversation_history = [('user', 'Pergunta')]
                gui.context_label = Mock()
                gui.clear_message_widgets = Mock()
                gui._clear_ocr_export = Mock()
                gui._hide_download_progress = Mock()
                gui.add_system_message = Mock()
                gui.set_status = Mock()

                gui.set_chat_mode()

                self.assertEqual(gui.current_context, '')
                self.assertEqual(gui.conversation_history, [])
                gui.bot.limpar_conversas.assert_not_called()
                gui.clear_message_widgets.assert_called_once_with()
                gui.context_label.setText.assert_called_once_with('Chat Livre')

    def test_contexto_vazio_usa_mensagem_de_erro_contextual(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)

                with self.assertRaisesRegex(ValueError, 'HTTP 429 Too Many Requests'):
                    gui.set_loaded_context(
                        ExtractedContent(
                            '',
                            'O YouTube bloqueou temporariamente as requisições (HTTP 429 Too Many Requests).',
                        )
                    )

    def test_set_ocr_export_habilita_botao_de_download(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.download_ocr_button = Mock()

                gui._set_ocr_export('Texto OCR', 'imagem')

                self.assertEqual(gui.last_ocr_text, 'Texto OCR')
                self.assertEqual(gui.last_ocr_name, 'imagem')
                gui.download_ocr_button.setEnabled.assert_called_once_with(True)

    def test_download_ocr_text_salva_arquivo_escolhido(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.last_ocr_text = 'Texto OCR extraído'
                gui.last_ocr_name = 'imagem'
                gui.set_status = Mock()
                gui.add_system_message = Mock()

                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = Path(temp_dir) / 'ocr.txt'
                    with patch(
                        f'{gui_class.download_ocr_text.__module__}.QFileDialog.getSaveFileName',
                        return_value=(str(output_path), 'Text files (*.txt)'),
                    ):
                        gui.download_ocr_text()

                    self.assertEqual(output_path.read_text(encoding='utf-8'), 'Texto OCR extraído')

                gui.set_status.assert_called_once_with('●  Texto OCR salvo', 'success')
                gui.add_system_message.assert_called_once()

    def test_update_download_progress_mostra_porcentagem(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.download_progress = Mock()

                gui._update_download_progress({'status': 'downloading', 'percent': 42.8})

                gui.download_progress.setRange.assert_called_once_with(0, 100)
                gui.download_progress.setValue.assert_called_once_with(42)
                gui.download_progress.setFormat.assert_called_once_with('Baixando áudio: 42%')
                gui.download_progress.show.assert_called_once_with()

    def test_update_download_progress_sem_total_mostra_indeterminado(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.download_progress = Mock()

                gui._update_download_progress({'status': 'downloading', 'percent': None})

                gui.download_progress.setRange.assert_called_once_with(0, 0)
                gui.download_progress.setFormat.assert_called_once_with('Baixando áudio...')
                gui.download_progress.show.assert_called_once_with()

    def test_download_progress_color_muda_com_percentual(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)

                self.assertEqual(gui._download_progress_color(0), '#fb7185')
                self.assertEqual(gui._download_progress_color(50), '#fbbf24')
                self.assertEqual(gui._download_progress_color(100), '#38d9a9')

    def test_load_context_mostra_titulo_quando_conteudo_tem_metadado(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.bot = Mock()
                gui.context_label = Mock()
                gui.add_system_message = Mock()
                gui.set_status = Mock()
                gui._hide_download_progress = Mock()

                def run_task(loader, on_success, **_kwargs):
                    on_success(loader())

                gui._run_task = run_task

                gui._load_context(
                    'Vídeo',
                    'https://youtu.be/abc123',
                    lambda: ExtractedContent('Texto do vídeo', source_title='Título do vídeo'),
                    'https://youtu.be/abc123',
                )

                gui.context_label.setText.assert_called_once_with('Vídeo: Título do vídeo')
                gui.add_system_message.assert_called_once_with(
                    'Vídeo carregado',
                    'Agora você pode fazer perguntas sobre: Título do vídeo',
                )
                gui.bot.save_context.assert_called_once_with(
                    'Vídeo',
                    'https://youtu.be/abc123',
                    'Título do vídeo',
                    'Texto do vídeo',
                )

    def test_load_saved_context_reseta_sessao_e_ativa_contexto(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.bot = Mock()
                gui.bot.load_contexts.return_value = [
                    {
                        'id': 7,
                        'source_type': 'Site',
                        'source_ref': 'https://example.com',
                        'display_name': 'Example',
                        'created_at': '2026-07-22 06:00:00',
                    }
                ]
                gui.bot.load_context.return_value = {
                    'id': 7,
                    'source_type': 'Site',
                    'source_ref': 'https://example.com',
                    'display_name': 'Example',
                    'content': 'Conteúdo salvo',
                    'created_at': '2026-07-22 06:00:00',
                }
                gui.is_processing = False
                gui.current_context = 'Contexto anterior'
                gui.conversation_history = [('user', 'Pergunta')]
                gui.context_label = Mock()
                gui.clear_message_widgets = Mock()
                gui._clear_ocr_export = Mock()
                gui._hide_download_progress = Mock()
                gui.add_system_message = Mock()
                gui.set_status = Mock()

                selected_label = '#7 - Site: Example (2026-07-22 06:00:00)'
                with patch(
                    f'{gui_class.load_saved_context.__module__}.QInputDialog.getItem',
                    return_value=(selected_label, True),
                ):
                    gui.load_saved_context()

                self.assertEqual(gui.current_context, 'Conteúdo salvo')
                self.assertEqual(gui.conversation_history, [])
                gui.clear_message_widgets.assert_called_once_with()
                gui.context_label.setText.assert_called_once_with('Site: Example')
                gui.add_system_message.assert_called_once_with(
                    'Contexto restaurado',
                    'Agora você pode fazer perguntas sobre: Example',
                )

    def test_generate_image_dispara_tarefa_sem_limpar_contexto(self):
        for gui_class in GUI_CLASSES:
            with self.subTest(gui=gui_class.__module__):
                gui = gui_class.__new__(gui_class)
                gui.bot = Mock()
                gui.bot.gerar_imagem.return_value = 'imagem-gerada'
                gui.is_processing = False
                gui.current_context = 'Contexto atual'
                gui.set_status = Mock()
                gui.add_system_message = Mock()
                gui.show_generated_image = Mock()

                def run_task(task, on_success, **_kwargs):
                    on_success(task())

                gui._run_task = run_task

                dialog = Mock()
                dialog.exec.return_value = QDialog.DialogCode.Accepted
                dialog.values.return_value = {
                    'prompt': 'Uma cidade minimalista',
                    'size': '1024x1024',
                    'quality': 'low',
                    'output_format': 'png',
                }

                with patch(
                    f'{gui_class.generate_image.__module__}.ImageGenerationDialog',
                    return_value=dialog,
                ):
                    gui.generate_image()

                gui.bot.gerar_imagem.assert_called_once_with(
                    prompt='Uma cidade minimalista',
                    size='1024x1024',
                    quality='low',
                    output_format='png',
                )
                gui.show_generated_image.assert_called_once_with('imagem-gerada')
                self.assertEqual(gui.current_context, 'Contexto atual')


if __name__ == '__main__':
    unittest.main()

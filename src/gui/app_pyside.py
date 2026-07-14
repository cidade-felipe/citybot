import os
import sys
import threading
from pathlib import Path

from PySide6.QtCore import QObject, QEvent, Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class ModernCityBotGUI(QMainWindow):
    def __init__(self, bot_factory, title='CityBot - Assistente Inteligente'):
        super().__init__()
        self.bot = bot_factory()
        self.current_context = ''
        self.conversation_history = []
        self.is_processing = False
        self._worker_signals = []

        self.colors = {
            'bg_primary': '#101214',
            'bg_secondary': '#171b20',
            'bg_tertiary': '#20262d',
            'surface': '#242b33',
            'surface_hover': '#2c3540',
            'accent': '#38d9a9',
            'accent_secondary': '#5ab0ff',
            'text_primary': '#f6f7fb',
            'text_secondary': '#a9b2bd',
            'success': '#6ee7b7',
            'warning': '#fbbf24',
            'error': '#fb7185',
            'border': '#303842',
        }

        self.setWindowTitle(title)
        self.resize(1400, 850)
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(self._stylesheet())

        self._build_layout()
        self.load_conversation_history()

    def _stylesheet(self):
        return f"""
        QMainWindow, QWidget#root {{
            background: {self.colors['bg_primary']};
            color: {self.colors['text_primary']};
            font-family: "Segoe UI";
            font-size: 11pt;
        }}
        QFrame#sidebar {{
            background: {self.colors['bg_secondary']};
            border-right: 1px solid {self.colors['border']};
        }}
        QFrame#inputPanel, QFrame#contextCard {{
            background: {self.colors['bg_tertiary']};
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
        }}
        QFrame#systemCard, QFrame#assistantBubble {{
            background: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
        }}
        QFrame#userBubble {{
            background: {self.colors['accent']};
            border-radius: 8px;
        }}
        QLabel {{
            color: {self.colors['text_primary']};
        }}
        QLabel[role="muted"] {{
            color: {self.colors['text_secondary']};
        }}
        QLabel[role="accent"] {{
            color: {self.colors['accent']};
            font-weight: 700;
        }}
        QDialog {{
            background: {self.colors['bg_secondary']};
            color: {self.colors['text_primary']};
            font-family: "Segoe UI";
            font-size: 11pt;
        }}
        QDialog QLabel {{
            color: {self.colors['text_primary']};
            background: transparent;
        }}
        QDialog QPushButton {{
            min-width: 72px;
            padding: 9px 14px;
            text-align: center;
            color: {self.colors['text_primary']};
            background: {self.colors['surface']};
        }}
        QDialog QPushButton:hover {{
            background: {self.colors['surface_hover']};
        }}
        QDialog QLineEdit {{
            color: {self.colors['text_primary']};
            background: {self.colors['bg_tertiary']};
            border: 1px solid {self.colors['border']};
            border-radius: 6px;
            padding: 8px;
            selection-background-color: {self.colors['accent_secondary']};
        }}
        QPushButton {{
            border: 0;
            border-radius: 8px;
            padding: 11px 16px;
            text-align: left;
            color: {self.colors['text_primary']};
            background: {self.colors['surface']};
        }}
        QPushButton:hover {{
            background: {self.colors['surface_hover']};
        }}
        QPushButton[variant="accent"] {{
            color: {self.colors['bg_primary']};
            background: {self.colors['accent']};
            font-weight: 700;
            text-align: center;
        }}
        QPushButton[variant="accent"]:hover {{
            background: {self.colors['accent_secondary']};
        }}
        QPushButton[variant="danger"] {{
            color: {self.colors['bg_primary']};
            background: {self.colors['error']};
        }}
        QTextEdit, QTextBrowser {{
            color: {self.colors['text_primary']};
            background: transparent;
            border: 0;
            selection-background-color: {self.colors['accent_secondary']};
        }}
        QTextEdit#messageInput {{
            background: {self.colors['bg_tertiary']};
            border: 0;
        }}
        QScrollArea {{
            border: 0;
            background: {self.colors['bg_primary']};
        }}
        QScrollBar:vertical {{
            width: 10px;
            background: {self.colors['bg_primary']};
        }}
        QScrollBar::handle:vertical {{
            background: {self.colors['surface_hover']};
            border-radius: 5px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        """

    def _build_layout(self):
        root = QWidget()
        root.setObjectName('root')
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_chat_area(), 1)

        root_layout.addLayout(body, 1)
        root_layout.addWidget(self._build_status_bar())
        self.setCentralWidget(root)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(320)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(22, 24, 22, 24)
        layout.setSpacing(14)

        logo = self._build_logo()
        layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignHCenter)

        section = QLabel('FONTES DE DADOS')
        section.setProperty('role', 'muted')
        section.setFont(QFont('Segoe UI', 9, QFont.Weight.Bold))
        layout.addWidget(section)

        actions = [
            ('💬  Chat Livre', self.set_chat_mode, ''),
            ('🌐  Carregar Site', self.load_website, ''),
            ('📹  Carregar Vídeo', self.load_video, ''),
            ('📄  Carregar PDF', self.load_pdf, ''),
            ('🖼️  OCR Imagem', self.load_image_ocr, ''),
        ]
        for text, callback, variant in actions:
            layout.addWidget(self._button(text, callback, variant))

        context_title = QLabel('Contexto Atual')
        context_title.setProperty('role', 'accent')
        layout.addWidget(context_title)

        context_card = QFrame()
        context_card.setObjectName('contextCard')
        context_layout = QVBoxLayout(context_card)
        context_layout.setContentsMargins(14, 12, 14, 12)
        self.context_label = QLabel('Chat Livre')
        self.context_label.setWordWrap(True)
        context_layout.addWidget(self.context_label)
        layout.addWidget(context_card)

        layout.addSpacing(12)
        layout.addWidget(self._button('Limpar Conversa', self.clear_chat, 'danger'))
        layout.addStretch(1)
        return sidebar

    def _build_logo(self):
        logo_path = PROJECT_ROOT / 'src' / 'figures' / 'citybot_logo.png'
        if logo_path.exists():
            label = QLabel()
            pixmap = QPixmap(str(logo_path))
            label.setPixmap(
                pixmap.scaled(
                    118,
                    118,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            return label

        label = QLabel('CityBot')
        label.setProperty('role', 'accent')
        label.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        return label

    def _build_chat_area(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(18)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.message_container = QWidget()
        self.messages_layout = QVBoxLayout(self.message_container)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch(1)
        self.scroll_area.setWidget(self.message_container)
        layout.addWidget(self.scroll_area, 1)

        self.add_system_message(
            'Bem-vindo ao CityBot',
            'Escolha uma fonte de dados na lateral ou comece uma conversa.',
        )

        layout.addWidget(self._build_input_panel())
        return container

    def _build_input_panel(self):
        panel = QFrame()
        panel.setObjectName('inputPanel')
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        self.input_text = QTextEdit()
        self.input_text.setObjectName('messageInput')
        self.input_text.setPlaceholderText('Digite sua mensagem...')
        self.input_text.setFixedHeight(78)
        self.input_text.installEventFilter(self)
        layout.addWidget(self.input_text, 1)

        send_button = self._button('Enviar', self.send_message, 'accent')
        send_button.setFixedWidth(110)
        layout.addWidget(send_button)
        return panel

    def _build_status_bar(self):
        bar = QFrame()
        bar.setObjectName('sidebar')
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 8, 24, 8)

        self.status_label = QLabel('●  Pronto')
        self.status_label.setStyleSheet(f"color: {self.colors['success']};")
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        hint = QLabel('Enter envia, Shift+Enter quebra linha')
        hint.setProperty('role', 'muted')
        layout.addWidget(hint)
        return bar

    def _button(self, text, callback, variant=''):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        if variant:
            button.setProperty('variant', variant)
        return button

    def eventFilter(self, obj, event):
        if obj is self.input_text and event.type() == QEvent.Type.KeyPress:
            is_enter = event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            has_shift = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            if is_enter and not has_shift:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def load_conversation_history(self):
        for user_message, assistant_response in self.bot.load_conversations():
            self.conversation_history.extend([
                ('user', user_message),
                ('assistant', assistant_response),
            ])
            self.add_message_bubble(user_message, is_user=True, animate=False)
            self.add_message_bubble(assistant_response, is_user=False, animate=False)

    def add_message_bubble(self, text, is_user=True, animate=True):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        bubble_width = self._message_width(is_user)

        bubble = QFrame()
        bubble.setObjectName('userBubble' if is_user else 'assistantBubble')
        bubble.setFixedWidth(bubble_width)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(18, 12, 18, 12)

        message = QTextBrowser()
        message.setOpenExternalLinks(True)
        message.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        message.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        message.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        message.document().setDocumentMargin(0)
        message.setMarkdown(text or '')
        message_width = bubble_width - 36
        message.document().setTextWidth(message_width)
        message.setFixedWidth(message_width)
        content_height = int(message.document().size().height()) + 8
        message.setFixedHeight(max(content_height, 38))
        if is_user:
            message.setStyleSheet(f"color: {self.colors['bg_primary']};")
        bubble_layout.addWidget(message)

        if is_user:
            row_layout.addStretch(1)
            row_layout.addWidget(bubble)
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch(1)

        self._insert_message_widget(row)
        self._scroll_to_bottom()

    def _message_width(self, is_user):
        viewport_width = self.scroll_area.viewport().width()
        if viewport_width <= 0:
            viewport_width = self.width() - 380

        available_width = max(viewport_width - 32, 520)
        if is_user:
            return min(max(int(available_width * 0.48), 360), 680)
        return min(max(int(available_width * 0.82), 720), 1080)

    def add_system_message(self, title, message):
        card = QFrame()
        card.setObjectName('systemCard')
        card.setMaximumWidth(680)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 20, 28, 20)

        title_label = QLabel(title)
        title_label.setProperty('role', 'accent')
        title_label.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        body = QLabel(message)
        body.setProperty('role', 'muted')
        body.setWordWrap(True)
        layout.addWidget(body)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.addStretch(1)
        row_layout.addWidget(card)
        row_layout.addStretch(1)
        self._insert_message_widget(row)
        self._scroll_to_bottom()

    def _insert_message_widget(self, widget):
        stretch_index = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(stretch_index, widget)

    def _scroll_to_bottom(self):
        QApplication.processEvents()
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())

    def clear_message_widgets(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def set_status(self, text, color_key='success'):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {self.colors[color_key]};")

    def send_message(self):
        if self.is_processing:
            return
        message = self.input_text.toPlainText().strip()
        if not message:
            return

        self.input_text.clear()
        self.add_message_bubble(message, is_user=True)
        self.is_processing = True
        self.set_status('●  Processando...', 'warning')

        messages = self.conversation_history + [('user', message)]
        self._run_task(
            lambda: self.bot.resposta_bot(messages, self.current_context),
            lambda response: self.show_response(response, message),
        )

    def show_response(self, response, user_message):
        self.add_message_bubble(response, is_user=False)
        self.conversation_history.extend([('user', user_message), ('assistant', response)])
        self.bot.save_conversation(user_message, response)
        self.is_processing = False
        self.set_status('●  Pronto', 'success')

    def show_error(self, error_message):
        self.add_message_bubble(f'Erro: {error_message}', is_user=False)
        self.is_processing = False
        self.set_status('●  Erro', 'error')

    def set_chat_mode(self):
        self.current_context = ''
        self.context_label.setText('Chat Livre')
        self.add_system_message('Modo Chat Livre', 'Pergunte o que quiser. Estou pronto para conversar.')

    def set_loaded_context(self, content):
        if not content or not content.strip():
            message = getattr(content, 'error_message', '')
            raise ValueError(message or 'Não foi possível extrair conteúdo dessa fonte.')
        self.current_context = content

    def load_website(self):
        url, ok = QInputDialog.getText(self, 'Carregar Site', 'Digite a URL do site:')
        if ok and url.strip():
            self._load_context('Site', url.strip(), lambda: self.bot.carrega_site(url.strip()), f'{url[:50]}...')

    def load_video(self):
        url, ok = QInputDialog.getText(self, 'Carregar Vídeo', 'Digite a URL do YouTube:')
        if ok and url.strip():
            self._load_context('Vídeo', url.strip(), lambda: self.bot.carrega_video(url.strip()), url.strip())

    def load_pdf(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Selecionar PDF', '', 'PDF files (*.pdf);;All files (*.*)')
        if filename:
            self._load_context('PDF', filename, lambda: self.bot.carrega_pdf(filename), os.path.basename(filename))

    def load_image_ocr(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Selecionar Imagem',
            '',
            'Image files (*.png *.jpg *.jpeg *.bmp *.tiff);;All files (*.*)',
        )
        if filename:
            name = os.path.splitext(os.path.basename(filename))[0]
            self._load_context('OCR', filename, lambda: self.bot.carrega_imagem_ocr(filename, name), os.path.basename(filename))

    def _load_context(self, source_type, source_ref, loader, display_name):
        self.set_status(f'●  Carregando {source_type.lower()}...', 'warning')

        def on_success(content):
            try:
                self.set_loaded_context(content)
            except ValueError as error:
                self.show_error(str(error))
                return
            self.context_label.setText(f'{source_type}: {display_name}')
            self.add_system_message(f'{source_type} carregado', f'Agora você pode fazer perguntas sobre: {display_name}')
            self.set_status('●  Pronto', 'success')

        self._run_task(loader, on_success)

    def clear_chat(self):
        if self.is_processing:
            QMessageBox.warning(self, 'Aguarde', 'Espere a resposta atual terminar antes de limpar a conversa.')
            return

        answer = QMessageBox.question(
            self,
            'Limpar conversa',
            'Deseja apagar permanentemente todo o histórico de conversas?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.bot.limpar_conversas()
        self.clear_message_widgets()
        self.conversation_history = []
        self.current_context = ''
        self.context_label.setText('Chat Livre')
        self.add_system_message('Conversa limpa', 'O histórico foi apagado. Comece uma nova conversa.')

    def _run_task(self, task, on_success):
        signals = WorkerSignals()
        self._worker_signals.append(signals)

        def finish(result):
            self._release_signals(signals)
            on_success(result)

        def fail(error_message):
            self._release_signals(signals)
            self.show_error(error_message)

        signals.finished.connect(finish)
        signals.failed.connect(fail)

        def run():
            try:
                signals.finished.emit(task())
            except Exception as error:
                signals.failed.emit(str(error))

        threading.Thread(target=run, daemon=True).start()

    def _release_signals(self, signals):
        if signals in self._worker_signals:
            self._worker_signals.remove(signals)


def run_qt_app(window_factory):
    app = QApplication.instance() or QApplication(sys.argv)
    window = window_factory()
    window.show()
    return app.exec()

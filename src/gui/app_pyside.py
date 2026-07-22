import os
import sys
import threading
from pathlib import Path

from PySide6.QtCore import QObject, QEvent, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BANNER_PATH = PROJECT_ROOT / 'src' / 'figures' / 'citybot_banner_minimal.png'
IMAGE_SIZE_OPTIONS = ('1536x1024', '1024x1024', '1024x1536', '2048x1152', '2048x2048', 'auto')
IMAGE_QUALITY_OPTIONS = ('medium', 'low', 'high', 'auto')
IMAGE_FORMAT_OPTIONS = ('png', 'jpeg', 'webp')


class BannerLabel(QWidget):
    def __init__(self, image_path, border_color, fallback_color):
        super().__init__()
        self._pixmap = QPixmap(str(image_path))
        self._border_color = border_color
        self._fallback_color = fallback_color
        self.setFixedHeight(168)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.fillPath(path, QColor(self._fallback_color))

        if not self._pixmap.isNull():
            painter.setClipPath(path)
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.setClipping(False)

        painter.setPen(QColor(self._border_color))
        painter.drawPath(path)


class ImageGenerationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Gerar imagem')
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        prompt_label = QLabel('Prompt')
        prompt_label.setProperty('role', 'accent')
        layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText('Descreva a imagem...')
        self.prompt_input.setFixedHeight(132)
        layout.addWidget(self.prompt_input)

        options = QHBoxLayout()
        options.setSpacing(10)
        self.size_combo = self._combo(IMAGE_SIZE_OPTIONS)
        self.quality_combo = self._combo(IMAGE_QUALITY_OPTIONS)
        self.format_combo = self._combo(IMAGE_FORMAT_OPTIONS)
        options.addWidget(self._option('Tamanho', self.size_combo))
        options.addWidget(self._option('Qualidade', self.quality_combo))
        options.addWidget(self._option('Formato', self.format_combo))
        layout.addLayout(options)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Gerar')
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('Cancelar')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return {
            'prompt': self.prompt_input.toPlainText().strip(),
            'size': self.size_combo.currentText(),
            'quality': self.quality_combo.currentText(),
            'output_format': self.format_combo.currentText(),
        }

    def _combo(self, values):
        combo = QComboBox()
        combo.addItems(values)
        return combo

    def _option(self, label, widget):
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        text = QLabel(label)
        text.setProperty('role', 'muted')
        layout.addWidget(text)
        layout.addWidget(widget)
        return box


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)
    progress = Signal(object)


class ModernCityBotGUI(QMainWindow):
    def __init__(self, bot_factory, title='CityBot - Assistente Inteligente'):
        super().__init__()
        self.bot = bot_factory()
        self.current_context = ''
        self.conversation_history = []
        self.is_processing = False
        self._worker_signals = []
        self.last_ocr_text = ''
        self.last_ocr_name = 'ocr_texto'

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
        QDialog QTextEdit, QDialog QComboBox {{
            color: {self.colors['text_primary']};
            background: {self.colors['bg_tertiary']};
            border: 1px solid {self.colors['border']};
            border-radius: 6px;
            padding: 8px;
            selection-background-color: {self.colors['accent_secondary']};
        }}
        QDialog QComboBox QAbstractItemView {{
            color: {self.colors['text_primary']};
            background: {self.colors['bg_tertiary']};
            selection-background-color: {self.colors['accent']};
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
        QPushButton:disabled {{
            color: {self.colors['text_secondary']};
            background: {self.colors['bg_tertiary']};
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
        QProgressBar {{
            color: {self.colors['text_primary']};
            background: {self.colors['bg_tertiary']};
            border: 1px solid {self.colors['border']};
            border-radius: 6px;
            height: 18px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background: {self.colors['accent']};
            border-radius: 5px;
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
            ('🌐  Analisar Site', self.load_website, ''),
            ('📹  Analisar Vídeo do YouTube', self.load_video, ''),
            ('📄  Analisar PDF', self.load_pdf, ''),
            ('🖼️  Analisar Texto de Imagem', self.load_image_ocr, ''),
            ('🎨  Gerar Imagem', self.generate_image, ''),
            ('📚  Contextos Salvos', self.load_saved_context, ''),
        ]
        for text, callback, variant in actions:
            layout.addWidget(self._button(text, callback, variant))

        self.download_ocr_button = self._button('💾  Salvar Texto OCR', self.download_ocr_text, '')
        self.download_ocr_button.setEnabled(False)
        layout.addWidget(self.download_ocr_button)

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
        layout.setContentsMargins(26, 20, 26, 22)
        layout.setSpacing(16)

        banner = self._build_chat_banner()
        if banner:
            layout.addWidget(banner)

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

    def _build_chat_banner(self):
        if not BANNER_PATH.exists():
            return None
        return BannerLabel(BANNER_PATH, self.colors['border'], self.colors['bg_tertiary'])

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

        status_stack = QWidget()
        status_stack.setFixedWidth(272)
        status_layout = QVBoxLayout(status_stack)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(4)

        self.download_progress = QProgressBar()
        self.download_progress.setFixedWidth(248)
        self.download_progress.setRange(0, 100)
        self.download_progress.setValue(0)
        self.download_progress.setFormat('Baixando áudio: 0%')
        self._set_download_progress_color(0)
        self.download_progress.hide()
        status_layout.addWidget(self.download_progress)

        self.status_label = QLabel('●  Pronto')
        self.status_label.setStyleSheet(f"color: {self.colors['success']};")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_stack)
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

    def add_generated_image_card(self, result):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        bubble_width = min(self._message_width(False), 900)
        bubble = QFrame()
        bubble.setObjectName('assistantBubble')
        bubble.setFixedWidth(bubble_width)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(18, 14, 18, 14)
        bubble_layout.setSpacing(10)

        title = QLabel('Imagem gerada')
        title.setProperty('role', 'accent')
        title.setFont(QFont('Segoe UI', 13, QFont.Weight.Bold))
        bubble_layout.addWidget(title)

        pixmap = QPixmap(str(result.path))
        if not pixmap.isNull():
            preview = QLabel()
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview.setPixmap(
                pixmap.scaled(
                    bubble_width - 36,
                    420,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            bubble_layout.addWidget(preview)

        prompt = QLabel(f'Prompt: {self._shorten_text(result.prompt, 180)}')
        prompt.setProperty('role', 'muted')
        prompt.setWordWrap(True)
        bubble_layout.addWidget(prompt)

        output = QLabel(f'Arquivo: {result.path}')
        output.setProperty('role', 'muted')
        output.setWordWrap(True)
        bubble_layout.addWidget(output)

        row_layout.addWidget(bubble)
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

    def show_generated_image(self, result):
        self.add_generated_image_card(result)
        self.is_processing = False
        self.set_status('●  Imagem gerada', 'success')

    def show_error(self, error_message):
        self._hide_download_progress()
        self.add_message_bubble(f'Erro: {error_message}', is_user=False)
        self.is_processing = False
        self.set_status('●  Erro', 'error')

    def set_chat_mode(self):
        if not self._can_change_context():
            return
        self._reset_active_session()
        self.context_label.setText('Chat Livre')
        self.add_system_message('Modo Chat Livre', 'Pergunte o que quiser. Estou pronto para conversar.')
        self.set_status('●  Pronto', 'success')

    def set_loaded_context(self, content):
        if not content or not content.strip():
            message = getattr(content, 'error_message', '')
            raise ValueError(message or 'Não foi possível extrair conteúdo dessa fonte.')
        self.current_context = content

    def load_website(self):
        if not self._can_change_context():
            return
        url, ok = QInputDialog.getText(self, 'Carregar Site', 'Digite a URL do site:')
        if ok and url.strip():
            self._reset_active_session()
            self._load_context('Site', url.strip(), lambda: self.bot.carrega_site(url.strip()), f'{url[:50]}...')

    def load_video(self):
        if not self._can_change_context():
            return
        url, ok = QInputDialog.getText(self, 'Carregar Vídeo', 'Digite a URL do YouTube:')
        if ok and url.strip():
            self._reset_active_session()
            self._load_context(
                'Vídeo',
                url.strip(),
                lambda progress_callback: self.bot.carrega_video(
                    url.strip(),
                    progress_callback=progress_callback,
                ),
                url.strip(),
                on_progress=self._update_download_progress,
                pass_progress=True,
            )

    def load_pdf(self):
        if not self._can_change_context():
            return
        filename, _ = QFileDialog.getOpenFileName(self, 'Selecionar PDF', '', 'PDF files (*.pdf);;All files (*.*)')
        if filename:
            self._reset_active_session()
            self._load_context('PDF', filename, lambda: self.bot.carrega_pdf(filename), os.path.basename(filename))

    def load_image_ocr(self):
        if not self._can_change_context():
            return
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Selecionar Imagem',
            '',
            'Image files (*.png *.jpg *.jpeg *.bmp *.tiff);;All files (*.*)',
        )
        if filename:
            name = os.path.splitext(os.path.basename(filename))[0]
            self._reset_active_session()
            self._load_context(
                'OCR',
                filename,
                lambda: self.bot.carrega_imagem_ocr(filename, name),
                os.path.basename(filename),
                after_success=lambda content: self._set_ocr_export(content, name),
            )

    def generate_image(self):
        if self.is_processing:
            QMessageBox.warning(self, 'Aguarde', 'Espere a ação atual terminar antes de gerar outra imagem.')
            return

        dialog = ImageGenerationDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        options = dialog.values()
        if not options['prompt']:
            QMessageBox.information(self, 'Gerar imagem', 'Informe um prompt para gerar a imagem.')
            return

        self.is_processing = True
        self.set_status('●  Gerando imagem...', 'warning')
        self.add_system_message('Gerando imagem', 'Aguarde enquanto o gpt-image-2 cria a imagem.')
        self._run_task(
            lambda: self.bot.gerar_imagem(**options),
            self.show_generated_image,
        )

    def load_saved_context(self):
        if not self._can_change_context():
            return

        contexts = self.bot.load_contexts()
        if not contexts:
            QMessageBox.information(self, 'Contextos salvos', 'Nenhum contexto salvo ainda.')
            return

        labels_by_context = {
            self._saved_context_label(context): context
            for context in contexts
        }
        selected_label, ok = QInputDialog.getItem(
            self,
            'Contextos salvos',
            'Escolha um contexto:',
            list(labels_by_context),
            0,
            False,
        )
        if not ok or not selected_label:
            return

        selected_context = labels_by_context[selected_label]
        context = self.bot.load_context(selected_context['id'])
        if not context:
            QMessageBox.warning(self, 'Contextos salvos', 'Esse contexto não foi encontrado no banco.')
            return

        self._reset_active_session()
        self.current_context = context['content']
        self.context_label.setText(f"{context['source_type']}: {context['display_name']}")
        self.add_system_message(
            'Contexto restaurado',
            f"Agora você pode fazer perguntas sobre: {context['display_name']}",
        )
        self.set_status('●  Contexto restaurado', 'success')

    def download_ocr_text(self):
        if not self.last_ocr_text.strip():
            QMessageBox.information(self, 'Baixar Texto OCR', 'Carregue uma imagem com OCR antes de baixar o texto.')
            return

        default_path = PROJECT_ROOT / 'textos' / f'{self.last_ocr_name or "ocr_texto"}.txt'
        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Baixar Texto OCR',
            str(default_path),
            'Text files (*.txt);;All files (*.*)',
        )
        if not filename:
            return

        try:
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(self.last_ocr_text, encoding='utf-8')
        except OSError as error:
            self.show_error(f'Não foi possível salvar o texto OCR: {error}')
            return

        self.set_status('●  Texto OCR salvo', 'success')
        self.add_system_message('Texto OCR salvo', f'Arquivo salvo em: {filename}')

    def _set_ocr_export(self, content, name):
        self.last_ocr_text = str(content or '')
        self.last_ocr_name = name or 'ocr_texto'
        if hasattr(self, 'download_ocr_button'):
            self.download_ocr_button.setEnabled(bool(self.last_ocr_text.strip()))

    def _clear_ocr_export(self):
        self.last_ocr_text = ''
        self.last_ocr_name = 'ocr_texto'
        if hasattr(self, 'download_ocr_button'):
            self.download_ocr_button.setEnabled(False)

    def _load_context(
        self,
        source_type,
        source_ref,
        loader,
        display_name,
        after_success=None,
        on_progress=None,
        pass_progress=False,
    ):
        self.set_status(f'●  Carregando {source_type.lower()}...', 'warning')

        def on_success(content):
            try:
                self.set_loaded_context(content)
            except ValueError as error:
                self.show_error(str(error))
                return
            resolved_display_name = self._context_display_name(content, display_name)
            self.context_label.setText(f'{source_type}: {resolved_display_name}')
            if after_success:
                after_success(content)
            self._save_loaded_context(source_type, source_ref, resolved_display_name, content)
            self.add_system_message(f'{source_type} carregado', f'Agora você pode fazer perguntas sobre: {resolved_display_name}')
            self._hide_download_progress()
            self.set_status('●  Pronto', 'success')

        self._run_task(loader, on_success, on_progress=on_progress, pass_progress=pass_progress)

    def _context_display_name(self, content, fallback):
        source_title = str(getattr(content, 'source_title', '') or '').strip()
        return source_title or fallback

    def _can_change_context(self):
        if not self.is_processing:
            return True

        QMessageBox.warning(self, 'Aguarde', 'Espere a resposta atual terminar antes de trocar de contexto.')
        return False

    def _reset_active_session(self):
        self.current_context = ''
        self.conversation_history = []
        self.clear_message_widgets()
        self._clear_ocr_export()
        self._hide_download_progress()

    def _save_loaded_context(self, source_type, source_ref, display_name, content):
        self.bot.save_context(
            source_type,
            source_ref,
            display_name,
            str(content),
        )

    def _saved_context_label(self, context):
        display_name = str(context.get('display_name') or context.get('source_ref') or 'Sem nome')
        if len(display_name) > 80:
            display_name = f'{display_name[:77]}...'
        created_at = context.get('created_at') or ''
        return f"#{context['id']} - {context['source_type']}: {display_name} ({created_at})"

    @staticmethod
    def _shorten_text(text, limit):
        value = str(text or '').strip()
        if len(value) <= limit:
            return value
        return f'{value[:limit - 3]}...'

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
        self._clear_ocr_export()
        self.context_label.setText('Chat Livre')
        self.add_system_message('Conversa limpa', 'O histórico foi apagado. Comece uma nova conversa.')

    def _show_download_progress(self):
        if not hasattr(self, 'download_progress'):
            return
        self.download_progress.setRange(0, 100)
        self.download_progress.setValue(0)
        self.download_progress.setFormat('Baixando áudio: 0%')
        self._set_download_progress_color(0)
        self.download_progress.show()

    def _hide_download_progress(self):
        if hasattr(self, 'download_progress'):
            self.download_progress.hide()

    def _update_download_progress(self, progress):
        if not hasattr(self, 'download_progress'):
            return

        status = progress.get('status', '')
        percent = progress.get('percent')
        if status == 'downloading':
            if percent is None:
                self.download_progress.setRange(0, 0)
                self.download_progress.setFormat('Baixando áudio...')
                self._set_download_progress_color(50)
                self.download_progress.show()
                return

            value = int(percent)
            self.download_progress.setRange(0, 100)
            self.download_progress.setValue(value)
            self.download_progress.setFormat(f'Baixando áudio: {value}%')
            self._set_download_progress_color(value)
            self.download_progress.show()
            return

        if status == 'finished':
            self.download_progress.setRange(0, 100)
            self.download_progress.setValue(100)
            self.download_progress.setFormat('Áudio baixado')
            self._set_download_progress_color(100)
            self.download_progress.show()

    def _set_download_progress_color(self, percent):
        if not hasattr(self, 'download_progress'):
            return

        color = self._download_progress_color(percent)
        self.download_progress.setStyleSheet(f"""
        QProgressBar::chunk {{
            background: {color};
            border-radius: 5px;
        }}
        """)

    def _download_progress_color(self, percent):
        value = max(0, min(100, float(percent or 0)))
        red = '#fb7185'
        yellow = '#fbbf24'
        green = '#38d9a9'

        if value <= 50:
            return self._interpolate_hex_color(red, yellow, value / 50)
        return self._interpolate_hex_color(yellow, green, (value - 50) / 50)

    @staticmethod
    def _interpolate_hex_color(start, end, ratio):
        ratio = max(0, min(1, ratio))
        start_rgb = tuple(int(start[index:index + 2], 16) for index in (1, 3, 5))
        end_rgb = tuple(int(end[index:index + 2], 16) for index in (1, 3, 5))
        mixed = tuple(
            round(start_value + (end_value - start_value) * ratio)
            for start_value, end_value in zip(start_rgb, end_rgb)
        )
        return '#{:02x}{:02x}{:02x}'.format(*mixed)

    def _run_task(self, task, on_success, on_progress=None, pass_progress=False):
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
        if on_progress:
            signals.progress.connect(on_progress)

        def run():
            try:
                if pass_progress:
                    signals.finished.emit(task(signals.progress.emit))
                else:
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
    window.showMaximized()
    return app.exec()

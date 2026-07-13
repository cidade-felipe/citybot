import contextlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont
import threading
from datetime import datetime
import os
import sys
from PIL import Image, ImageTk
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para permitir imports do pacote src
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
   sys.path.append(root_path)

from src.core.bot_gemini import CityBotGemini
from src.gui.markdown_renderer import create_markdown_message

class ModernCityBotGUI:
   def __init__(self, root, bot_factory=CityBotGemini, title="CityBot Gemini - Assistente Inteligente"):
      self.root = root
      self.root.title(title)
      self.root.geometry("1400x850")
      self.root.minsize(1200, 700)
      self.root.configure(bg="#101214")
      
      self.colors = {
         'bg_primary': "#101214",
         'bg_secondary': "#171b20",
         'bg_tertiary': "#20262d",
         'surface': "#242b33",
         'surface_hover': "#2c3540",
         'accent': "#38d9a9",
         'accent_secondary': "#5ab0ff",
         'text_primary': "#f6f7fb",
         'text_secondary': "#a9b2bd",
         'success': "#6ee7b7",
         'warning': "#fbbf24",
         'error': "#fb7185",
         'border': "#303842"
      }
      
      self.setup_styles()
      
      self.bot = bot_factory()
      self.current_context = ""
      self.conversation_history = []
      self.is_processing = False
      
      self.create_layout()
      self.create_sidebar()
      self.create_chat_area()
      self.create_input_area()
      self.create_status_bar()
      self.load_conversation_history()
      
      self.root.bind("<Return>", lambda e: None if e.state & 0x1 else self.send_message())
      self.root.bind("<Shift-Return>", lambda e: None)
      
      self.animate_startup()
      
   def setup_styles(self):
      self.font_title = tkfont.Font(family="Segoe UI", size=16, weight="bold")
      self.font_text = tkfont.Font(family="Segoe UI", size=11)
      self.font_mono = tkfont.Font(family="Consolas", size=10)
      self.font_small = tkfont.Font(family="Segoe UI", size=10)
      self.font_menu = tkfont.Font(family="Segoe UI", size=11)

      self.style = ttk.Style()
      self.style.theme_use('clam')
      self.style.configure('.', font=self.font_text)
      self.style.configure('City.TFrame', background=self.colors['bg_primary'])
      self.style.configure('Sidebar.TFrame', background=self.colors['bg_secondary'])
      self.style.configure('Panel.TFrame', background=self.colors['bg_tertiary'])
      self.style.configure('Card.TFrame', background=self.colors['surface'])
      self.style.configure('UserBubble.TFrame', background=self.colors['accent'])
      self.style.configure('AssistantBubble.TFrame', background=self.colors['surface'])
      self.style.configure('City.TLabel', background=self.colors['bg_primary'], foreground=self.colors['text_primary'])
      self.style.configure('Sidebar.TLabel', background=self.colors['bg_secondary'], foreground=self.colors['text_primary'])
      self.style.configure('Muted.TLabel', background=self.colors['bg_secondary'], foreground=self.colors['text_secondary'])
      self.style.configure('ChatMuted.TLabel', background=self.colors['bg_primary'], foreground=self.colors['text_secondary'], font=self.font_small)
      self.style.configure('Panel.TLabel', background=self.colors['bg_tertiary'], foreground=self.colors['text_primary'])
      self.style.configure('Card.TLabel', background=self.colors['surface'], foreground=self.colors['text_primary'])
      self.style.configure('CardMuted.TLabel', background=self.colors['surface'], foreground=self.colors['text_secondary'])
      self.style.configure('SystemTitle.TLabel', background=self.colors['surface'], foreground=self.colors['accent'], font=self.font_title)
      self.style.configure('Accent.TLabel', background=self.colors['bg_secondary'], foreground=self.colors['accent'], font=self.font_title)
      self.style.configure('Status.TLabel', background=self.colors['bg_secondary'], foreground=self.colors['success'], font=self.font_small)
      self.style.configure('Sidebar.TButton', background=self.colors['surface'], foreground=self.colors['text_primary'], borderwidth=0, focusthickness=0, padding=(18, 12), anchor='w', font=self.font_menu)
      self.style.map('Sidebar.TButton', background=[('active', self.colors['surface_hover']), ('pressed', self.colors['bg_tertiary'])], foreground=[('active', self.colors['text_primary'])])
      self.style.configure('Danger.TButton', background=self.colors['error'], foreground=self.colors['bg_primary'], borderwidth=0, focusthickness=0, padding=(18, 12), anchor='w', font=self.font_menu)
      self.style.map('Danger.TButton', background=[('active', "#ff8aa0"), ('pressed', "#f43f5e")])
      self.style.configure('Accent.TButton', background=self.colors['accent'], foreground=self.colors['bg_primary'], borderwidth=0, focusthickness=0, padding=(18, 10), font=("Segoe UI", 14, "bold"))
      self.style.map('Accent.TButton', background=[('active', self.colors['accent_secondary']), ('pressed', self.colors['accent'])], foreground=[('active', self.colors['bg_primary'])])
      self.style.configure('Ghost.TButton', background=self.colors['bg_tertiary'], foreground=self.colors['text_primary'], borderwidth=0, focusthickness=0, padding=(20, 10), font=self.font_text)
      self.style.map('Ghost.TButton', background=[('active', self.colors['surface_hover'])])
      self.style.configure('Dialog.TEntry', fieldbackground=self.colors['bg_tertiary'], foreground=self.colors['text_primary'], insertcolor=self.colors['accent'], bordercolor=self.colors['border'], lightcolor=self.colors['border'], darkcolor=self.colors['border'])
      self.style.configure('City.Vertical.TScrollbar', background=self.colors['surface'], troughcolor=self.colors['bg_primary'], bordercolor=self.colors['bg_primary'], arrowcolor=self.colors['text_secondary'])
      self.style.configure('City.Horizontal.TSeparator', background=self.colors['border'])
      
   def create_layout(self):
      self.root.grid_columnconfigure(1, weight=1)
      self.root.grid_rowconfigure(0, weight=1)
      
   def create_sidebar(self):  # sourcery skip: extract-method
      self.sidebar = ttk.Frame(self.root, style='Sidebar.TFrame', width=320)
      self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
      self.sidebar.grid_propagate(False)
      self.sidebar.pack_propagate(False)
      
      sidebar_canvas = tk.Canvas(self.sidebar, bg=self.colors['bg_secondary'], 
                                 highlightthickness=0, width=320)
      sidebar_canvas.pack(side="left", fill="both", expand=True)
      
      scrollbar = ttk.Scrollbar(
         self.sidebar,
         orient="vertical",
         command=sidebar_canvas.yview,
         style='City.Vertical.TScrollbar',
      )
      scrollbar.pack(side="right", fill="y")
      
      sidebar_canvas.configure(yscrollcommand=scrollbar.set)
      
      self.sidebar_content = ttk.Frame(sidebar_canvas, style='Sidebar.TFrame', width=300)
      self.sidebar_window = sidebar_canvas.create_window((0, 0), 
                                                         window=self.sidebar_content,
                                                         anchor="nw", width=300)
      
      self.sidebar_content.bind("<Configure>", 
                              lambda e: sidebar_canvas.configure(
                                    scrollregion=sidebar_canvas.bbox("all")))
      
      header = ttk.Frame(self.sidebar_content, style='Sidebar.TFrame', height=112)
      header.pack(fill="x", padx=20, pady=25)
      header.pack_propagate(False)
      
      logo_path = Path(root_path) / 'src' / 'figures' / 'citybot_logo.png'
      if logo_path.exists():
         logo_img = Image.open(logo_path)
         logo_img.thumbnail((120, 120), Image.Resampling.LANCZOS)
         logo_tk = ImageTk.PhotoImage(logo_img)
         logo_label = ttk.Label(header, image=logo_tk, style='Sidebar.TLabel')
         logo_label.pack(expand=True)
         logo_label.image = logo_tk
      else:
         ttk.Label(header, text="CityBot", style='Accent.TLabel').pack(expand=True)
      
      self.pulse_animation()
      
      ttk.Separator(self.sidebar_content, orient="horizontal", style='City.Horizontal.TSeparator').pack(fill="x", padx=20, pady=15)
      
      menu_label = ttk.Label(
         self.sidebar_content,
         text="FONTES DE DADOS",
         style='Muted.TLabel',
         font=("Segoe UI", 9, "bold"),
      )
      menu_label.pack(anchor="w", padx=25, pady=(15, 10))
      
      self.menu_buttons = []
      menu_items = [
         ("💬  Chat Livre", self.set_chat_mode),
         ("🌐   Carregar Site", self.load_website),
         ("📹  Carregar Vídeo", self.load_video),
         ("📄  Carregar PDF", self.load_pdf),
         ("🖼️  OCR Imagem", self.load_image_ocr),
      ]
      
      for text, command in menu_items:
         btn = self.create_menu_button(text, command)
         btn.pack(fill="x", padx=20, pady=4)
         self.menu_buttons.append(btn)
      
      ttk.Separator(self.sidebar_content, orient="horizontal", style='City.Horizontal.TSeparator').pack(fill="x", padx=20, pady=20)
      
      context_container = ttk.Frame(self.sidebar_content, style='Sidebar.TFrame')
      context_container.pack(fill="x", padx=20, pady=10)
      
      ttk.Label(
         context_container,
         text="📋 Contexto Atual",
         style='Sidebar.TLabel',
         font=("Segoe UI", 10, "bold"),
         foreground=self.colors['accent'],
      ).pack(anchor="w")

      self.context_frame = ttk.Frame(
         context_container,
         style='Panel.TFrame',
         padding=(14, 10),
      )
      self.context_frame.pack(fill="x", pady=(10, 0), ipady=10)
      
      self.context_label = ttk.Label(
         self.context_frame,
         text="Chat Livre",
         style='Panel.TLabel',
         font=self.font_small,
         wraplength=230,
      )
      self.context_label.pack(anchor="w")
      
      self.create_menu_button("🗑️  Limpar Conversa", self.clear_chat, 
                              bg=self.colors['error']).pack(fill="x", padx=20, pady=30)
      
   def create_menu_button(self, text, command, bg=None):
      style = 'Danger.TButton' if bg else 'Sidebar.TButton'
      return ttk.Button(
         self.sidebar_content,
         text=text,
         command=command,
         style=style,
         cursor="hand2",
      )
      
   def create_chat_area(self):
      self.chat_container = ttk.Frame(self.root, style='City.TFrame')
      self.chat_container.grid(row=0, column=1, sticky="nsew")
      self.chat_container.grid_columnconfigure(0, weight=1)
      self.chat_container.grid_rowconfigure(0, weight=1)
      
      self.chat_canvas = tk.Canvas(self.chat_container, bg=self.colors['bg_primary'], 
                                 highlightthickness=0)
      scrollbar = ttk.Scrollbar(
         self.chat_container,
         orient="vertical",
         command=self.chat_canvas.yview,
         style='City.Vertical.TScrollbar',
      )
      
      self.chat_canvas.configure(yscrollcommand=scrollbar.set)
      
      self.chat_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
      scrollbar.grid(row=0, column=1, sticky="ns")
      
      self.messages_frame = ttk.Frame(self.chat_canvas, style='City.TFrame')
      self.canvas_window = self.chat_canvas.create_window((0, 0), 
                                                         window=self.messages_frame, 
                                                         anchor="nw")
      
      self.messages_frame.bind("<Configure>", self.on_frame_configure)
      self.chat_canvas.bind("<Configure>", self.on_canvas_configure)
      
      self.chat_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
      
      self.add_system_message("👋 Bem-vindo ao CityBot!", 
                              "Sou seu assistente inteligente. Escolha uma opção no menu lateral ou comece a conversar.")
      
   def create_input_area(self):
      input_frame = ttk.Frame(self.chat_container, style='Sidebar.TFrame', height=160)
      input_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=25)
      input_frame.grid_propagate(False)
      input_frame.grid_columnconfigure(0, weight=1)
      
      input_container = ttk.Frame(input_frame, style='Panel.TFrame', padding=(10, 8))
      input_container.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
      input_container.grid_columnconfigure(0, weight=1)
      
      self.input_text = tk.Text(input_container, height=3, 
                              bg=self.colors['bg_tertiary'],
                              fg=self.colors['text_primary'], 
                              font=self.font_text,
                              wrap="word", bd=0, highlightthickness=0,
                              insertbackground=self.colors['accent'],
                              padx=10, pady=10)
      self.input_text.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
      
      self.input_text.insert("1.0", "Digite sua mensagem...")
      self.input_text.config(fg=self.colors['text_secondary'])
      
      def on_focus_in(event):
         if self.input_text.get("1.0", "end-1c") == "Digite sua mensagem...":
               self.input_text.delete("1.0", "end")
               self.input_text.config(fg=self.colors['text_primary'])
               
      def on_focus_out(event):
         if not self.input_text.get("1.0", "end-1c").strip():
               self.input_text.delete("1.0", "end")
               self.input_text.insert("1.0", "Digite sua mensagem...")
               self.input_text.config(fg=self.colors['text_secondary'])
      
      self.input_text.bind("<FocusIn>", on_focus_in)
      self.input_text.bind("<FocusOut>", on_focus_out)
      
      send_btn = ttk.Button(
         input_container,
         text="➤",
         command=self.send_message,
         style='Accent.TButton',
         cursor="hand2",
         width=3,
      )
      send_btn.grid(row=0, column=1, padx=12, pady=8)

      hint_label = ttk.Label(
         input_frame,
         text="💡 Enter para enviar  •  Shift+Enter para nova linha",
         style='Muted.TLabel',
         font=self.font_small,
      )
      hint_label.grid(row=1, column=0, sticky="w", padx=15)
      
   def create_status_bar(self):
      self.status_bar = ttk.Frame(self.root, style='Sidebar.TFrame', height=35)
      self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
      self.status_bar.grid_propagate(False)
      
      self.status_label = ttk.Label(
         self.status_bar,
         text="●  Pronto",
         style='Status.TLabel',
      )
      self.status_label.pack(side="left", padx=25)
      
      self.time_label = ttk.Label(
         self.status_bar,
         text="",
         style='Muted.TLabel',
      )
      self.time_label.pack(side="right", padx=25)
      self.update_time()
      
   def update_time(self):
      current_time = datetime.now().strftime("%H:%M:%S")
      self.time_label.config(text=current_time)
      self.root.after(1000, self.update_time)

   def set_status(self, text, color_key='success'):
      self.status_label.config(text=text, foreground=self.colors[color_key])
      
   def pulse_animation(self):
      def animate():
         with contextlib.suppress(Exception):
            for i in range(10):
               1 + (i * 0.05)
               self.root.after(50)
            self.root.after(2000, animate)
      animate()
      
   def animate_startup(self):
      pass

   def load_conversation_history(self):
      for user_message, assistant_response in self.bot.load_conversations():
         self.conversation_history.extend([
            ('user', user_message),
            ('assistant', assistant_response),
         ])
         self.add_message_bubble(user_message, is_user=True, animate=False)
         self.add_message_bubble(assistant_response, is_user=False, animate=False)
      
   def on_frame_configure(self, event=None):
      self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
      
   def on_canvas_configure(self, event):
      self.chat_canvas.itemconfig(self.canvas_window, width=event.width)
      
   def on_mousewheel(self, event):
      self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
      
   def add_message_bubble(self, text, is_user=True, animate=True):
      bubble_container = ttk.Frame(self.messages_frame, style='City.TFrame')
      bubble_container.pack(fill="x", padx=30, pady=8)
      
      if is_user:
         bubble_container.grid_columnconfigure(0, weight=1)
         col = 1
         bg_color = self.colors['accent']
         fg_color = self.colors['bg_primary']
         bubble_style = 'UserBubble.TFrame'
         anchor = "e"
      else:
         bubble_container.grid_columnconfigure(1, weight=1)
         col = 0
         bg_color = self.colors['surface']
         fg_color = self.colors['text_primary']
         bubble_style = 'AssistantBubble.TFrame'
         anchor = "w"
      
      bubble = ttk.Frame(bubble_container, style=bubble_style, padding=(20, 12))
      bubble.grid(row=0, column=col, sticky=anchor)
      
      msg_widget = create_markdown_message(
         bubble,
         text,
         fonts={'text': self.font_text, 'mono': self.font_mono},
         colors=self.colors,
         bg_color=bg_color,
         fg_color=fg_color,
         is_user=is_user,
      )
      msg_widget.pack(fill="both", expand=True)
      
      time_str = datetime.now().strftime("%H:%M:%S")
      time_label = ttk.Label(
         bubble_container,
         text=time_str,
         style='ChatMuted.TLabel',
      )
      time_label.grid(row=1, column=col, sticky=anchor, pady=(5, 0))
      
      self.messages_frame.update_idletasks()
      self.chat_canvas.yview_moveto(1.0)
      return bubble_container
      
   def animate_typing(self, label, text, index=0):
      if index < len(text):
         label.config(text=text[:index+1])
         self.root.after(15, lambda: self.animate_typing(label, text, index+1))
         
   def add_system_message(self, title, message):
      container = ttk.Frame(self.messages_frame, style='City.TFrame')
      container.pack(fill="x", padx=30, pady=30)
      container.grid_columnconfigure(0, weight=1)
      
      inner = ttk.Frame(container, style='Card.TFrame', padding=(40, 25))
      inner.grid(row=0, column=0)
      
      ttk.Label(inner, text=title, style='SystemTitle.TLabel').pack()
      ttk.Label(
         inner,
         text=message,
         style='CardMuted.TLabel',
         font=self.font_text,
         wraplength=600,
      ).pack(pady=(15, 0))
      
      self.messages_frame.update_idletasks()
      self.chat_canvas.yview_moveto(1.0)
      
   def add_loading_indicator(self):
      self.loading_frame = ttk.Frame(self.messages_frame, style='City.TFrame')
      self.loading_frame.pack(fill="x", padx=30, pady=15)
      dots = ttk.Label(
         self.loading_frame,
         text="● ● ●",
         style='City.TLabel',
         font=("Segoe UI", 24, "bold"),
         foreground=self.colors['accent'],
      )
      dots.pack()
      
      def animate_dots(count=0):
         if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
               colors = [self.colors['accent'] if i == count % 3 else self.colors['bg_tertiary'] for i in range(3)]
               dots.config(foreground=colors[0])
               self.root.after(400, lambda: animate_dots(count + 1))
      animate_dots()
      self.messages_frame.update_idletasks()
      self.chat_canvas.yview_moveto(1.0)
      
   def remove_loading_indicator(self):
      if hasattr(self, 'loading_frame'):
         self.loading_frame.destroy()
         delattr(self, 'loading_frame')
         
   def send_message(self):
      if self.is_processing: return
      message = self.input_text.get("1.0", "end-1c").strip()
      if not message or message == "Digite sua mensagem...": return
      self.input_text.delete("1.0", "end")
      self.input_text.insert("1.0", "Digite sua mensagem...")
      self.input_text.config(fg=self.colors['text_secondary'])
      self.add_message_bubble(message, is_user=True)
      self.is_processing = True
      self.set_status("●  Processando...", 'warning')
      self.add_loading_indicator()
      thread = threading.Thread(target=self.process_message, args=(message,))
      thread.daemon = True
      thread.start()
      
   def process_message(self, message):
      try:
         messages = self.conversation_history + [("user", message)]
         response = self.bot.resposta_bot(messages, self.current_context)
         self.root.after(0, lambda: self.show_response(response, message))
      except Exception as e:
         error_message = str(e)
         self.root.after(0, lambda: self.show_error(error_message))
         
   def show_response(self, response, user_message):
      self.remove_loading_indicator()
      self.add_message_bubble(response, is_user=False)
      self.conversation_history.extend([("user", user_message), ("assistant", response)])
      self.bot.save_conversation(user_message, response)
      self.is_processing = False
      self.set_status("●  Pronto", 'success')
      
   def show_error(self, error_msg):
      self.remove_loading_indicator()
      self.add_message_bubble(f"❌ Erro: {error_msg}", is_user=False, animate=False)
      self.is_processing = False
      self.set_status("●  Erro", 'error')
      
   def set_chat_mode(self):
      self.current_context = ""
      self.context_label.config(text="Chat Livre")
      self.add_system_message("💬 Modo Chat Livre", "Pergunte o que quiser. Estou pronto para conversar!")

   def set_loaded_context(self, content):
      if not content or not content.strip():
         raise ValueError('Não foi possível extrair conteúdo dessa fonte.')
      self.current_context = content

   def show_context_error(self, error_message):
      self.set_status("●  Erro", 'error')
      messagebox.showerror("Erro", error_message)
      
   def load_website(self):
      self.show_input_dialog("Carregar Site", "Digite a URL do site:", self.process_website)
      
   def process_website(self, url):
      if not url: return
      self.set_status("●  Carregando site...", 'warning')
      def load():
         try:
            content = self.bot.carrega_site(url)
            self.set_loaded_context(content)
            self.root.after(0, lambda: self.on_context_loaded("Site", f"{url[:50]}..."))
         except Exception as e:
            error_message = str(e)
            self.root.after(0, lambda: self.show_context_error(error_message))
      threading.Thread(target=load, daemon=True).start()
      
   def load_video(self):
      self.show_input_dialog("Carregar Vídeo", "Digite a URL do YouTube:", self.process_video)
      
   def process_video(self, url):
      if not url: return
      self.set_status("●  Carregando vídeo...", 'warning')
      def load():
         try:
            content = self.bot.carrega_video(url)
            self.set_loaded_context(content)
            self.root.after(0, lambda: self.on_context_loaded("Vídeo", url))
         except Exception as e:
            error_message = str(e)
            self.root.after(0, lambda: self.show_context_error(error_message))
      threading.Thread(target=load, daemon=True).start()
      
   def load_pdf(self):
      filename = filedialog.askopenfilename(title="Selecionar PDF", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
      if filename:
         self.set_status("●  Carregando PDF...", 'warning')
         def load():
            try:
               content = self.bot.carrega_pdf(filename)
               self.set_loaded_context(content)
               self.root.after(0, lambda: self.on_context_loaded("PDF", os.path.basename(filename)))
            except Exception as e:
               error_message = str(e)
               self.root.after(0, lambda: self.show_context_error(error_message))
         threading.Thread(target=load, daemon=True).start()
         
   def load_image_ocr(self):
      filename = filedialog.askopenfilename(title="Selecionar Imagem", filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All files", "*.*")])
      if filename:
         nome = os.path.splitext(os.path.basename(filename))[0]
         self.set_status("●  Processando OCR...", 'warning')
         def load():
            try:
               content = self.bot.carrega_imagem_ocr(filename, nome)
               self.set_loaded_context(content)
               self.root.after(0, lambda: self.on_context_loaded("OCR", os.path.basename(filename)))
            except Exception as e:
               error_message = str(e)
               self.root.after(0, lambda: self.show_context_error(error_message))
         threading.Thread(target=load, daemon=True).start()
         
   def on_context_loaded(self, tipo, nome):
      self.context_label.config(text=f"{tipo}: {nome}")
      self.add_system_message(f"✅ {tipo} Carregado", f"Agora você pode fazer perguntas sobre: {nome}")
      self.set_status("●  Pronto", 'success')
      
   def clear_chat(self):
      if self.is_processing:
         messagebox.showwarning("Aguarde", "Espere a resposta atual terminar antes de limpar a conversa.")
         return

      if not messagebox.askyesno("Limpar conversa", "Deseja apagar permanentemente todo o histórico de conversas?"):
         return

      self.bot.limpar_conversas()
      for widget in self.messages_frame.winfo_children(): widget.destroy()
      self.conversation_history = []
      self.current_context = ""
      self.context_label.config(text="Chat Livre")
      self.add_system_message("🗑️ Conversa Limpa", "O histórico foi apagado. Comece uma nova conversa!")
      
   def show_input_dialog(self, title, prompt, callback):
      dialog = tk.Toplevel(self.root)
      dialog.title(title)
      dialog.geometry("550x220")
      dialog.configure(bg=self.colors['bg_secondary'])
      dialog.transient(self.root)
      dialog.grab_set()
      dialog.update_idletasks()
      x = (dialog.winfo_screenwidth() // 2) - 275
      y = (dialog.winfo_screenheight() // 2) - 110
      dialog.geometry(f"+{x}+{y}")

      container = ttk.Frame(dialog, style='Sidebar.TFrame', padding=(28, 24))
      container.pack(fill="both", expand=True)

      ttk.Label(
         container,
         text=prompt,
         style='Sidebar.TLabel',
         font=self.font_text,
      ).pack(anchor="w", pady=(0, 16))

      entry = ttk.Entry(
         container,
         font=self.font_text,
         width=45,
         style='Dialog.TEntry',
      )
      entry.pack(fill="x", ipady=7)
      entry.focus()
      def on_ok():
         value = entry.get(); dialog.destroy(); callback(value)
      btn_frame = ttk.Frame(container, style='Sidebar.TFrame')
      btn_frame.pack(pady=(24, 0), anchor="e")
      ttk.Button(
         btn_frame,
         text="Cancelar",
         command=dialog.destroy,
         style='Ghost.TButton',
      ).pack(side="left", padx=5)
      ttk.Button(
         btn_frame,
         text="OK",
         command=on_ok,
         style='Accent.TButton',
      ).pack(side="left", padx=5)
      entry.bind("<Return>", lambda e: on_ok())

if __name__ == "__main__":
   root = tk.Tk()
   app = ModernCityBotGUI(root)
   root.mainloop()

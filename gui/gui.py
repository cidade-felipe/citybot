import contextlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Canvas
from tkinter import font as tkfont
import threading
from datetime import datetime
import os
import sys
from PIL import Image, ImageTk

# Adicionar o diretório atual ao path para importar o CityBot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
   from citybot import CityBot
except ImportError:
   # Classe mock para testes visuais
   class CityBot:
      def __init__(self):
         self.memory = None
      def carrega_site(self, url):
         return f"Conteúdo simulado do site: {url}"
      def carrega_video(self, url):
         return f"Transcrição simulada do vídeo: {url}"
      def carrega_pdf(self, path):
         return f"Conteúdo simulado do PDF: {path}"
      def carrega_imagem_ocr(self, path, nome):
         return f"Texto OCR simulado da imagem: {nome}"
      def resposta_bot(self, mensagens, doc=''):
         return f"Resposta simulada do bot para: {mensagens[-1][1] if mensagens else '...'}"
      def save_conversation(self, user_msg, bot_resp):
         pass

class ModernCityBotGUI:
   def __init__(self, root):
      self.root = root
      self.root.title("CityBot - Assistente Inteligente")
      self.root.geometry("1400x850")
      self.root.minsize(1200, 700)
      self.root.configure(bg="#0f0f0f")
      
      # Cores do tema cyber/dark moderno
      self.colors = {
         'bg_primary': "#0f0f0f",
         'bg_secondary': "#1a1a1a",
         'bg_tertiary': "#252525",
         'accent': "#00d4ff",
         'accent_secondary': "#0099cc",
         'text_primary': "#ffffff",
         'text_secondary': "#b0b0b0",
         'success': "#00ff88",
         'warning': "#ffaa00",
         'error': "#ff4444",
         'border': "#333333"
      }
      
      # Configurar estilos
      self.setup_styles()
      
      # Inicializar bot
      self.bot = CityBot()
      self.current_context = ""
      self.conversation_history = []
      self.is_processing = False
      
      # Criar interface
      self.create_layout()
      self.create_sidebar()
      self.create_chat_area()
      self.create_input_area()
      self.create_status_bar()
      
      # Bindings
      self.root.bind("<Return>", lambda e: None if e.state & 0x1 else self.send_message())
      self.root.bind("<Shift-Return>", lambda e: None)
      
      # Animação inicial
      self.animate_startup()
      
   def setup_styles(self):
      style = ttk.Style()
      style.theme_use('clam')
      
      # Configurar fontes
      self.font_title = tkfont.Font(family="Segoe UI", size=16, weight="bold")
      self.font_text = tkfont.Font(family="Segoe UI", size=11)
      self.font_mono = tkfont.Font(family="Consolas", size=10)
      self.font_small = tkfont.Font(family="Segoe UI", size=10)
      self.font_menu = tkfont.Font(family="Segoe UI", size=11)
      
   def create_layout(self):
      # Grid principal
      self.root.grid_columnconfigure(1, weight=1)
      self.root.grid_rowconfigure(0, weight=1)
      
   def create_sidebar(self):

      self.sidebar = tk.Frame(self.root, bg=self.colors['bg_secondary'], width=320)
      self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
      self.sidebar.grid_propagate(False)
      self.sidebar.pack_propagate(False)
      
      # Canvas com scrollbar para sidebar (caso seja necessário scroll)
      sidebar_canvas = tk.Canvas(self.sidebar, bg=self.colors['bg_secondary'], 
                                 highlightthickness=0, width=320)
      sidebar_canvas.pack(side="left", fill="both", expand=True)
      
      scrollbar = ttk.Scrollbar(self.sidebar, orient="vertical", 
                              command=sidebar_canvas.yview)
      scrollbar.pack(side="right", fill="y")
      
      sidebar_canvas.configure(yscrollcommand=scrollbar.set)
      
      # Frame interno para conteúdo
      self.sidebar_content = tk.Frame(sidebar_canvas, bg=self.colors['bg_secondary'], width=300)
      self.sidebar_window = sidebar_canvas.create_window((0, 0), 
                                                         window=self.sidebar_content,
                                                         anchor="nw", width=300)
      
      self.sidebar_content.bind("<Configure>", 
                              lambda e: sidebar_canvas.configure(
                                    scrollregion=sidebar_canvas.bbox("all")))
      
      # Logo/Header
      header = tk.Frame(self.sidebar_content, bg=self.colors['bg_secondary'], height=100)
      header.pack(fill="x", padx=20, pady=25)
      header.pack_propagate(False)
      # Carregar logo
      logo_img = Image.open("logo.png")
      logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
      logo_tk = ImageTk.PhotoImage(logo_img)

      # Substituir no header
      logo_label = tk.Label(header,image=logo_tk, bg=self.colors['bg_secondary'])
      logo_label.pack(side="left", padx=(0, 15))

      logo_label.image = logo_tk
      
      # Animação
      self.pulse_animation()
      
      # Título
      title_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
      title_frame.pack(side="left", fill="y")
      
      tk.Label(title_frame, text="CityBot", font=self.font_title, 
               bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor="w")
      tk.Label(title_frame, text="Assistente IA", font=self.font_small, 
               bg=self.colors['bg_secondary'], fg=self.colors['accent']).pack(anchor="w")
      
      # Separador
      tk.Frame(self.sidebar_content, bg=self.colors['border'], height=2).pack(fill="x", padx=20, pady=15)
      
      # Menu de fontes de dados
      menu_label = tk.Label(self.sidebar_content, text="FONTES DE DADOS", 
                           font=("Segoe UI", 9, "bold"),
                           bg=self.colors['bg_secondary'], 
                           fg=self.colors['text_secondary'])
      menu_label.pack(anchor="w", padx=25, pady=(15, 10))
      
      # Botões do menu
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
      
      # Separador
      tk.Frame(self.sidebar_content, bg=self.colors['border'], height=2).pack(fill="x", padx=20, pady=20)
      
      # Informações do contexto atual
      context_container = tk.Frame(self.sidebar_content, bg=self.colors['bg_secondary'])
      context_container.pack(fill="x", padx=20, pady=10)
      
      tk.Label(context_container, text="📋 Contexto Atual", 
               font=("Segoe UI", 10, "bold"),
               bg=self.colors['bg_secondary'], 
               fg=self.colors['accent']).pack(anchor="w")
      
      # Frame do contexto com borda
      self.context_frame = tk.Frame(context_container, bg=self.colors['bg_tertiary'], 
                                    highlightbackground=self.colors['accent'], 
                                    highlightthickness=2, bd=0)
      self.context_frame.pack(fill="x", pady=(10, 0), ipady=10)
      
      self.context_label = tk.Label(self.context_frame, text="Chat Livre", 
                                    font=self.font_small, 
                                    wraplength=240,
                                    bg=self.colors['bg_tertiary'], 
                                    fg=self.colors['text_primary'])
      self.context_label.pack(anchor="w", padx=15, pady=10)
      
      # Botão limpar conversa
      self.create_menu_button("🗑️  Limpar Conversa", self.clear_chat, 
                              bg=self.colors['error']).pack(fill="x", padx=20, pady=30)
      
   def create_menu_button(self, text, command, bg=None):
      bg_color = bg or self.colors['bg_secondary']
      hover_color = bg_color if bg else self.colors['bg_tertiary']
      
      btn = tk.Frame(self.sidebar_content, bg=bg_color, height=45, cursor="hand2")
      btn.pack_propagate(False)
      
      label = tk.Label(btn, text=text, font=self.font_menu, bg=bg_color, 
                     fg=self.colors['text_primary'], cursor="hand2",
                     anchor="w")
      label.pack(side="left", padx=20, fill="x", expand=True)
      
      # Efeito hover
      def on_enter(e):
         if not bg:
               btn.config(bg=hover_color)
               label.config(bg=hover_color)
      
      def on_leave(e):
         if not bg:
               btn.config(bg=bg_color)
               label.config(bg=bg_color)
      
      btn.bind("<Enter>", on_enter)
      btn.bind("<Leave>", on_leave)
      label.bind("<Enter>", on_enter)
      label.bind("<Leave>", on_leave)
      btn.bind("<Button-1>", lambda e: command())
      label.bind("<Button-1>", lambda e: command())
      
      return btn
      
   def create_chat_area(self):
      # Container principal do chat
      self.chat_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
      self.chat_container.grid(row=0, column=1, sticky="nsew")
      self.chat_container.grid_columnconfigure(0, weight=1)
      self.chat_container.grid_rowconfigure(0, weight=1)
      
      # Área de mensagens com scroll
      self.chat_canvas = tk.Canvas(self.chat_container, bg=self.colors['bg_primary'], 
                                 highlightthickness=0)
      scrollbar = ttk.Scrollbar(self.chat_container, orient="vertical", 
                              command=self.chat_canvas.yview)
      
      self.chat_canvas.configure(yscrollcommand=scrollbar.set)
      
      self.chat_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
      scrollbar.grid(row=0, column=1, sticky="ns")
      
      # Frame interno para as mensagens
      self.messages_frame = tk.Frame(self.chat_canvas, bg=self.colors['bg_primary'])
      self.canvas_window = self.chat_canvas.create_window((0, 0), 
                                                         window=self.messages_frame, 
                                                         anchor="nw")
      
      self.messages_frame.bind("<Configure>", self.on_frame_configure)
      self.chat_canvas.bind("<Configure>", self.on_canvas_configure)
      
      # Bind mousewheel
      self.chat_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
      
      # Mensagem de boas-vindas
      self.add_system_message("👋 Bem-vindo ao CityBot!", 
                              "Sou seu assistente inteligente. Escolha uma opção no menu lateral ou comece a conversar.")
      
   def create_input_area(self):
      # Frame de input
      input_frame = tk.Frame(self.chat_container, bg=self.colors['bg_secondary'], height=160)
      input_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=25)
      input_frame.grid_propagate(False)
      input_frame.grid_columnconfigure(0, weight=1)
      
      # Container do input
      input_container = tk.Frame(input_frame, bg=self.colors['bg_tertiary'], 
                                 highlightbackground=self.colors['border'],
                                 highlightthickness=1)
      input_container.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
      input_container.grid_columnconfigure(0, weight=1)
      
      # Text area
      self.input_text = tk.Text(input_container, height=3, 
                              bg=self.colors['bg_tertiary'],
                              fg=self.colors['text_primary'], 
                              font=self.font_text,
                              wrap="word", bd=0, highlightthickness=0,
                              insertbackground=self.colors['accent'],
                              padx=10, pady=10)
      self.input_text.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
      
      # Placeholder
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
      
      # Botão de enviar
      send_btn = tk.Button(input_container, text="➤", 
                           font=("Segoe UI", 18, "bold"),
                           bg=self.colors['accent'], 
                           fg=self.colors['bg_primary'],
                           activebackground=self.colors['accent_secondary'],
                           activeforeground=self.colors['text_primary'],
                           bd=0, cursor="hand2", command=self.send_message,
                           width=3, height=1)
      send_btn.grid(row=0, column=1, padx=15, pady=10)
      
      # Label de dica
      hint_label = tk.Label(input_frame, 
                           text="💡 Enter para enviar  •  Shift+Enter para nova linha",
                           font=self.font_small, 
                           bg=self.colors['bg_secondary'],
                           fg=self.colors['text_secondary'])
      hint_label.grid(row=1, column=0, sticky="w", padx=15)
      
   def create_status_bar(self):
      self.status_bar = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=35)
      self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
      self.status_bar.grid_propagate(False)
      
      self.status_label = tk.Label(self.status_bar, text="●  Pronto", 
                                 font=self.font_small,
                                 bg=self.colors['bg_secondary'], 
                                 fg=self.colors['success'])
      self.status_label.pack(side="left", padx=25)
      
      # Hora
      self.time_label = tk.Label(self.status_bar, text="", 
                                 font=self.font_small,
                                 bg=self.colors['bg_secondary'], 
                                 fg=self.colors['text_secondary'])
      self.time_label.pack(side="right", padx=25)
      self.update_time()
      
   def update_time(self):
      current_time = datetime.now().strftime("%H:%M:%S")
      self.time_label.config(text=current_time)
      self.root.after(1000, self.update_time)
      
   def pulse_animation(self):
      """Animação de pulso no logo"""
      def animate():
         with contextlib.suppress(Exception):
            for i in range(10):
               scale = 1 + (i * 0.05)
               self.root.after(50)
            self.root.after(2000, animate)

      animate()
      
   def animate_startup(self):
      """Animação de entrada"""
      pass
      
   def on_frame_configure(self, event=None):
      self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
      
   def on_canvas_configure(self, event):
      self.chat_canvas.itemconfig(self.canvas_window, width=event.width)
      
   def on_mousewheel(self, event):
      self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
      
   def add_message_bubble(self, text, is_user=True, animate=True):
      """Adiciona uma bolha de mensagem moderna"""
      bubble_container = tk.Frame(self.messages_frame, 
                                 bg=self.colors['bg_primary'])
      bubble_container.pack(fill="x", padx=30, pady=8)
      
      # Alinhar à direita se for usuário, esquerda se for bot
      if is_user:
         bubble_container.grid_columnconfigure(0, weight=1)
         col = 1
         bg_color = self.colors['accent']
         fg_color = self.colors['bg_primary']
         anchor = "e"
      else:
         bubble_container.grid_columnconfigure(1, weight=1)
         col = 0
         bg_color = self.colors['bg_tertiary']
         fg_color = self.colors['text_primary']
         anchor = "w"
      
      # Frame da bolha
      bubble = tk.Frame(bubble_container, bg=bg_color, padx=20, pady=12)
      bubble.grid(row=0, column=col, sticky=anchor)
      
      # Label da mensagem - AUMENTADO wraplength
      msg_label = tk.Label(bubble, text=text, font=self.font_text, 
                           bg=bg_color, fg=fg_color, 
                           wraplength=700, justify="left")
      msg_label.pack()
      
      # Timestamp
      time_str = datetime.now().strftime("%H:%M:%S")
      time_label = tk.Label(bubble_container, text=time_str, 
                           font=self.font_small,
                           bg=self.colors['bg_primary'], 
                           fg=self.colors['text_secondary'])
      time_label.grid(row=1, column=col, sticky=anchor, pady=(5, 0))
      
      # Animação de digitação se for mensagem do bot
      if not is_user and animate:
         msg_label.config(text="")
         self.animate_typing(msg_label, text)
      
      # Scroll para o final
      self.messages_frame.update_idletasks()
      self.chat_canvas.yview_moveto(1.0)
      
      return bubble_container
      
   def animate_typing(self, label, text, index=0):
      """Animação de digitação"""
      if index < len(text):
         label.config(text=text[:index+1])
         self.root.after(15, lambda: self.animate_typing(label, text, index+1))
         
   def add_system_message(self, title, message):
      """Adiciona mensagem de sistema centralizada"""
      container = tk.Frame(self.messages_frame, 
                           bg=self.colors['bg_primary'])
      container.pack(fill="x", padx=30, pady=30)
      
      # Centralizar
      container.grid_columnconfigure(0, weight=1)
      
      inner = tk.Frame(container, bg=self.colors['bg_secondary'], 
                     padx=40, pady=25)
      inner.grid(row=0, column=0)
      
      tk.Label(inner, text=title, font=self.font_title, 
               bg=self.colors['bg_secondary'],
               fg=self.colors['accent']).pack()
      tk.Label(inner, text=message, font=self.font_text, 
               bg=self.colors['bg_secondary'],
               fg=self.colors['text_secondary'], 
               wraplength=600).pack(pady=(15, 0))
      
      self.messages_frame.update_idletasks()
      self.chat_canvas.yview_moveto(1.0)
      
   def add_loading_indicator(self):
      """Adiciona indicador de carregamento"""
      self.loading_frame = tk.Frame(self.messages_frame, 
                                    bg=self.colors['bg_primary'])
      self.loading_frame.pack(fill="x", padx=30, pady=15)
      
      dots = tk.Label(self.loading_frame, text="● ● ●", 
                     font=("Segoe UI", 24, "bold"),
                     bg=self.colors['bg_primary'], 
                     fg=self.colors['accent'])
      dots.pack()
      
      # Animação
      def animate_dots(count=0):
         if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
               colors = [self.colors['accent'] if i == count % 3 
                        else self.colors['bg_tertiary'] 
                        for i in range(3)]
               dots.config(fg=colors[0])
               self.root.after(400, lambda: animate_dots(count + 1))
      
      animate_dots()
      self.messages_frame.update_idletasks()
      self.chat_canvas.yview_moveto(1.0)
      
   def remove_loading_indicator(self):
      if hasattr(self, 'loading_frame'):
         self.loading_frame.destroy()
         delattr(self, 'loading_frame')
         
   def send_message(self):
      if self.is_processing:
         return
         
      message = self.input_text.get("1.0", "end-1c").strip()
      if not message or message == "Digite sua mensagem...":
         return
         
      # Limpar input
      self.input_text.delete("1.0", "end")
      self.input_text.insert("1.0", "Digite sua mensagem...")
      self.input_text.config(fg=self.colors['text_secondary'])
      
      # Adicionar mensagem do usuário
      self.add_message_bubble(message, is_user=True)
      
      # Processar em thread separada
      self.is_processing = True
      self.status_label.config(text="●  Processando...", 
                              fg=self.colors['warning'])
      self.add_loading_indicator()
      
      thread = threading.Thread(target=self.process_message, 
                              args=(message,))
      thread.daemon = True
      thread.start()
      
   def process_message(self, message):
      try:
         # Preparar mensagens para o bot
         messages = [("user", msg) for msg in self.conversation_history] + [("user", message)]
         
         # Obter resposta
         response = self.bot.resposta_bot(messages, self.current_context)
         
         # Atualizar UI na thread principal
         self.root.after(0, lambda: self.show_response(response, message))
      except Exception as e:
         self.root.after(0, lambda: self.show_error(str(e)))
         
   def show_response(self, response, user_message):
      self.remove_loading_indicator()
      self.add_message_bubble(response, is_user=False)
      
      # Salvar conversa
      self.conversation_history.extend([user_message, response])
      self.bot.save_conversation(user_message, response)
      
      self.is_processing = False
      self.status_label.config(text="●  Pronto", fg=self.colors['success'])
      
   def show_error(self, error_msg):
      self.remove_loading_indicator()
      self.add_message_bubble(f"❌ Erro: {error_msg}", 
                              is_user=False, animate=False)
      self.is_processing = False
      self.status_label.config(text="●  Erro", fg=self.colors['error'])
      
   def set_chat_mode(self):
      self.current_context = ""
      self.context_label.config(text="Chat Livre")
      self.add_system_message("💬 Modo Chat Livre", 
                              "Pergunte o que quiser. Estou pronto para conversar!")
      
   def load_website(self):
      self.show_input_dialog("Carregar Site", 
                           "Digite a URL do site:", 
                           self.process_website)
      
   def process_website(self, url):
      if not url:
         return
      self.status_label.config(text="●  Carregando site...", 
                              fg=self.colors['warning'])

      def load():
         try:
            content = self.bot.carrega_site(url)
            self.current_context = content
            self.root.after(0, lambda: self.on_context_loaded("Site", f"{url[:50]}..."))
         except Exception as e:
               self.root.after(0, lambda: messagebox.showerror("Erro", str(e)))

      threading.Thread(target=load, daemon=True).start()
      
   def load_video(self):
      self.show_input_dialog("Carregar Vídeo", 
                           "Digite a URL do YouTube:", 
                           self.process_video)
      
   def process_video(self, url):
      if not url:
         return
      self.status_label.config(text="●  Carregando vídeo...", 
                              fg=self.colors['warning'])
      
      def load():
         try:
               content = self.bot.carrega_video(url)
               self.current_context = content
               self.root.after(0, lambda: self.on_context_loaded("Vídeo", url))
         except Exception as e:
               self.root.after(0, lambda: messagebox.showerror("Erro", str(e)))
               
      threading.Thread(target=load, daemon=True).start()
      
   def load_pdf(self):
      filename = filedialog.askopenfilename(
         title="Selecionar PDF",
         filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
      )
      if filename:
         self.status_label.config(text="●  Carregando PDF...", 
                                 fg=self.colors['warning'])
         
         def load():
               try:
                  content = self.bot.carrega_pdf(filename)
                  self.current_context = content
                  self.root.after(0, lambda: self.on_context_loaded(
                     "PDF", 
                     os.path.basename(filename)))
               except Exception as e:
                  self.root.after(0, lambda: messagebox.showerror("Erro", str(e)))
                  
         threading.Thread(target=load, daemon=True).start()
         
   def load_image_ocr(self):
      filename = filedialog.askopenfilename(
         title="Selecionar Imagem",
         filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"), 
                     ("All files", "*.*")]
      )
      if filename:
         nome = os.path.splitext(os.path.basename(filename))[0]
         self.status_label.config(text="●  Processando OCR...", 
                                 fg=self.colors['warning'])
         
         def load():
               try:
                  content = self.bot.carrega_imagem_ocr(filename, nome)
                  self.current_context = content
                  self.root.after(0, lambda: self.on_context_loaded(
                     "OCR", 
                     os.path.basename(filename)))
               except Exception as e:
                  self.root.after(0, lambda: messagebox.showerror("Erro", str(e)))
                  
         threading.Thread(target=load, daemon=True).start()
         
   def on_context_loaded(self, tipo, nome):
      self.context_label.config(text=f"{tipo}: {nome}")
      self.add_system_message(f"✅ {tipo} Carregado", 
                              f"Agora você pode fazer perguntas sobre: {nome}")
      self.status_label.config(text="●  Pronto", fg=self.colors['success'])
      
   def clear_chat(self):
      for widget in self.messages_frame.winfo_children():
         widget.destroy()
      self.conversation_history = []
      self.add_system_message("🗑️ Conversa Limpa", 
                              "O histórico foi apagado. Comece uma nova conversa!")
      
   def show_input_dialog(self, title, prompt, callback):
      """Diálogo de input moderno"""
      dialog = tk.Toplevel(self.root)
      dialog.title(title)
      dialog.geometry("550x220")
      dialog.configure(bg=self.colors['bg_secondary'])
      dialog.transient(self.root)
      dialog.grab_set()
      
      # Centralizar
      dialog.update_idletasks()
      x = (dialog.winfo_screenwidth() // 2) - (275)
      y = (dialog.winfo_screenheight() // 2) - (110)
      dialog.geometry(f"+{x}+{y}")
      
      tk.Label(dialog, text=prompt, font=self.font_text,
               bg=self.colors['bg_secondary'], 
               fg=self.colors['text_primary']).pack(pady=25)
      
      entry = tk.Entry(dialog, font=self.font_text, width=45,
                     bg=self.colors['bg_tertiary'], 
                     fg=self.colors['text_primary'],
                     insertbackground=self.colors['accent'], 
                     bd=0, highlightthickness=1,
                     highlightbackground=self.colors['border'])
      entry.pack(pady=10, ipady=8)
      entry.focus()
      
      def on_ok():
         value = entry.get()
         dialog.destroy()
         callback(value)
         
      def on_cancel():
         dialog.destroy()
         
      btn_frame = tk.Frame(dialog, bg=self.colors['bg_secondary'])
      btn_frame.pack(pady=25)
      
      tk.Button(btn_frame, text="Cancelar", command=on_cancel,
               bg=self.colors['bg_tertiary'], 
               fg=self.colors['text_primary'],
               activebackground=self.colors['border'], 
               bd=0, padx=25, pady=10,
               font=self.font_text).pack(side="left", padx=5)
      
      tk.Button(btn_frame, text="OK", command=on_ok,
               bg=self.colors['accent'], 
               fg=self.colors['bg_primary'],
               activebackground=self.colors['accent_secondary'], 
               bd=0, padx=35, pady=10,
               font=self.font_text).pack(side="left", padx=5)
      
      entry.bind("<Return>", lambda e: on_ok())

if __name__ == "__main__":
   root = tk.Tk()
   app = ModernCityBotGUI(root)
   root.mainloop()
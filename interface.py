import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import os
from citybot import CityBot
city = CityBot()
memory = city.memory
janela_princiapal = tk.Tk()
janela_princiapal.title('CityBot')
janela_princiapal.resizable(False, True)
mensagens = list(city.load_conversations())

def exibir_mensagem(remetente, texto):
   cor = '#e0ffe0' if remetente == 'Você' else "#98e9e8"
   lbl = tk.Label(frame_mensagens, text=f"{remetente}: {texto}", bg=cor,
                  wraplength=600, justify='left', anchor='w', padx=10, pady=5)
   lbl.pack(fill='x', padx=10, pady=5, anchor='w')
   canvas.update_idletasks()
   canvas.yview_moveto(1.0)  # rola pro final automaticamente
   entry_enviar.delete(0, tk.END)

def enviar_texto():
   global mensagens
   
   pergunta = entry_enviar.get()
   if not pergunta:
      return
   tk.Label(frame_mensagens, bg='white', anchor='w').pack(fill='x', padx=5, pady=2)
   exibir_mensagem('Você', pergunta)
   # entry_enviar.delete(0, tk.END)
   mensagens.append(('user', pergunta))
   resposta = city.resposta_bot(mensagens, texto)
   mensagens.append(('assistant', resposta))
   salvar(pergunta, resposta)
   exibir_mensagem('CityBot', resposta)
   # Atualiza região de scroll
   frame_mensagens.update_idletasks()
   canvas.config(scrollregion=canvas.bbox("all"))

# --- Widgets ---
def escolher_pdf():
   global mensagens
   
   try:
      arquivo = filedialog.askopenfile(title='SELECIONE UM ARQUIVO EM PDF',
                                       filetypes=[('Arquivos em PDF', '*.pdf')])
      if arquivo:
         caminho = Path(arquivo.name)
         nome_arquivo = caminho.name
         confirmar = messagebox.askyesno('SELECIONAR ARQUIVO', f'Deseja abrir {nome_arquivo}?')
         texto = city.carrega_pdf(arquivo.name  )
         if confirmar:
            pergunta = entry_enviar.get().strip()
            mensagens.append(('user', pergunta))
            resposta = city.resposta_bot(mensagens, texto)
            mensagens.append(('assistant', resposta))
            salvar(pergunta, resposta)
            exibir_mensagem('CityBot', resposta)
            #exibir_mensagem('CityBot', f'PDF carregado com sucesso!\n\n{texto[:500]}...')
         else:
               messagebox.showwarning('CANCELADO!', 'Nenhum arquivo selecionado!')
   except Exception as e:
      messagebox.showerror('ERRO!', f'{e}')

def escolher_imagem():
   global mensagens
   
   try:
      arquivo = filedialog.askopenfile(title='SELECIONE UM ARQUIVO DE IMAGEM',
                                       filetypes=[('Imagens', '*.png *.jpg *.jpeg')])
      if arquivo:
         caminho = Path(arquivo.name)
         nome_arquivo = caminho.name
         confirmar = messagebox.askyesno('SELECIONAR ARQUIVO', f'Deseja abrir {nome_arquivo}?')
         texto = city.carrega_imagem_ocr(arquivo.name, nome_arquivo)
         if confirmar:
            pergunta = entry_enviar.get().strip()
            mensagens.append(('user', pergunta))
            resposta = city.resposta_bot(mensagens, texto)
            mensagens.append(('assistant', resposta))
            salvar(pergunta, resposta)
            exibir_mensagem('CityBot', resposta)
            #exibir_mensagem('CityBot', f'PDF carregado com sucesso!\n\n{texto[:500]}...')
         else:
            messagebox.showwarning('CANCELADO!', 'Nenhuma imagem selecionada!')
   except Exception as e:
      messagebox.showerror('ERRO!', f'{e}')
      
def escolher_site():
   global mensagens

   try:
      url = entry_enviar.get().strip()
      if not url:
         messagebox.showerror('ERRO!', 'Nenhum URL informado!')
         return
      texto = city.carrega_site(url)      
      pergunta = entry_enviar.get().strip()
      mensagens.append(('user', pergunta))
      resposta = city.resposta_bot(mensagens, texto)
      mensagens.append(('assistant', resposta))
      salvar(pergunta, resposta)
      exibir_mensagem('CityBot', resposta)
      #exibir_mensagem('CityBot', f'PDF carregado com sucesso!\n\n{texto[:500]}...')
   except Exception as e:
      messagebox.showerror('ERRO!', f'{e}')

def salvar(pergunta, resposta):
   memory.save_context({'input': pergunta}, {'output': resposta})
   city.save_conversation(pergunta, resposta)
   
   

style = ttk.Style()
style.configure('Custom.TLabel', foreground='black', font=('Arial', 20, 'bold'))
style.configure('Custom.TButton', padding=1, font=('Arial', 12), foreground='black', background='#add8e6')

logo_imagem = Image.open('./testes/logo.png')
logo_imagem = logo_imagem.resize((150,150))
logo = ImageTk.PhotoImage(logo_imagem)

frame_menu = tk.Frame(janela_princiapal, width=200,)
frame_menu.pack(side='right', fill='both')
lbl_logo = ttk.Label(frame_menu, image=logo).grid(row=0, column=0,)
#lbl_menu = ttk.Label(frame_menu, text='MENU', style='Custom.TLabel', ).grid(row=1, column=0, padx=1, pady=1)

# --- Frame do Chat ---
frame_chat = tk.Frame(janela_princiapal, bg='white', bd=2, relief='sunken')
frame_chat.pack(side='left', fill='both', expand=True, padx=10, pady=10)

# --- Canvas + Scrollbar ---
frame_canvas = tk.Frame(janela_princiapal)
frame_canvas.pack(fill='both', expand=True)
canvas = tk.Canvas(frame_canvas, bg='white', highlightthickness=0)
scrollbar = tk.Scrollbar(frame_canvas, orient='vertical', command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side='right', fill='y')
canvas.pack(side='left', fill='both', expand=True)
frame_mensagens = tk.Frame(canvas, bg='white')
canvas.create_window((0, 0), window=frame_mensagens, anchor='nw')

scrollbar.pack(side='right', fill='y')
canvas.pack(side='left', fill='both', expand=True)

frame_mensagens = tk.Frame(canvas, bg='white')
canvas.create_window((0, 0), window=frame_mensagens, anchor='nw')

# Atualiza região de scroll quando o tamanho do frame muda
def atualizar_scroll(event):
   canvas.configure(scrollregion=canvas.bbox("all"))

frame_mensagens.bind("<Configure>", atualizar_scroll)

frame_entry = tk.Frame(janela_princiapal, width=200,)
frame_entry.pack(fill='x', expand=True, padx=10, pady=0)
entry_enviar = ttk.Entry(frame_entry, width=100)
entry_enviar.grid(row=0, column=0, padx=10, pady=0, sticky='ew')
btn_enviar = ttk.Button(frame_entry, text='Enviar', style='Custom.TButton', width=10, command=enviar_texto).grid(row=0, column=5, padx=10, pady=0)

# --- Botões ---
botoes = {
   'Informações sobre um site': escolher_site,
   'Informações sobre um PDF': escolher_pdf,
   'OCR imagem': escolher_imagem,
   'Limpar banco de dados': city.limpar_banco,
   'Sair': janela_princiapal.destroy
}

lista_indices = []
lista_indices.extend(iter(range(1,len(botoes)+1)))

for i, (texto, comando) in zip(lista_indices,botoes.items()):
   ttk.Button(frame_menu, text=texto, style='Custom.TButton', width=30, command=comando).grid(row=i, column=0, padx=10, pady=5)




janela_princiapal.mainloop()
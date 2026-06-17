"""
Cliente de Chat TCP — Interface Gráfica (tkinter)
Trabalho de Redes de Computadores
"""

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import datetime

# ──────────────────────────────────────────
# Paleta de cores
# ──────────────────────────────────────────
COR_FUNDO        = "#1e1e2e"
COR_PAINEL       = "#2a2a3e"
COR_ENTRADA      = "#313145"
COR_BORDA        = "#44445a"
COR_TEXTO        = "#cdd6f4"
COR_SISTEMA      = "#a6e3a1"
COR_PRIVADO      = "#f9e2af"
COR_PROPRIA      = "#89b4fa"
COR_OUTRO        = "#cdd6f4"
COR_BOTAO        = "#89b4fa"
COR_BOTAO_TEXTO  = "#1e1e2e"
COR_DESTAQUE     = "#cba6f7"


class ChatCliente:
    def __init__(self, root):
        self.root = root
        self.root.title("PyChat — Conectando…")
        self.root.configure(bg=COR_FUNDO)
        self.root.minsize(720, 520)

        self.socket = None
        self.apelido = ""
        self.conectado = False

        self._construir_tela_login()

    # ──────────────────────────────────────
    # Tela de login
    # ──────────────────────────────────────
    def _construir_tela_login(self):
        self.frame_login = tk.Frame(self.root, bg=COR_FUNDO)
        self.frame_login.pack(expand=True)

        tk.Label(
            self.frame_login, text="💬 PyChat",
            font=("Segoe UI", 28, "bold"),
            bg=COR_FUNDO, fg=COR_DESTAQUE
        ).grid(row=0, column=0, columnspan=2, pady=(0, 6))

        tk.Label(
            self.frame_login, text="Chat em tempo real via sockets TCP",
            font=("Segoe UI", 11),
            bg=COR_FUNDO, fg=COR_BORDA
        ).grid(row=1, column=0, columnspan=2, pady=(0, 24))

        campos = [
            ("Servidor (IP):", "entry_host",  "127.0.0.1"),
            ("Porta:",         "entry_porta", "12345"),
            ("Seu apelido:",   "entry_apelido", ""),
        ]
        for i, (label, attr, placeholder) in enumerate(campos, start=2):
            tk.Label(
                self.frame_login, text=label,
                font=("Segoe UI", 11), bg=COR_FUNDO, fg=COR_TEXTO, anchor="w"
            ).grid(row=i, column=0, sticky="w", padx=8, pady=4)

            entry = tk.Entry(
                self.frame_login,
                font=("Segoe UI", 12), bg=COR_ENTRADA, fg=COR_TEXTO,
                insertbackground=COR_TEXTO, relief="flat",
                bd=0, highlightthickness=1, highlightcolor=COR_BORDA,
                highlightbackground=COR_BORDA, width=26
            )
            entry.insert(0, placeholder)
            entry.grid(row=i, column=1, padx=8, pady=4, ipady=6)
            setattr(self, attr, entry)

        tk.Button(
            self.frame_login, text="Conectar →",
            font=("Segoe UI", 12, "bold"),
            bg=COR_BOTAO, fg=COR_BOTAO_TEXTO,
            activebackground=COR_DESTAQUE, activeforeground=COR_BOTAO_TEXTO,
            relief="flat", cursor="hand2", padx=20, pady=8,
            command=self._conectar
        ).grid(row=5, column=0, columnspan=2, pady=20)

        self.root.bind("<Return>", lambda e: self._conectar())

    # ──────────────────────────────────────
    # Lógica de conexão
    # ──────────────────────────────────────
    def _conectar(self):
        host   = self.entry_host.get().strip()
        porta_str = self.entry_porta.get().strip()
        apelido = self.entry_apelido.get().strip()

        if not host or not porta_str or not apelido:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        try:
            porta = int(porta_str)
        except ValueError:
            messagebox.showerror("Erro", "Porta inválida.")
            return

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, porta))
        except Exception as e:
            messagebox.showerror("Erro de conexão", f"Não foi possível conectar:\n{e}")
            return

        # Protocolo de handshake: servidor pede "APELIDO"
        try:
            sinal = self.socket.recv(1024).decode('utf-8')
            if sinal == "APELIDO":
                self.socket.sendall(apelido.encode('utf-8'))
            # Verificar se houve erro de apelido duplicado
            resposta = self.socket.recv(1024).decode('utf-8')
            if resposta.startswith("ERRO:"):
                messagebox.showerror("Erro", resposta[5:])
                self.socket.close()
                return
            # Resposta ok → é a mensagem de boas-vindas, processamos depois
            self.apelido = apelido
            self.conectado = True
            self.frame_login.destroy()
            self.root.unbind("<Return>")
            self._construir_chat()
            # Processar a primeira mensagem recebida (boas-vindas)
            self._processar_mensagem(resposta)
            # Iniciar thread de recebimento
            threading.Thread(target=self._receber, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no handshake:\n{e}")
            self.socket.close()

    # ──────────────────────────────────────
    # Tela principal do chat
    # ──────────────────────────────────────
    def _construir_chat(self):
        self.root.title(f"PyChat — {self.apelido}")

        # Barra superior
        barra = tk.Frame(self.root, bg=COR_PAINEL, pady=8)
        barra.pack(fill="x")

        tk.Label(
            barra, text="💬 PyChat",
            font=("Segoe UI", 14, "bold"),
            bg=COR_PAINEL, fg=COR_DESTAQUE
        ).pack(side="left", padx=14)

        tk.Label(
            barra, text=f"Conectado como: {self.apelido}",
            font=("Segoe UI", 10),
            bg=COR_PAINEL, fg=COR_TEXTO
        ).pack(side="left", padx=6)

        tk.Button(
            barra, text="👥 Usuários",
            font=("Segoe UI", 9), bg=COR_ENTRADA, fg=COR_TEXTO,
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=lambda: self._enviar_raw("/usuarios")
        ).pack(side="right", padx=6)

        tk.Button(
            barra, text="✉ Privado",
            font=("Segoe UI", 9), bg=COR_ENTRADA, fg=COR_TEXTO,
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=self._dialog_privado
        ).pack(side="right", padx=2)

        tk.Button(
            barra, text="🔌 Sair",
            font=("Segoe UI", 9), bg="#f38ba8", fg=COR_BOTAO_TEXTO,
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=self._desconectar
        ).pack(side="right", padx=6)

        # Área de mensagens
        self.area_msgs = scrolledtext.ScrolledText(
            self.root,
            font=("Segoe UI", 11),
            bg=COR_FUNDO, fg=COR_TEXTO,
            bd=0, relief="flat",
            state="disabled",
            wrap="word",
            padx=12, pady=10
        )
        self.area_msgs.pack(fill="both", expand=True, padx=6, pady=(4, 0))

        # Configurar tags de cor
        self.area_msgs.tag_configure("sistema",  foreground=COR_SISTEMA,  font=("Segoe UI", 10, "italic"))
        self.area_msgs.tag_configure("privado",  foreground=COR_PRIVADO,  font=("Segoe UI", 11, "bold"))
        self.area_msgs.tag_configure("propria",  foreground=COR_PROPRIA)
        self.area_msgs.tag_configure("outro",    foreground=COR_OUTRO)
        self.area_msgs.tag_configure("nome",     font=("Segoe UI", 11, "bold"))

        # Área de entrada
        frame_entrada = tk.Frame(self.root, bg=COR_PAINEL, pady=8)
        frame_entrada.pack(fill="x", padx=6, pady=6)

        self.campo_msg = tk.Entry(
            frame_entrada,
            font=("Segoe UI", 12),
            bg=COR_ENTRADA, fg=COR_TEXTO,
            insertbackground=COR_TEXTO,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightcolor=COR_BOTAO,
            highlightbackground=COR_BORDA
        )
        self.campo_msg.pack(side="left", fill="x", expand=True, padx=(8, 6), ipady=8)
        self.campo_msg.bind("<Return>", lambda e: self._enviar_mensagem())
        self.campo_msg.focus()

        tk.Button(
            frame_entrada, text="Enviar ➤",
            font=("Segoe UI", 11, "bold"),
            bg=COR_BOTAO, fg=COR_BOTAO_TEXTO,
            activebackground=COR_DESTAQUE,
            relief="flat", cursor="hand2",
            padx=16, pady=6,
            command=self._enviar_mensagem
        ).pack(side="right", padx=8)

    # ──────────────────────────────────────
    # Envio de mensagens
    # ──────────────────────────────────────
    def _enviar_mensagem(self):
        texto = self.campo_msg.get().strip()
        if not texto or not self.conectado:
            return
        self.campo_msg.delete(0, tk.END)
        self._enviar_raw(texto)

    def _enviar_raw(self, texto):
        try:
            self.socket.sendall(texto.encode('utf-8'))
        except:
            self._mostrar_sistema("Erro ao enviar mensagem. Conexão perdida.")

    def _dialog_privado(self):
        destinatario = simpledialog.askstring("Mensagem Privada", "Nome do destinatário:")
        if not destinatario:
            return
        msg = simpledialog.askstring("Mensagem Privada", f"Mensagem para {destinatario}:")
        if msg:
            self._enviar_raw(f"/privado {destinatario} {msg}")

    # ──────────────────────────────────────
    # Recebimento e processamento
    # ──────────────────────────────────────
    def _receber(self):
        while self.conectado:
            try:
                dados = self.socket.recv(4096)
                if not dados:
                    break
                mensagem = dados.decode('utf-8')
                self.root.after(0, self._processar_mensagem, mensagem)
            except:
                break
        self.root.after(0, self._mostrar_sistema, "Desconectado do servidor.")
        self.conectado = False

    def _processar_mensagem(self, mensagem):
        for linha in mensagem.split('\n'):
            linha = linha.strip()
            if not linha:
                continue

            if linha.startswith("SISTEMA:"):
                self._mostrar_sistema(linha[8:])

            elif linha.startswith("MSG:"):
                # MSG:apelido:hora:texto
                partes = linha.split(':', 3)
                if len(partes) == 4:
                    _, nome, hora, texto = partes
                    self._mostrar_mensagem(nome, hora, texto, tag="outro")

            elif linha.startswith("MSG_PROPRIA:"):
                partes = linha.split(':', 3)
                if len(partes) == 4:
                    _, nome, hora, texto = partes
                    self._mostrar_mensagem(nome, hora, texto, tag="propria", prefixo="Você")

            elif linha.startswith("PRIVADO:"):
                partes = linha.split(':', 2)
                if len(partes) == 3:
                    _, remetente, texto = partes
                    self._mostrar_privado(f"[Privado de {remetente}]", texto)

            elif linha.startswith("PRIVADO_ENVIADO:"):
                partes = linha.split(':', 2)
                if len(partes) == 3:
                    _, dest, texto = partes
                    self._mostrar_privado(f"[Privado para {dest}]", texto)

            elif linha.startswith("ERRO:"):
                messagebox.showerror("Erro", linha[5:])

    # ──────────────────────────────────────
    # Renderização de mensagens
    # ──────────────────────────────────────
    def _mostrar_sistema(self, texto):
        self.area_msgs.configure(state="normal")
        self.area_msgs.insert(tk.END, f"  ★ {texto}\n", "sistema")
        self.area_msgs.configure(state="disabled")
        self.area_msgs.see(tk.END)

    def _mostrar_mensagem(self, nome, hora, texto, tag="outro", prefixo=None):
        exibir = prefixo if prefixo else nome
        self.area_msgs.configure(state="normal")
        self.area_msgs.insert(tk.END, f"  {exibir}", ("nome", tag))
        self.area_msgs.insert(tk.END, f"  {hora}\n", "sistema")
        self.area_msgs.insert(tk.END, f"  {texto}\n\n", tag)
        self.area_msgs.configure(state="disabled")
        self.area_msgs.see(tk.END)

    def _mostrar_privado(self, header, texto):
        self.area_msgs.configure(state="normal")
        self.area_msgs.insert(tk.END, f"  {header}: {texto}\n\n", "privado")
        self.area_msgs.configure(state="disabled")
        self.area_msgs.see(tk.END)

    # ──────────────────────────────────────
    # Desconexão
    # ──────────────────────────────────────
    def _desconectar(self):
        if self.conectado:
            self._enviar_raw("/sair")
            self.conectado = False
        try:
            self.socket.close()
        except:
            pass
        self.root.destroy()


# ──────────────────────────────────────────
# Ponto de entrada
# ──────────────────────────────────────────
if __name__ == '__main__':
    root = tk.Tk()
    app = ChatCliente(root)
    root.protocol("WM_DELETE_WINDOW", app._desconectar)
    root.mainloop()

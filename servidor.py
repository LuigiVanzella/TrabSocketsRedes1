"""
Servidor de Chat TCP
Trabalho de Redes de Computadores
"""

import socket
import threading
import datetime

HOST = '0.0.0.0'
PORT = 12345

clientes = {}       # socket -> apelido
lock = threading.Lock()


def log(mensagem):
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{hora}] {mensagem}")


def broadcast(mensagem, remetente_socket=None):
    """Envia mensagem para todos os clientes conectados, exceto o remetente."""
    with lock:
        desconectados = []
        for cliente_socket in clientes:
            if cliente_socket != remetente_socket:
                try:
                    cliente_socket.sendall(mensagem.encode('utf-8'))
                except:
                    desconectados.append(cliente_socket)
        for c in desconectados:
            remover_cliente(c)


def enviar_para(socket_destino, mensagem):
    """Envia mensagem para um cliente específico."""
    try:
        socket_destino.sendall(mensagem.encode('utf-8'))
    except:
        remover_cliente(socket_destino)


def remover_cliente(cliente_socket):
    """Remove cliente da lista (sem lock — já deve estar dentro de um lock)."""
    if cliente_socket in clientes:
        apelido = clientes.pop(cliente_socket)
        log(f"Cliente '{apelido}' removido da lista.")
        return apelido
    return None


def listar_usuarios():
    """Retorna string com todos os usuários online."""
    with lock:
        nomes = list(clientes.values())
    if not nomes:
        return "Nenhum usuário conectado."
    return "Usuários online: " + ", ".join(nomes)


def handle_cliente(cliente_socket, endereco):
    log(f"Nova conexão: {endereco}")

    # 1. Receber apelido
    try:
        cliente_socket.sendall("APELIDO".encode('utf-8'))
        apelido = cliente_socket.recv(1024).decode('utf-8').strip()
        if not apelido:
            apelido = f"User_{endereco[1]}"
    except:
        cliente_socket.close()
        return

    # 2. Verificar apelido duplicado
    with lock:
        nomes_atuais = list(clientes.values())
        if apelido in nomes_atuais:
            cliente_socket.sendall("ERRO:Apelido já em uso. Tente outro.".encode('utf-8'))
            cliente_socket.close()
            log(f"Apelido duplicado rejeitado: '{apelido}'")
            return
        clientes[cliente_socket] = apelido

    log(f"'{apelido}' entrou no chat ({endereco})")

    # 3. Boas-vindas
    enviar_para(cliente_socket, f"SISTEMA:Bem-vindo ao chat, {apelido}! Digite /ajuda para ver os comandos.")
    broadcast(f"SISTEMA:{apelido} entrou na sala.", remetente_socket=cliente_socket)

    # 4. Loop de mensagens
    while True:
        try:
            dados = cliente_socket.recv(2048)
            if not dados:
                break
            mensagem = dados.decode('utf-8').strip()

            # Comandos especiais
            if mensagem.startswith('/'):
                partes = mensagem.split(' ', 2)
                cmd = partes[0].lower()

                if cmd == '/sair':
                    break

                elif cmd == '/usuarios':
                    enviar_para(cliente_socket, f"SISTEMA:{listar_usuarios()}")

                elif cmd == '/privado' and len(partes) >= 3:
                    destinatario = partes[1]
                    texto_privado = partes[2]
                    with lock:
                        dest_socket = next((s for s, n in clientes.items() if n == destinatario), None)
                    if dest_socket:
                        enviar_para(dest_socket, f"PRIVADO:{apelido}:{texto_privado}")
                        enviar_para(cliente_socket, f"PRIVADO_ENVIADO:{destinatario}:{texto_privado}")
                    else:
                        enviar_para(cliente_socket, f"SISTEMA:Usuário '{destinatario}' não encontrado.")

                elif cmd == '/ajuda':
                    ajuda = (
                        "SISTEMA:Comandos disponíveis:\n"
                        "  /usuarios        → lista usuários online\n"
                        "  /privado <nome> <msg> → mensagem privada\n"
                        "  /ajuda           → mostra esta ajuda\n"
                        "  /sair            → desconecta do chat"
                    )
                    enviar_para(cliente_socket, ajuda)

                else:
                    enviar_para(cliente_socket, "SISTEMA:Comando desconhecido. Digite /ajuda.")

            else:
                # Mensagem pública
                hora = datetime.datetime.now().strftime("%H:%M")
                msg_formatada = f"MSG:{apelido}:{hora}:{mensagem}"
                log(f"[{apelido}]: {mensagem}")
                broadcast(msg_formatada, remetente_socket=cliente_socket)
                enviar_para(cliente_socket, f"MSG_PROPRIA:{apelido}:{hora}:{mensagem}")

        except ConnectionResetError:
            break
        except Exception as e:
            log(f"Erro com cliente '{apelido}': {e}")
            break

    # Desconexão
    with lock:
        remover_cliente(cliente_socket)
    try:
        cliente_socket.close()
    except:
        pass
    log(f"'{apelido}' saiu do chat.")
    broadcast(f"SISTEMA:{apelido} saiu da sala.")


def iniciar_servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor_socket.bind((HOST, PORT))
    servidor_socket.listen(50)
    log(f"Servidor iniciado em {HOST}:{PORT}")
    log("Aguardando conexões...")

    try:
        while True:
            cliente_socket, endereco = servidor_socket.accept()
            thread = threading.Thread(target=handle_cliente, args=(cliente_socket, endereco), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        log("Servidor encerrado pelo administrador.")
    finally:
        servidor_socket.close()


if __name__ == '__main__':
    iniciar_servidor()

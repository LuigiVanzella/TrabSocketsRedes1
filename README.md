# 💬 PyChat — Chat TCP em Python

Grupo:

Luigi Antonio Loddi Vanzella;

Lucas de Mesquita Barros;

Vinicius Augusto de Souza Sabino;

Gabriel Araújo Rodrigues;



Sistema de chat em tempo real desenvolvido com **sockets TCP** em Python puro.

## Arquitetura

```
cliente.py  ──────┐
cliente.py  ───── servidor.py (HOST:12345)
cliente.py  ──────┘
```

O servidor centraliza as mensagens: cada cliente conecta-se via TCP, e o servidor repassa as mensagens para todos os demais participantes.

## Requisitos

- Python 3.8 ou superior (tkinter já incluído na instalação padrão)

## Como executar

### 1. Iniciar o servidor

```bash
python servidor.py
```

O servidor fica escutando na porta **12345** de todas as interfaces (`0.0.0.0`).

### 2. Iniciar o cliente (quantas janelas quiser)

```bash
python cliente.py
```

Preencha:
- **Servidor (IP):** `127.0.0.1` (mesma máquina) ou o IP da máquina que roda o servidor
- **Porta:** `12345`
- **Apelido:** nome que aparecerá no chat

## Funcionalidades

| Recurso | Como usar |
|---|---|
| Mensagem pública | Digite e pressione Enter ou clique em **Enviar** |
| Listar usuários online | Botão **👥 Usuários** ou digite `/usuarios` |
| Mensagem privada | Botão **✉ Privado** ou `/privado <nome> <mensagem>` |
| Ajuda | Digite `/ajuda` |
| Sair | Botão **🔌 Sair** ou `/sair` |

## Protocolo (resumo)

```
Cliente → Servidor   : apelido (após receber "APELIDO")
Servidor → Cliente   : SISTEMA:<texto>
Servidor → Cliente   : MSG:<nome>:<hora>:<texto>
Servidor → Cliente   : MSG_PROPRIA:<nome>:<hora>:<texto>
Servidor → Cliente   : PRIVADO:<remetente>:<texto>
Servidor → Cliente   : PRIVADO_ENVIADO:<dest>:<texto>
```

## Vídeo de demonstração

> Link do YouTube: https://youtu.be/-Dp4BnYeB_o

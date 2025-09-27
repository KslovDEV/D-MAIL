
# D-Mail

**D-Mail** é um agendador de e-mails em terminal inspirado em *Steins;Gate*. Permite enviar e-mails imediatos ou programados, usando **keyring** para armazenar senhas de app de forma segura.

---

## Funcionalidades

* Configurar remetente (e-mail).
* Salvar e recuperar senha de app com **keyring**.
* Enviar e-mails imediatamente.
* Agendar envio diário de e-mails em horário fixo.
* Listar e cancelar agendamentos ativos.

---

## Requisitos

* Python 3.8 ou superior
* Bibliotecas Python: `schedule`, `keyring`

Instale as dependências com:


pip install schedule keyring


## Instalação

1. Clone o repositório:

git clone https://github.com/KslovDEV/D-MAIL.git
cd D-Mail

2. Execute o programa:

python d_mail.py


---

## Configuração

1. Configure seu **remetente** (e-mail) no menu `[1]`.
2. Salve a senha de app no **keyring** com `[2]` para não precisar digitá-la sempre.

> **Atenção:** Para Gmail, use **senha de app**, não a senha principal da conta.

---

## Uso

* **Enviar agora:** `[3]` e siga os prompts.
* **Agendar diário:** `[4]`, digite destinatário, assunto, mensagem e horário (`HH:MM`).
* **Ver agendamentos:** `[5]`
* **Cancelar agendamento:** `[6]`

---

## Segurança

* Senhas são armazenadas apenas no **keyring do sistema**, não no código.
* Recomendado usar senhas de app ou contas dedicadas.

---

## Exemplo de fluxo

1. Configurar remetente: `meuemail@gmail.com`.
2. Salvar senha de app.
3. Enviar e-mail imediato para um amigo.
4. Agendar envio diário de lembrete às 08:00.

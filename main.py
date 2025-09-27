#!/usr/bin/env python3
import threading, time, schedule, smtplib, keyring, uuid, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

APP_SERVICE_NAME = "D-Mail"
scheduled_jobs = {}

def send_email_smtp(sender, password, to, subject, body, smtp_server="smtp.gmail.com", smtp_port=587):
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to, msg.as_string())
        return True, None
    except Exception as e:
        return False, str(e)

def schedule_loop(stop_event):
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)

def clear_screen():
    if sys.platform.startswith("win"):
        _ = __import__("os").system("cls")
    else:
        _ = __import__("os").system("clear")

def header():
    print(r"""
   ____        __  __       _ _      
  |  _ \      |  \/  | __ _(_) | __ 
  | | | |     | |\/| |/ _` | | |
  | |_| | (_) | |  | | (_| | | |
  |____/      |_|  |_|\__,_|_|_|
        -- D-Mail --
 Simple terminal email scheduler
 Legitimate use only. Use app passwords.
""")

def menu():
    print("[1] Configurar remetente (email)")
    print("[2] Salvar/usar senha (keyring)")
    print("[3] Enviar agora")
    print("[4] Agendar envio diário (HH:MM)")
    print("[5] Ver agendamentos")
    print("[6] Cancelar agendamento")
    print("[7] Sair")

def input_nonempty(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v

def list_agendamentos():
    if not scheduled_jobs:
        print("Nenhum agendamento.")
        return
    for jid, info in scheduled_jobs.items():
        print(f"ID: {jid} | {info['from']} -> {info['to']} | {info['time']} | assunto: {info['subject']}")

def cancel_agendamento_by_id(jid):
    if jid in scheduled_jobs:
        try:
            schedule.cancel_job(scheduled_jobs[jid]["job"])
        except Exception:
            pass
        del scheduled_jobs[jid]
        print("Agendamento cancelado.")
    else:
        print("ID não encontrado.")

def main():
    stop_event = threading.Event()
    t = threading.Thread(target=schedule_loop, args=(stop_event,), daemon=True)
    t.start()

    remetente = ""
    senha_cached = None
    log = []

    while True:
        clear_screen()
        header()
        if remetente:
            print(f"Remetente atual: {remetente}")
        else:
            print("Remetente não configurado.")
        print()
        menu()
        escolha = input("\nEscolha uma opção: ").strip()
        if escolha == "1":
            remetente = input_nonempty("Digite seu email (remetente): ")
            use_saved = input("Tentar recuperar senha salva para esse email? (s/N): ").strip().lower()
            if use_saved == "s":
                senha_cached = keyring.get_password(APP_SERVICE_NAME, remetente)
                if senha_cached:
                    print("Senha recuperada do cofre do sistema.")
                else:
                    print("Nenhuma senha salva encontrada.")
            input("Enter para continuar...")
        elif escolha == "2":
            if not remetente:
                print("Configure o remetente primeiro.")
                input("Enter para continuar...")
                continue
            senha = input("Digite a senha de app (será salva no keyring): ").strip()
            if not senha:
                print("Senha vazia. Cancelado.")
            else:
                keyring.set_password(APP_SERVICE_NAME, remetente, senha)
                senha_cached = senha
                print("Senha salva no cofre do sistema.")
            input("Enter para continuar...")
        elif escolha == "3":
            if not remetente:
                print("Configure o remetente primeiro.")
                input("Enter para continuar...")
                continue
            if not senha_cached:
                senha_cached = input("Senha (ou pressione Enter para tentar recuperar do keyring): ").strip()
                if not senha_cached:
                    senha_cached = keyring.get_password(APP_SERVICE_NAME, remetente)
            if not senha_cached:
                print("Senha não fornecida.")
                input("Enter para continuar...")
                continue
            to = input_nonempty("Destinatário: ")
            subject = input("Assunto: ").strip()
            print("Digite a mensagem. Termine com uma linha contendo somente '.' (ponto).")
            lines = []
            while True:
                line = input()
                if line == ".":
                    break
                lines.append(line)
            body = "\n".join(lines)
            ok, err = send_email_smtp(remetente, senha_cached, to, subject, body)
            if ok:
                print("Email enviado com sucesso.")
                log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} SENT -> {to}")
            else:
                print("Erro ao enviar:", err)
                log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ERROR -> {err}")
            input("Enter para continuar...")
        elif escolha == "4":
            if not remetente:
                print("Configure o remetente primeiro.")
                input("Enter para continuar...")
                continue
            if not senha_cached:
                senha_cached = input("Senha (ou Enter para tentar recuperar do keyring): ").strip()
                if not senha_cached:
                    senha_cached = keyring.get_password(APP_SERVICE_NAME, remetente)
            if not senha_cached:
                print("Senha não fornecida.")
                input("Enter para continuar...")
                continue
            to = input_nonempty("Destinatário: ")
            subject = input("Assunto: ").strip()
            print("Digite a mensagem. Termine com uma linha contendo somente '.' (ponto).")
            lines = []
            while True:
                line = input()
                if line == ".":
                    break
                lines.append(line)
            body = "\n".join(lines)
            horario = input_nonempty("Horário (HH:MM) — enviará todo dia: ")
            job_id = str(uuid.uuid4())[:8]
            def job_closure(sender=remetente, pw=senha_cached, toaddr=to, subj=subject, bod=body, jid=job_id, h=horario):
                ok, err = send_email_smtp(sender, pw, toaddr, subj, bod)
                if ok:
                    msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} SCHEDULED SENT -> {toaddr} at {h}"
                    print(msg)
                    log.append(msg)
                else:
                    msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} SCHEDULED ERROR -> {err}"
                    print(msg)
                    log.append(msg)
            try:
                job = schedule.every().day.at(horario).do(job_closure)
                scheduled_jobs[job_id] = {"job": job, "from": remetente, "to": to, "time": horario, "subject": subject}
                print(f"Agendamento criado. ID: {job_id}")
            except Exception as e:
                print("Erro ao agendar:", e)
            input("Enter para continuar...")
        elif escolha == "5":
            list_agendamentos()
            input("Enter para continuar...")
        elif escolha == "6":
            list_agendamentos()
            jid = input("Digite o ID do agendamento para cancelar: ").strip()
            if jid:
                cancel_agendamento_by_id(jid)
            input("Enter para continuar...")
        elif escolha == "7":
            print("Encerrando...")
            stop_event.set()
            break
        else:
            print("Opção inválida.")
            input("Enter para continuar...")

if __name__ == "__main__":
    main()
import smtplib
from tkinter import Tk, filedialog, messagebox, Label, Button, StringVar, Entry, Frame
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import mimetypes
import threading
from time import sleep


def run_email_app():
    class EmailApp:
        def __init__(self, root):
            self.root = root
            self.root.title("Envio de E-mail")
            self.root.geometry("500x400")

            # Variáveis para os campos
            self.smtp_username = StringVar()
            self.senha = StringVar()
            self.destinatario_email = StringVar()
            self.assunto_email = StringVar()
            self.corpo_email = StringVar()
            self.anexo_path = StringVar()

            self.cancelado = False
            self.is_sending = False  # Flag para controlar envio simultâneo

            # Criar a interface
            self.create_interface()

        def create_interface(self):
            """Cria os elementos da interface gráfica."""
            Label(self.root, text="Envio de E-mail", font=("Arial", 16, "bold")).pack(pady=10)

            frame = Frame(self.root)
            frame.pack(pady=10, padx=20, fill="x")

            Label(frame, text="Seu E-mail:").grid(row=0, column=0, sticky="w")
            Entry(frame, textvariable=self.smtp_username).grid(row=0, column=1, sticky="ew")

            Label(frame, text="Senha:").grid(row=1, column=0, sticky="w")
            Entry(frame, textvariable=self.senha, show="*").grid(row=1, column=1, sticky="ew")

            Label(frame, text="E-mail do Destinatário:").grid(row=2, column=0, sticky="w")
            Entry(frame, textvariable=self.destinatario_email).grid(row=2, column=1, sticky="ew")

            Label(frame, text="Assunto:").grid(row=3, column=0, sticky="w")
            Entry(frame, textvariable=self.assunto_email).grid(row=3, column=1, sticky="ew")

            Label(frame, text="Corpo do E-mail:").grid(row=4, column=0, sticky="nw")
            Entry(frame, textvariable=self.corpo_email).grid(row=4, column=1, sticky="ew")

            Label(frame, text="Anexo:").grid(row=5, column=0, sticky="w")
            Entry(frame, textvariable=self.anexo_path).grid(row=5, column=1, sticky="ew")
            Button(frame, text="Selecionar", command=self.selecionar_anexo).grid(row=5, column=2)

            frame.columnconfigure(1, weight=1)

            self.status_label = Label(self.root, text="Pronto para enviar.", font=("Arial", 12), fg="black")
            self.status_label.pack(pady=20)

            self.enviar_button = Button(self.root, text="Enviar E-mail", command=self.iniciar_envio)
            self.enviar_button.pack(pady=5)
            self.cancelar_button = Button(self.root, text="Cancelar Envio", command=self.cancelar_envio, state="disabled")
            self.cancelar_button.pack(pady=5)

        def selecionar_anexo(self):
            """Abre o seletor de arquivos para anexos."""
            filepath = filedialog.askopenfilename(title="Selecione o arquivo")
            if filepath:
                self.anexo_path.set(filepath)

        def reset_campos(self):
            """Reseta todos os campos após o envio."""
            self.smtp_username.set("")
            self.senha.set("")
            self.destinatario_email.set("")
            self.assunto_email.set("")
            self.corpo_email.set("")
            self.anexo_path.set("")
            self.status_label.config(text="Pronto para enviar.", fg="black")

        def validar_campos(self):
            """Valida se os campos obrigatórios estão preenchidos."""
            if not self.smtp_username.get():
                messagebox.showerror("Erro", "O campo 'Seu E-mail' é obrigatório.")
                return False
            if not self.senha.get():
                messagebox.showerror("Erro", "O campo 'Senha' é obrigatório.")
                return False
            if not self.destinatario_email.get():
                messagebox.showerror("Erro", "O campo 'E-mail do Destinatário' é obrigatório.")
                return False
            return True

        def enviar_email(self):
            """Função para enviar o e-mail."""
            try:
                # Configurações
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587

                # Montar a mensagem
                msg = MIMEMultipart()
                msg['From'] = self.smtp_username.get()
                msg['To'] = self.destinatario_email.get()
                msg['Subject'] = self.assunto_email.get()
                msg.attach(MIMEText(self.corpo_email.get(), 'plain'))

                # Adicionar anexo
                if self.anexo_path.get():
                    basename = os.path.basename(self.anexo_path.get())
                    mime_type, _ = mimetypes.guess_type(self.anexo_path.get())
                    mime_type = mime_type or 'application/octet-stream'
                    main_type, sub_type = mime_type.split('/')
                    with open(self.anexo_path.get(), 'rb') as attachment:
                        part = MIMEBase(main_type, sub_type)
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{basename}"')
                        msg.attach(part)

                # Enviar e-mail
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username.get(), self.senha.get())
                    server.sendmail(self.smtp_username.get(), self.destinatario_email.get(), msg.as_string())

                self.status_label.config(text="E-mail enviado com sucesso!", fg="green")
                sleep(5)
                self.reset_campos()  # Limpa os campos após o envio
            except Exception as e:
                self.status_label.config(text=f"Erro: {str(e)}", fg="red")
            finally:
                self.is_sending = False
                self.enviar_button.config(state="normal")
                self.cancelar_button.config(state="disabled")

        def iniciar_envio(self):
            """Inicia o envio em uma nova thread."""
            if not self.validar_campos():
                return

            if self.is_sending:
                messagebox.showinfo("Aviso", "Já existe um envio em andamento.")
                return

            self.is_sending = True
            self.cancelado = False
            self.status_label.config(text="Iniciando envio...", fg="blue")
            self.enviar_button.config(state="disabled")
            self.cancelar_button.config(state="normal")

            threading.Thread(target=self.enviar_email).start()

        def cancelar_envio(self):
            """Cancela o envio."""
            self.cancelado = True
            self.status_label.config(text="Envio cancelado pelo usuário.", fg="red")
            self.enviar_button.config(state="normal")
            self.cancelar_button.config(state="disabled")

    email_root = Tk()
    EmailApp(email_root)
    email_root.mainloop()

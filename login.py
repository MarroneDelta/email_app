import tkinter as tk
from tkinter import messagebox
from supabase import create_client, Client
from app import run_email_app  # Importa a função correta do app.py


# Configurações do Supabase
SUPABASE_URL = "https://exemplo.supabase.co"  # Substitua pela URL do seu projeto
SUPABASE_KEY = "exemplo85656wd5665QR44544"  # Substitua pela sua chave "anon"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Função para autenticar o usuário
def login():
    email = email_entry.get()
    password = password_entry.get()
    
    if not email or not password:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return
    
    try:
        # Realiza o login no Supabase
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if "error" in response and response["error"]:
            messagebox.showerror("Erro", "Credenciais inválidas!")
        else:
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            root.destroy()  # Fecha a janela de login
            # Chama a função que inicia o app de e-mail
            run_email_app()  # Função definida no app.py
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Interface gráfica com tkinter
root = tk.Tk()
root.title("Login - Supabase")
root.geometry("300x200")
root.resizable(False, False)

# Elementos da interface
tk.Label(root, text="Email").pack(pady=5)
email_entry = tk.Entry(root, width=30)
email_entry.pack()

tk.Label(root, text="Senha").pack(pady=5)
password_entry = tk.Entry(root, width=30, show="*")
password_entry.pack()

login_button = tk.Button(root, text="Login", command=login)
login_button.pack(pady=20)

# Executar a janela
root.mainloop()

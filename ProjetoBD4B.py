import tkinter as tk
from tkinter import messagebox, simpledialog
from pymongo import MongoClient
from cryptography.fernet import Fernet
import bcrypt
import random

# Configuração do MongoDB
client = MongoClient("mongodb+srv://joaovkb:JvKb2808@projeto4b.zlq2l.mongodb.net/")
db = client["med_records"]
usuarios_collection = db["usuarios"]
pacientes_collection = db["pacientes"]
registros_collection = db["registros"]


# Geração de chave de criptografia
def gerar_chave():
    return Fernet.generate_key()


# Funções para Usuários (Médicos)
def registrar_usuario(nome, crm, email, senha, telefone):
    hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    secret = str(random.randint(100000, 999999))  # Código 2FA simples
    usuarios_collection.insert_one(
        {"nome": nome, "crm": crm, "email": email, "senha": hashed, "telefone": telefone, "2fa_secret": secret})
    return secret  # Retorna o código 2FA para informar ao usuário


def autenticar_usuario(nome, senha, codigo_2fa):
    usuario = usuarios_collection.find_one({"nome": nome})
    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha']):
        return usuario['2fa_secret'] == codigo_2fa
    return False


# Funções para Pacientes
def registrar_paciente(nome, data_nascimento, sexo, cpf, telefone):
    pacientes_collection.insert_one(
        {"nome": nome, "data_nascimento": data_nascimento, "sexo": sexo, "cpf": cpf, "telefone": telefone})

def listar_pacientes():
    return list(
        pacientes_collection.find({}, {"_id": 0, "nome": 1, "data_nascimento": 1, "sexo": 1, "cpf": 1, "telefone": 1}))

# Funções para Registros Médicos
def criar_registro(nome_paciente, nome_medico, sintomas, diagnostico, tratamento, historico):
    key = gerar_chave()
    cipher = Fernet(key)
    historico_encriptado = cipher.encrypt(historico.encode('utf-8'))
    registros_collection.insert_one(
        {"nome_paciente": nome_paciente, "nome_medico": nome_medico, "sintomas": sintomas, "diagnostico": diagnostico,
         "tratamento": tratamento, "historico": historico_encriptado})


def listar_registros():
    return list(registros_collection.find({}, {"_id": 0, "nome_paciente": 1, "sintomas": 1, "diagnostico": 1,
                                               "tratamento": 1, "historico": 1}))


# Interface gráfica
class SistemaGerenciamentoRegistros:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Gerenciamento de Registros Médicos")
        self.master.geometry("600x600")
        self.master.config(bg="#e8f5e9")
        self.current_frame = None
        self.usuario_logado = None  # Armazena o usuário logado
        self.show_initial_form()

    def clear_window(self):
        if self.current_frame:
            self.current_frame.pack_forget()

    def show_initial_form(self):
        self.clear_window()
        frame = tk.Frame(self.master, bg="#e8f5e9")
        frame.pack(pady=20)
        tk.Label(frame, text="Sistema de Gerenciamento", bg="#e8f5e9", font=("Arial", 24)).pack(pady=10)
        tk.Button(frame, text="Registrar Médico", command=self.show_user_registration_form, bg="#4CAF50", fg="white",
                  width=20).pack(pady=10)
        tk.Button(frame, text="Acessar Médico", command=self.show_user_access_form, bg="#2196F3", fg="white",
                  width=20).pack(pady=10)
        self.current_frame = frame

    def show_user_registration_form(self):
        self.clear_window()
        frame = tk.Frame(self.master, bg="#e8f5e9")
        frame.pack(pady=20)
        tk.Label(frame, text="Registro de Médico", bg="#e8f5e9", font=("Arial", 24)).pack(pady=10)
        tk.Label(frame, text="Nome:", bg="#e8f5e9").pack(pady=5)
        self.nome_entry = tk.Entry(frame)
        self.nome_entry.pack(pady=5)
        tk.Label(frame, text="CRM:", bg="#e8f5e9").pack(pady=5)
        self.crm_entry = tk.Entry(frame)
        self.crm_entry.pack(pady=5)
        tk.Label(frame, text="Email:", bg="#e8f5e9").pack(pady=5)
        self.email_entry = tk.Entry(frame)
        self.email_entry.pack(pady=5)
        tk.Label(frame, text="Senha:", bg="#e8f5e9").pack(pady=5)
        self.senha_entry = tk.Entry(frame, show="*")
        self.senha_entry.pack(pady=5)
        tk.Label(frame, text="Telefone:", bg="#e8f5e9").pack(pady=5)
        self.telefone_entry = tk.Entry(frame)
        self.telefone_entry.pack(pady=5)
        tk.Button(frame, text="Registrar", command=self.register_user, bg="#4CAF50", fg="white", width=20).pack(pady=10)
        self.current_frame = frame

    def register_user(self):
        nome = self.nome_entry.get()
        crm = self.crm_entry.get()
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        telefone = self.telefone_entry.get()
        if nome and crm and email and senha and telefone:
            codigo_2fa = registrar_usuario(nome, crm, email, senha, telefone)
            messagebox.showinfo("Registro", f"Médico registrado com sucesso! Seu código 2FA é: {codigo_2fa}")
            self.show_initial_form()
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")

    def show_user_access_form(self):
        self.clear_window()
        frame = tk.Frame(self.master, bg="#e8f5e9")
        frame.pack(pady=20)
        tk.Label(frame, text="Acesso de Médico", bg="#e8f5e9", font=("Arial", 24)).pack(pady=10)
        tk.Label(frame, text="Nome:", bg="#e8f5e9").pack(pady=5)
        self.nome_access_entry = tk.Entry(frame)
        self.nome_access_entry.pack(pady=5)
        tk.Label(frame, text="Senha:", bg="#e8f5e9").pack(pady=5)
        self.senha_access_entry = tk.Entry(frame, show="*")
        self.senha_access_entry.pack(pady=5)
        tk.Button(frame, text="Acessar", command=self.access_user, bg="#2196F3", fg="white", width=20).pack(pady=10)
        self.current_frame = frame

    def access_user(self):
        nome = self.nome_access_entry.get()
        senha = self.senha_access_entry.get()
        codigo_2fa = simpledialog.askstring("Código 2FA", "Digite seu código 2FA:")  # Solicita o código 2FA
        if autenticar_usuario(nome, senha, codigo_2fa):
            messagebox.showinfo("Acesso", "Acesso concedido!")
            self.usuario_logado = nome  # Armazena o usuário logado
            self.show_patient_management_form()
        else:
            messagebox.showwarning("Aviso", "Usuário, senha, ou código de autenticação incorreto.")

    def show_patient_management_form(self):
        self.clear_window()
        frame = tk.Frame(self.master, bg="#e8f5e9")
        frame.pack(pady=20)
        tk.Label(frame, text="Gerenciamento de Pacientes", bg="#e8f5e9", font=("Arial", 24)).pack(pady=10)

        tk.Label(frame, text="Nome:", bg="#e8f5e9").pack(pady=5)
        self.paciente_nome_entry = tk.Entry(frame)
        self.paciente_nome_entry.pack(pady=5)

        tk.Label(frame, text="Data de Nascimento:", bg="#e8f5e9").pack(pady=5)
        self.paciente_dob_entry = tk.Entry(frame)
        self.paciente_dob_entry.pack(pady=5)

        tk.Label(frame, text="Sexo:", bg="#e8f5e9").pack(pady=5)
        self.paciente_sexo_entry = tk.Entry(frame)
        self.paciente_sexo_entry.pack(pady=5)

        tk.Label(frame, text="CPF:", bg="#e8f5e9").pack(pady=5)
        self.paciente_cpf_entry = tk.Entry(frame)
        self.paciente_cpf_entry.pack(pady=5)

        tk.Label(frame, text="Telefone:", bg="#e8f5e9").pack(pady=5)
        self.paciente_telefone_entry = tk.Entry(frame)
        self.paciente_telefone_entry.pack(pady=5)

        tk.Button(frame, text="Registrar Paciente", command=self.register_patient, bg="#4CAF50", fg="white",
                  width=20).pack(pady=10)
        tk.Button(frame, text="Listar Pacientes", command=self.list_patients, bg="#2196F3", fg="white", width=20).pack(
            pady=5)

        # Botão para acessar a tela de Registros Médicos
        tk.Button(frame, text="Gerenciar Registros Médicos", command=self.show_medical_records_management_form,
                  bg="#2196F3", fg="white", width=20).pack(pady=10)

        self.current_frame = frame

    def register_patient(self):
        nome = self.paciente_nome_entry.get()
        data_nascimento = self.paciente_dob_entry.get()
        sexo = self.paciente_sexo_entry.get()
        cpf = self.paciente_cpf_entry.get()
        telefone = self.paciente_telefone_entry.get()
        if nome and data_nascimento and sexo and cpf and telefone:
            registrar_paciente(nome, data_nascimento, sexo, cpf, telefone)
            messagebox.showinfo("Registro", "Paciente registrado com sucesso!")
            self.paciente_nome_entry.delete(0, tk.END)
            self.paciente_dob_entry.delete(0, tk.END)
            self.paciente_sexo_entry.delete(0, tk.END)
            self.paciente_cpf_entry.delete(0, tk.END)
            self.paciente_telefone_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")

    def list_patients(self):
        pacientes = listar_pacientes()
        if pacientes:
            pacientes_str = "\n".join([
                                          f"Nome: {p['nome']}, Data de Nascimento: {p['data_nascimento']}, Sexo: {p['sexo']}, CPF: {p['cpf']}, Telefone: {p['telefone']}"
                                          for p in pacientes])
            messagebox.showinfo("Lista de Pacientes", pacientes_str)
        else:
            messagebox.showinfo("Lista de Pacientes", "Nenhum paciente registrado.")

    def show_medical_records_management_form(self):
        self.clear_window()
        frame = tk.Frame(self.master, bg="#e8f5e9")
        frame.pack(pady=20)
        tk.Label(frame, text="Gerenciamento de Registros Médicos", bg="#e8f5e9", font=("Arial", 24)).pack(pady=10)

        tk.Label(frame, text="Nome do Paciente:", bg="#e8f5e9").pack(pady=5)
        self.nome_paciente_entry = tk.Entry(frame)
        self.nome_paciente_entry.pack(pady=5)

        tk.Label(frame, text="Nome do Médico:", bg="#e8f5e9").pack(pady=5)
        self.nome_medico_entry = tk.Entry(frame)
        self.nome_medico_entry.pack(pady=5)

        tk.Label(frame, text="Sintomas:", bg="#e8f5e9").pack(pady=5)
        self.sintomas_entry = tk.Entry(frame)
        self.sintomas_entry.pack(pady=5)

        tk.Label(frame, text="Diagnóstico:", bg="#e8f5e9").pack(pady=5)
        self.diagnostico_entry = tk.Entry(frame)
        self.diagnostico_entry.pack(pady=5)

        tk.Label(frame, text="Tratamento:", bg="#e8f5e9").pack(pady=5)
        self.tratamento_entry = tk.Entry(frame)
        self.tratamento_entry.pack(pady=5)

        tk.Label(frame, text="Histórico Médico:", bg="#e8f5e9").pack(pady=5)
        self.historico_entry = tk.Entry(frame)
        self.historico_entry.pack(pady=5)

        tk.Button(frame, text="Criar Registro", command=self.create_medical_record, bg="#4CAF50", fg="white",
                  width=20).pack(pady=10)
        tk.Button(frame, text="Listar Registros", command=self.list_medical_records, bg="#2196F3", fg="white",
                  width=20).pack(pady=5)

        # Botão para voltar para o gerenciamento de pacientes
        tk.Button(frame, text="Gerenciamento de Pacientes", command=self.show_patient_management_form,
                  bg="#2196F3", fg="white", width=20).pack(pady=10)

        self.current_frame = frame

    def create_medical_record(self):
        nome_paciente = self.nome_paciente_entry.get()
        nome_medico = self.nome_medico_entry.get()
        sintomas = self.sintomas_entry.get()
        diagnostico = self.diagnostico_entry.get()
        tratamento = self.tratamento_entry.get()
        historico = self.historico_entry.get()
        if nome_paciente and nome_medico and sintomas and diagnostico and tratamento and historico:
            criar_registro(nome_paciente, nome_medico, sintomas, diagnostico, tratamento, historico)
            messagebox.showinfo("Registro", "Registro médico criado com sucesso!")
            self.nome_paciente_entry.delete(0, tk.END)
            self.nome_medico_entry.delete(0, tk.END)
            self.sintomas_entry.delete(0, tk.END)
            self.diagnostico_entry.delete(0, tk.END)
            self.tratamento_entry.delete(0, tk.END)
            self.historico_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")

    def list_medical_records(self):
        registros = listar_registros()
        if registros:
            registros_str = "\n".join([
                                          f"Nome Paciente: {r['nome_paciente']}, Sintomas: {r['sintomas']}, Diagnóstico: {r['diagnostico']}, Tratamento: {r['tratamento']}"
                                          for r in registros])
            messagebox.showinfo("Lista de Registros Médicos", registros_str)
        else:
            messagebox.showinfo("Lista de Registros Médicos", "Nenhum registro médico encontrado.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGerenciamentoRegistros(root)
    root.mainloop()

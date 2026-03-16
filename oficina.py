import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

# ==================== BANCO DE DADOS ====================
conn = sqlite3.connect('oficina.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS clientes 
             (id INTEGER PRIMARY KEY, nome TEXT, telefone TEXT, cpf TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS veiculos 
             (id INTEGER PRIMARY KEY, cliente_id INTEGER, placa TEXT, modelo TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS os 
             (id INTEGER PRIMARY KEY, data TEXT, cliente_id INTEGER, veiculo_id INTEGER, total REAL, status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS os_itens 
             (id INTEGER PRIMARY KEY, os_id INTEGER, descricao TEXT, quantidade REAL, preco REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS despesas 
             (id INTEGER PRIMARY KEY, data TEXT, descricao TEXT, valor REAL)''')
conn.commit()

# ==================== JANELA PRINCIPAL ====================
class OficinaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚗 Oficina Mecânica - Sistema Simples")
        self.geometry("900x700")
        self.configure(bg="#f0f0f0")

        tk.Label(self, text="Sistema de Oficina Mecânica", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=20)

        # Botões grandes e fáceis
        btn_style = {"font": ("Arial", 14), "width": 30, "height": 2, "bg": "#4CAF50", "fg": "white"}

        tk.Button(self, text="👤 Cadastrar Cliente", **btn_style, command=self.cadastrar_cliente).pack(pady=10)
        tk.Button(self, text="🚘 Cadastrar Veículo", **btn_style, command=self.cadastrar_veiculo).pack(pady=10)
        tk.Button(self, text="📋 Nova Ordem de Serviço", **btn_style, command=self.nova_os).pack(pady=10)
        tk.Button(self, text="📋 Listar Ordens de Serviço", **btn_style, command=self.listar_os).pack(pady=10)
        tk.Button(self, text="💰 Calcular Gastos e Lucro", **btn_style, command=self.relatorio_gastos).pack(pady=10)
        tk.Button(self, text="📄 Gerar NF-e (Simples)", **btn_style, command=self.gerar_nfe).pack(pady=10)
        tk.Button(self, text="❌ Sair", font=("Arial", 14), width=30, height=2, bg="#f44336", fg="white", command=self.quit).pack(pady=20)

    # ==================== FUNÇÕES ====================
    def cadastrar_cliente(self):
        janela = tk.Toplevel(self)
        janela.title("Cadastrar Cliente")
        janela.geometry("400x300")

        tk.Label(janela, text="Nome:").pack(pady=5)
        nome = tk.Entry(janela, width=40)
        nome.pack()

        tk.Label(janela, text="Telefone:").pack(pady=5)
        tel = tk.Entry(janela, width=40)
        tel.pack()

        tk.Label(janela, text="CPF:").pack(pady=5)
        cpf = tk.Entry(janela, width=40)
        cpf.pack()

        def salvar():
            c.execute("INSERT INTO clientes (nome, telefone, cpf) VALUES (?,?,?)", 
                      (nome.get(), tel.get(), cpf.get()))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            janela.destroy()

        tk.Button(janela, text="Salvar Cliente", bg="#4CAF50", fg="white", command=salvar).pack(pady=20)

    def cadastrar_veiculo(self):
        janela = tk.Toplevel(self)
        janela.title("Cadastrar Veículo")
        janela.geometry("400x350")

        # Carrega clientes
        c.execute("SELECT id, nome FROM clientes")
        clientes = c.fetchall()
        lista_clientes = [f"{id} - {nome}" for id, nome in clientes]

        tk.Label(janela, text="Cliente:").pack(pady=5)
        combo_cliente = ttk.Combobox(janela, values=lista_clientes, width=37)
        combo_cliente.pack()

        tk.Label(janela, text="Placa:").pack(pady=5)
        placa = tk.Entry(janela, width=40)
        placa.pack()

        tk.Label(janela, text="Modelo:").pack(pady=5)
        modelo = tk.Entry(janela, width=40)
        modelo.pack()

        def salvar():
            if not combo_cliente.get():
                messagebox.showwarning("Atenção", "Escolha um cliente!")
                return
            cliente_id = combo_cliente.get().split(" - ")[0]
            c.execute("INSERT INTO veiculos (cliente_id, placa, modelo) VALUES (?,?,?)",
                      (cliente_id, placa.get(), modelo.get()))
            conn.commit()
            messagebox.showinfo("Sucesso", "Veículo cadastrado!")
            janela.destroy()

        tk.Button(janela, text="Salvar Veículo", bg="#4CAF50", fg="white", command=salvar).pack(pady=20)

    def nova_os(self):
        janela = tk.Toplevel(self)
        janela.title("Nova Ordem de Serviço")
        janela.geometry("700x600")

        # Cliente e Veículo
        c.execute("SELECT id, nome FROM clientes")
        clientes = [f"{id} - {nome}" for id, nome in c.fetchall()]
        tk.Label(janela, text="Cliente:").grid(row=0, column=0, pady=5)
        combo_cli = ttk.Combobox(janela, values=clientes, width=40)
        combo_cli.grid(row=0, column=1)

        c.execute("SELECT id, placa FROM veiculos")
        veiculos = [f"{id} - {placa}" for id, placa in c.fetchall()]
        tk.Label(janela, text="Veículo:").grid(row=1, column=0, pady=5)
        combo_vei = ttk.Combobox(janela, values=veiculos, width=40)
        combo_vei.grid(row=1, column=1)

        # Itens da OS
        tk.Label(janela, text="Descrição do serviço/peça:").grid(row=2, column=0, pady=10)
        desc = tk.Entry(janela, width=50)
        desc.grid(row=2, column=1)

        tk.Label(janela, text="Quantidade:").grid(row=3, column=0)
        qtd = tk.Entry(janela, width=20)
        qtd.grid(row=3, column=1)

        tk.Label(janela, text="Preço unitário:").grid(row=4, column=0)
        preco = tk.Entry(janela, width=20)
        preco.grid(row=4, column=1)

        itens = []
        tree = ttk.Treeview(janela, columns=("desc", "qtd", "preco", "sub"), show="headings", height=8)
        tree.heading("desc", text="Descrição")
        tree.heading("qtd", text="Qtd")
        tree.heading("preco", text="Preço")
        tree.heading("sub", text="Subtotal")
        tree.grid(row=5, column=0, columnspan=2, pady=10)

        def adicionar_item():
            if not desc.get() or not qtd.get() or not preco.get():
                return
            subtotal = float(qtd.get()) * float(preco.get())
            tree.insert("", "end", values=(desc.get(), qtd.get(), preco.get(), f"R$ {subtotal:.2f}"))
            itens.append((desc.get(), float(qtd.get()), float(preco.get()), subtotal))
            desc.delete(0, tk.END)
            qtd.delete(0, tk.END)
            preco.delete(0, tk.END)
            atualizar_total()

        tk.Button(janela, text="➕ Adicionar Item", bg="#2196F3", fg="white", command=adicionar_item).grid(row=6, column=1)

        total_label = tk.Label(janela, text="Total: R$ 0.00", font=("Arial", 16, "bold"))
        total_label.grid(row=7, column=0, columnspan=2)

        def atualizar_total():
            soma = sum(i[3] for i in itens)
            total_label.config(text=f"Total: R$ {soma:.2f}")

        def salvar_os():
            if not combo_cli.get() or not combo_vei.get() or not itens:
                messagebox.showwarning("Atenção", "Preencha tudo!")
                return
            cliente_id = combo_cli.get().split(" - ")[0]
            veiculo_id = combo_vei.get().split(" - ")[0]
            total = sum(i[3] for i in itens)

            c.execute("INSERT INTO os (data, cliente_id, veiculo_id, total, status) VALUES (?,?,?,?,?)",
                      (datetime.now().strftime("%d/%m/%Y"), cliente_id, veiculo_id, total, "Aberta"))
            os_id = c.lastrowid

            for item in itens:
                c.execute("INSERT INTO os_itens (os_id, descricao, quantidade, preco) VALUES (?,?,?,?)",
                          (os_id, item[0], item[1], item[2]))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Ordem de Serviço #{os_id} salva!")
            janela.destroy()

        tk.Button(janela, text="💾 Salvar Ordem de Serviço", bg="#4CAF50", fg="white", font=("Arial", 14), command=salvar_os).grid(row=8, column=0, columnspan=2, pady=20)

    def listar_os(self):
        janela = tk.Toplevel(self)
        janela.title("Ordens de Serviço")
        janela.geometry("900x500")

        tree = ttk.Treeview(janela, columns=("id", "data", "cliente", "total", "status"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col.capitalize())
        tree.pack(fill="both", expand=True)

        c.execute("""SELECT os.id, os.data, clientes.nome, os.total, os.status 
                     FROM os JOIN clientes ON os.cliente_id = clientes.id""")
        for row in c.fetchall():
            tree.insert("", "end", values=row)

    def relatorio_gastos(self):
        janela = tk.Toplevel(self)
        janela.title("Relatório de Gastos e Lucro")
        janela.geometry("600x400")

        # Total das OS
        c.execute("SELECT SUM(total) FROM os")
        total_os = c.fetchone()[0] or 0

        # Total despesas
        c.execute("SELECT SUM(valor) FROM despesas")
        total_des = c.fetchone()[0] or 0

        lucro = total_os - total_des

        tk.Label(janela, text=f"Total recebido (OS): R$ {total_os:.2f}", font=("Arial", 14)).pack(pady=10)
        tk.Label(janela, text=f"Total de despesas: R$ {total_des:.2f}", font=("Arial", 14)).pack(pady=10)
        tk.Label(janela, text=f"💰 LUCRO: R$ {lucro:.2f}", font=("Arial", 18, "bold"), fg="green").pack(pady=20)

        # Adicionar despesa rápida
        tk.Label(janela, text="Nova despesa:").pack()
        desc = tk.Entry(janela, width=50)
        desc.pack()
        valor = tk.Entry(janela, width=20)
        valor.pack()

        def add_despesa():
            c.execute("INSERT INTO despesas (data, descricao, valor) VALUES (?,?,?)",
                      (datetime.now().strftime("%d/%m/%Y"), desc.get(), float(valor.get())))
            conn.commit()
            messagebox.showinfo("Ok", "Despesa registrada!")
            janela.destroy()
            self.relatorio_gastos()  # atualiza

        tk.Button(janela, text="Registrar Despesa", bg="#f44336", fg="white", command=add_despesa).pack(pady=10)

    def gerar_nfe(self):
        # Aqui gera uma NF-e simples em TXT (mock). Depois posso transformar em XML real se quiser.
        janela = tk.Toplevel(self)
        janela.title("Gerar NF-e")
        janela.geometry("500x300")

        tk.Label(janela, text="Digite o número da OS para gerar NF-e:").pack(pady=10)
        num_os = tk.Entry(janela, width=30)
        num_os.pack()

        def emitir():
            try:
                os_id = int(num_os.get())
                c.execute("SELECT * FROM os WHERE id=?", (os_id,))
                os_data = c.fetchone()
                if not os_data:
                    messagebox.showerror("Erro", "OS não encontrada")
                    return

                nome_arq = f"NF-e_OS_{os_id}.txt"
                with open(nome_arq, "w", encoding="utf-8") as f:
                    f.write(f"NOTA FISCAL ELETRÔNICA (MOCK)\n")
                    f.write(f"OS: {os_id} | Data: {os_data[1]}\n")
                    f.write(f"Total: R$ {os_data[4]:.2f}\n")
                    f.write("="*50 + "\n")
                    c.execute("SELECT descricao, quantidade, preco FROM os_itens WHERE os_id=?", (os_id,))
                    for item in c.fetchall():
                        f.write(f"{item[0]} | Qtd: {item[1]} | Preço: R$ {item[2]:.2f}\n")

                messagebox.showinfo("Sucesso", f"NF-e salva como {nome_arq}\nAbra o arquivo!")
                os.startfile(nome_arq)  # abre automaticamente no Windows
            except:
                messagebox.showerror("Erro", "Digite um número válido de OS")

        tk.Button(janela, text="Emitir NF-e", bg="#2196F3", fg="white", font=("Arial", 14), command=emitir).pack(pady=20)

if __name__ == "__main__":
    app = OficinaApp()
    app.mainloop()

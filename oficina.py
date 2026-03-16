import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# ==================== LOGIN SIMPLES ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Usuários cadastrados (você pode adicionar mais aqui!)
USUARIOS = {
    "admin": "1234",
    "Claudinei": "oficina2025"
}

if not st.session_state.logged_in:
    st.title("🔐 Login - Oficina Mecânica")
    st.markdown("### Digite seu usuário e senha")
    
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuário")
    with col2:
        senha = st.text_input("Senha", type="password")
    
    if st.button("🚪 Entrar", type="primary"):
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state.logged_in = True
            st.session_state.username = usuario
            st.success(f"Bem-vindo, {usuario}! 🎉")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorreto")
    
    st.caption("Usuários padrão:\nadmin / 1234\nmecanico / oficina2025")
    st.stop()  # para aqui até fazer login

# ==================== SE JÁ ESTIVER LOGADO ====================
st.set_page_config(page_title="Oficina Mecânica", layout="wide")
st.title("🚗 Oficina Mecânica - Sistema Fácil")
st.markdown(f"**Bem-vindo, {st.session_state.username}!**")

# Botão de sair
if st.sidebar.button("🚪 Sair"):
    st.session_state.logged_in = False
    st.rerun()

# ==================== BANCO DE DADOS (igual antes) ====================
conn = sqlite3.connect('oficina.db', check_same_thread=False)
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

# ==================== MENU LATERAL ====================
menu = st.sidebar.selectbox(
    "Escolha o que fazer:",
    ["👤 Cadastrar Cliente",
     "🚘 Cadastrar Veículo",
     "📋 Nova Ordem de Serviço",
     "📋 Listar Ordens de Serviço",
     "💰 Relatório de Gastos e Lucro",
     "📄 Gerar NF-e"]
)

# (Todo o resto do código é exatamente igual ao anterior — só colei aqui pra não ficar gigante)

# ==================== CADASTRAR CLIENTE ====================
if menu == "👤 Cadastrar Cliente":
    st.subheader("Cadastrar Novo Cliente")
    with st.form("form_cliente"):
        nome = st.text_input("Nome completo")
        telefone = st.text_input("Telefone")
        cpf = st.text_input("CPF")
        if st.form_submit_button("💾 Salvar Cliente"):
            if nome:
                c.execute("INSERT INTO clientes (nome, telefone, cpf) VALUES (?,?,?)", (nome, telefone, cpf))
                conn.commit()
                st.success("✅ Cliente cadastrado com sucesso!")
            else:
                st.error("Preencha o nome")

# ==================== CADASTRAR VEÍCULO ====================
elif menu == "🚘 Cadastrar Veículo":
    st.subheader("Cadastrar Veículo")
    c.execute("SELECT id, nome FROM clientes")
    clientes = c.fetchall()
    if not clientes:
        st.warning("Cadastre um cliente primeiro!")
    else:
        lista_clientes = [f"{id} - {nome}" for id, nome in clientes]
        with st.form("form_veiculo"):
            cliente = st.selectbox("Cliente", lista_clientes)
            placa = st.text_input("Placa")
            modelo = st.text_input("Modelo do veículo")
            if st.form_submit_button("💾 Salvar Veículo"):
                cliente_id = cliente.split(" - ")[0]
                c.execute("INSERT INTO veiculos (cliente_id, placa, modelo) VALUES (?,?,?)",
                          (cliente_id, placa, modelo))
                conn.commit()
                st.success("✅ Veículo cadastrado!")

# ==================== NOVA ORDEM DE SERVIÇO ====================
elif menu == "📋 Nova Ordem de Serviço":
    st.subheader("Nova Ordem de Serviço")
    c.execute("SELECT id, nome FROM clientes")
    clientes = [f"{id} - {nome}" for id, nome in c.fetchall()]
    cliente_sel = st.selectbox("Cliente", clientes) if clientes else None
    
    c.execute("SELECT id, placa FROM veiculos")
    veiculos = [f"{id} - {placa}" for id, placa in c.fetchall()]
    veiculo_sel = st.selectbox("Veículo", veiculos) if veiculos else None
    
    if "itens_os" not in st.session_state:
        st.session_state.itens_os = []
    
    st.write("### Adicionar serviços/peças")
    col1, col2, col3 = st.columns(3)
    with col1: desc = st.text_input("Descrição")
    with col2: qtd = st.number_input("Quantidade", min_value=0.1, step=0.1)
    with col3: preco = st.number_input("Preço unitário R$", min_value=0.0, step=0.1)
    
    if st.button("➕ Adicionar item"):
        if desc and qtd > 0 and preco > 0:
            subtotal = qtd * preco
            st.session_state.itens_os.append([desc, qtd, preco, subtotal])
            st.rerun()
    
    if st.session_state.itens_os:
        df_itens = pd.DataFrame(st.session_state.itens_os, columns=["Descrição", "Qtd", "Preço", "Subtotal"])
        st.dataframe(df_itens, use_container_width=True)
        total = df_itens["Subtotal"].sum()
        st.success(f"**Total da OS: R$ {total:.2f}**")
    
    if st.button("💾 Salvar Ordem de Serviço", type="primary"):
        if cliente_sel and veiculo_sel and st.session_state.itens_os:
            cliente_id = cliente_sel.split(" - ")[0]
            veiculo_id = veiculo_sel.split(" - ")[0]
            total = sum(item[3] for item in st.session_state.itens_os)
            
            c.execute("INSERT INTO os (data, cliente_id, veiculo_id, total, status) VALUES (?,?,?,?,?)",
                      (datetime.now().strftime("%d/%m/%Y"), cliente_id, veiculo_id, total, "Aberta"))
            os_id = c.lastrowid
            
            for item in st.session_state.itens_os:
                c.execute("INSERT INTO os_itens (os_id, descricao, quantidade, preco) VALUES (?,?,?,?)",
                          (os_id, item[0], item[1], item[2]))
            conn.commit()
            st.success(f"✅ Ordem de Serviço #{os_id} salva!")
            st.session_state.itens_os = []
            st.rerun()
        else:
            st.error("Preencha todos os campos")

# ==================== LISTAR OS ====================
elif menu == "📋 Listar Ordens de Serviço":
    st.subheader("Todas as Ordens de Serviço")
    df = pd.read_sql_query("""
        SELECT os.id, os.data, clientes.nome as cliente, os.total, os.status 
        FROM os 
        JOIN clientes ON os.cliente_id = clientes.id
        ORDER BY os.id DESC
    """, conn)
    st.dataframe(df, use_container_width=True)

# ==================== RELATÓRIO GASTOS ====================
elif menu == "💰 Relatório de Gastos e Lucro":
    st.subheader("Relatório Financeiro")
    total_os = pd.read_sql_query("SELECT SUM(total) as total FROM os", conn).iloc[0]['total'] or 0
    total_despesas = pd.read_sql_query("SELECT SUM(valor) as total FROM despesas", conn).iloc[0]['total'] or 0
    lucro = total_os - total_despesas
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Recebido (OS)", f"R$ {total_os:.2f}")
    col2.metric("Total Despesas", f"R$ {total_despesas:.2f}")
    col3.metric("💰 LUCRO", f"R$ {lucro:.2f}")
    
    st.subheader("Adicionar Nova Despesa")
    with st.form("despesa"):
        desc = st.text_input("Descrição da despesa")
        valor = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Registrar Despesa"):
            c.execute("INSERT INTO despesas (data, descricao, valor) VALUES (?,?,?)",
                      (datetime.now().strftime("%d/%m/%Y"), desc, valor))
            conn.commit()
            st.success("Despesa registrada!")
            st.rerun()

# ==================== GERAR NF-e ====================
elif menu == "📄 Gerar NF-e":
    st.subheader("Gerar NF-e (Nota Fiscal)")
    df_os = pd.read_sql_query("SELECT id FROM os ORDER BY id DESC", conn)
    if not df_os.empty:
        os_id = st.selectbox("Escolha a Ordem de Serviço", df_os['id'])
        if st.button("📄 Gerar e Baixar NF-e"):
            os_data = pd.read_sql_query(f"SELECT * FROM os WHERE id={os_id}", conn).iloc[0]
            itens = pd.read_sql_query(f"SELECT * FROM os_itens WHERE os_id={os_id}", conn)
            
            conteudo = f"""NOTA FISCAL ELETRÔNICA (SIMPLIFICADA)
====================================
OS: {os_id}
Data: {os_data['data']}
Cliente: {pd.read_sql_query(f"SELECT nome FROM clientes WHERE id={os_data['cliente_id']}", conn).iloc[0]['nome']}
Veículo: {pd.read_sql_query(f"SELECT placa FROM veiculos WHERE id={os_data['veiculo_id']}", conn).iloc[0]['placa']}
====================================
ITENS:
"""
            for _, item in itens.iterrows():
                conteudo += f"{item['descricao']} | Qtd: {item['quantidade']} | Preço: R$ {item['preco']:.2f}\n"
            conteudo += f"\nTOTAL: R$ {os_data['total']:.2f}\n"
            
            st.download_button(
                label="⬇️ Baixar NF-e agora",
                data=conteudo,
                file_name=f"NF-e_OS_{os_id}.txt",
                mime="text/plain"
            )
            st.success("NF-e gerada! Clique no botão acima para baixar.")
    else:
        st.warning("Nenhuma OS cadastrada ainda.")

st.sidebar.caption("Sistema com login protegido ❤️\nQualquer dúvida é só falar!")
import json, os, datetime
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'macaco'

# Configurações de pastas
BASE_DIR = 'db_usuarios'
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --- FUNÇÕES DE BANCO DE DADOS POR USUÁRIO ---

def get_user_path(username):
    return os.path.join(BASE_DIR, f"{username.lower()}.json")

def carregar_dados_usuario(username):
    path = get_user_path(username)
    if not os.path.exists(path):
        return {"senha": "", "historico": {}}
    with open(path, 'r') as f:
        return json.load(f)

def salvar_dados_usuario(username, dados):
    path = get_user_path(username)
    with open(path, 'w') as f:
        json.dump(dados, f)

# --- LÓGICA DE ANÁLISE (A mesma que você já usa) ---

def gerar_analise_especialista(ctr, roas, lucro, cpa, vendas, dias, anterior=None):
    # (Mantive a lógica anterior conforme seu pedido)
    veredito = []
    plano_acao = []
    
    if anterior:
        diff = roas - anterior.get('roas', 0)
        if diff > 0: veredito.append({"status": "sucesso", "msg": f"📈 Evolução: Seu ROAS subiu {diff:.2f}x."})
        elif diff < 0: veredito.append({"status": "erro", "msg": f"📉 Queda: O ROAS caiu {abs(diff):.2f}x."})
    
    if lucro > 0: veredito.append({"status": "sucesso", "msg": "Operação lucrando."})
    else: veredito.append({"status": "erro", "msg": "Operação no prejuízo."})
    
    if ctr < 1.0: veredito.append({"status": "erro", "msg": f"CTR Baixo ({ctr}%)."})
    else: veredito.append({"status": "sucesso", "msg": f"CTR Forte ({ctr}%)."})

    if ctr < 1.2: plano_acao.append("🚀 Teste 3 novos ganchos de vídeo.")
    else: plano_acao.append("💎 Escala Criativa: Duplique o melhor anúncio.")
    
    if roas < 2.5: plano_acao.append("🛒 Revise sua oferta ou dê um cupom.")
    else: plano_acao.append("📈 Escala Vertical: Aumente orçamento em 15%.")

    return veredito[:5], plano_acao[:2]

# --- ROTAS DE ACESSO ---

# --- ROTAS DE ACESSO (SUBSTITUA AS SUAS POR ESTAS) ---
# Adicione isso ao seu app.py

CHAVES_FILE = 'chaves.json'

def carregar_chaves():
    if not os.path.exists(CHAVES_FILE):
        return []
    with open(CHAVES_FILE, 'r') as f:
        return json.load(f)

def salvar_chaves(lista):
    with open(CHAVES_FILE, 'w') as f:
        json.dump(lista, f)

@app.route('/ativar', methods=['GET', 'POST'])
def ativar():
    if request.method == 'POST':
        chave_digitada = request.form.get('chave').strip()
        user = (request.form.get('usuario') or '').strip().lower()
        senha = request.form.get('senha')
        
        chaves_validas = carregar_chaves()
        
        if chave_digitada not in chaves_validas:
            return render_template('ativar.html', erro="Chave de acesso inválida ou já utilizada!")
        
        if os.path.exists(get_user_path(user)):
            return render_template('ativar.html', erro="Este usuário já existe!")

        # 1. Cria o usuário
        dados = {"senha": generate_password_hash(senha), "historico": {}}
        salvar_dados_usuario(user, dados)
        
        # 2. "Queima" a chave para não ser usada de novo
        chaves_validas.remove(chave_digitada)
        salvar_chaves(chaves_validas)
        
        session['usuario'] = user
        return redirect(url_for('index'))
        
    return render_template('ativar.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = (request.form.get('usuario') or '').strip().lower()
        senha = request.form.get('senha')
        
        if not user or not senha:
            return render_template('login.html', erro="Preencha todos os campos!")

        path = get_user_path(user)

        # SE O USUÁRIO NÃO EXISTE
        if not os.path.exists(path):
            # CRIAMOS A CONTA AUTOMATICAMENTE PARA ELE NÃO DAR ERRO
            dados = {
                "senha": generate_password_hash(senha),
                "historico": {}
            }
            salvar_dados_usuario(user, dados)
            session['usuario'] = user
            return redirect(url_for('index'))

        # SE O USUÁRIO JÁ EXISTE, VERIFICA A SENHA
        dados = carregar_dados_usuario(user)
        # Se por algum motivo o arquivo existir mas não tiver senha (erro de sistema)
        if not dados.get("senha"):
            dados["senha"] = generate_password_hash(senha)
            salvar_dados_usuario(user, dados)

        if check_password_hash(dados["senha"], senha):
            session['usuario'] = user
            return redirect(url_for('index'))
        
        return render_template('login.html', erro="Senha incorreta para este usuário!")
        
    return render_template('login.html')

""" @app.route('/cadastro', methods=['GET', 'POST'])
 def cadastro():
    if request.method == 'POST':
        user = (request.form.get('usuario') or '').strip().lower()
        senha = request.form.get('senha')
        
        if not user or not senha:
            return render_template('cadastro.html', erro="Preencha todos os campos!")

        if os.path.exists(get_user_path(user)):
            return render_template('cadastro.html', erro="Este usuário já existe! Vá em Login.")
        
        # Cria e salva
        dados = {"senha": generate_password_hash(senha), "historico": {}}
        salvar_dados_usuario(user, dados)
        
        # JÁ LOGA O USUÁRIO DIRETO (Melhor experiência)
        session['usuario'] = user
        return redirect(url_for('index'))
        
    return render_template('cadastro.html')
"""
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'usuario' not in session: return redirect(url_for('login'))
    
    user_data = carregar_dados_usuario(session['usuario'])
    historico = user_data['historico']
    r = None
    
    if request.method == 'POST':
        nome_camp = request.form.get('nome_campanha', 'GERAL').strip().upper()
        inv = float(request.form.get('investimento') or 0)
        cpc = float(request.form.get('cpc') or 1)
        cliques = int(request.form.get('cliques') or 0)
        vendas = int(request.form.get('vendas') or 0)
        preco_venda = float(request.form.get('preco_venda') or 0)
        custo_prod = float(request.form.get('custo_produto') or 0)
        dias = int(request.form.get('dias') or 1)
        
        faturamento = vendas * preco_venda
        lucro_valor = faturamento - (inv + (vendas * custo_prod) + (faturamento * 0.05))
        roas = faturamento / inv if inv > 0 else 0
        ctr = (cliques / (inv / cpc)) * 100 if inv > 0 else 0
        
        # Busca anterior apenas no histórico DESTE usuário
        lista_analises = historico.get(nome_camp, [])
        anterior = lista_analises[0] if lista_analises else None
        
        v, p = gerar_analise_especialista(round(ctr, 2), round(roas, 2), lucro_valor, 0, vendas, dias, anterior)

        r = {
            "nome": nome_camp, "lucro": f"R$ {lucro_valor:,.2f}", "roas": round(roas, 2), "ctr": round(ctr, 2),
            "status_cor": "text-emerald-400" if lucro_valor > 0 else "text-rose-500",
            "veredito": v, "plano_acao": p
        }
        
        # Salva no histórico do usuário
        nova_analise = {
            "roas": round(roas, 2), "lucro": lucro_valor, "ctr": round(ctr, 2), 
            "vendas": vendas, "data": datetime.datetime.now().strftime("%d/%m %H:%M")
        }
        
        if nome_camp not in historico: historico[nome_camp] = []
        historico[nome_camp].insert(0, nova_analise)
        user_data['historico'] = historico
        salvar_dados_usuario(session['usuario'], user_data)

    return render_template('index.html', r=r, historico=historico, usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
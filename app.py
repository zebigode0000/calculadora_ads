import json, os, datetime
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'macaco'

BASE_DIR = 'db_usuarios'
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
CHAVES_FILE = 'chaves.json'

# --- FUNÇÕES AUXILIARES ---
def get_user_path(username): return os.path.join(BASE_DIR, f"{username.lower()}.json")

def carregar_dados_usuario(username):
    path = get_user_path(username)
    if not os.path.exists(path): return {"senha": "", "historico": {}}
    with open(path, 'r') as f: return json.load(f)

def salvar_dados_usuario(username, dados):
    with open(get_user_path(username), 'w') as f: json.dump(dados, f)

def carregar_chaves():
    if not os.path.exists(CHAVES_FILE): return []
    with open(CHAVES_FILE, 'r') as f: return json.load(f)

def salvar_chaves(lista):
    with open(CHAVES_FILE, 'w') as f: json.dump(lista, f)

# --- NOVA LÓGICA DE INTELIGÊNCIA COM ANÁLISE DE FUNIL ---
def gerar_analise_especialista(ctr, roas, lucro, cpa_real, cpa_ideal, break_even, cliques, checkouts, vendas):
    veredito = []
    plano_acao = []
    
    # 1. Análise de Lucratividade
    if roas >= break_even:
        veredito.append({"status": "sucesso", "msg": f"✅ Operação Segura: Seu ROAS ({roas}) está acima do break-even ({break_even:.2f})."})
    else:
        veredito.append({"status": "erro", "msg": f"🚨 Alerta de Prejuízo: ROAS abaixo do ponto de equilíbrio."})

    # 2. Análise de CPA
    if cpa_real <= cpa_ideal:
        veredito.append({"status": "sucesso", "msg": f"🎯 Meta de CPA: R${cpa_real:.2f} está dentro do limite."})
        plano_acao.append("📈 ESCALA: Aumente o orçamento em 20% a cada 48h.")
    else:
        veredito.append({"status": "erro", "msg": f"💸 CPA Caro: R${cpa_real:.2f} (Meta era R${cpa_ideal:.2f})."})
        plano_acao.append("🛑 PAUSAR/REVISAR: O custo por venda está alto demais.")

    # 3. ANÁLISE DE FUNIL (Página vs Checkout)
    taxa_checkout = (checkouts / cliques * 100) if cliques > 0 else 0
    taxa_venda_final = (vendas / checkouts * 100) if checkouts > 0 else 0

    if cliques > 20:
        if taxa_checkout < 7:
            veredito.append({"status": "erro", "msg": f"📉 Falha na Página: Apenas {taxa_checkout:.1f}% iniciaram checkout. Sua página não está convencendo."})
            plano_acao.append("🎨 Melhore o Header e o carregamento da página de vendas.")
        else:
            veredito.append({"status": "sucesso", "msg": f"💎 Página Forte: {taxa_checkout:.1f}% de conversão para checkout."})

    if checkouts > 0:
        if taxa_venda_final < 30:
            veredito.append({"status": "alerta", "msg": f"🛒 Abandono de Carrinho: Apenas {taxa_venda_final:.1f}% dos checkouts viram venda. Verifique frete ou preço."})
            plano_acao.append("📧 Ative/Otimize sua recuperação de carrinho e WhatsApp.")

    return veredito, plano_acao

# --- ROTAS ---
@app.route('/ativar', methods=['GET', 'POST'])
def ativar():
    if request.method == 'POST':
        chave = request.form.get('chave', '').strip()
        user = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha')
        chaves = carregar_chaves()
        if chave in chaves and user:
            salvar_dados_usuario(user, {"senha": generate_password_hash(senha), "historico": {}})
            chaves.remove(chave)
            salvar_chaves(chaves)
            session['usuario'] = user
            return redirect(url_for('index'))
    return render_template('ativar.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha')
        dados = carregar_dados_usuario(user)
        if dados.get("senha") and check_password_hash(dados["senha"], senha):
            session['usuario'] = user
            return redirect(url_for('index'))
    return render_template('login.html', erro="Usuário ou senha incorretos")

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'usuario' not in session: return redirect(url_for('login'))
    user_data = carregar_dados_usuario(session['usuario'])
    r = None
    
    if request.method == 'POST':
        inv = float(request.form.get('investimento') or 0)
        cliques = int(request.form.get('cliques') or 0)
        checkouts = int(request.form.get('checkouts') or 0)
        vendas = int(request.form.get('vendas') or 0)
        preco_venda = float(request.form.get('preco_venda') or 0)
        cpa_ideal = float(request.form.get('cpa_ideal') or 0)
        custo_prod = float(request.form.get('custo_produto') or 0)
        
        # Cálculos avançados
        faturamento = vendas * preco_venda
        roas = faturamento / inv if inv > 0 else 0
        lucro_liquido = faturamento - (inv + (vendas * custo_prod) + (faturamento * 0.06))
        cpa_real = inv / vendas if vendas > 0 else inv
        ctr = (cliques / (cliques * 10)) * 100 if cliques > 0 else 0 # Simulação de impressões
        
        margem = (preco_venda - custo_prod) / preco_venda if preco_venda > 0 else 0
        break_even = 1 / margem if margem > 0 else 0
        
        v, p = gerar_analise_especialista(round(ctr, 2), round(roas, 2), lucro_liquido, 
                                         cpa_real, cpa_ideal, break_even, 
                                         cliques, checkouts, vendas)

        r = {
            "lucro": f"R$ {lucro_liquido:,.2f}", 
            "roas": round(roas, 2), 
            "cpa": round(cpa_real, 2),
            "break_even": round(break_even, 2),
            "taxa_checkout": (checkouts/cliques*100) if cliques > 0 else 0,
            "taxa_venda": (vendas/checkouts*100) if checkouts > 0 else 0,
            "veredito": v, "plano_acao": p,
            "cor_lucro": "text-emerald-400" if lucro_liquido > 0 else "text-rose-500"
        }
        
        nova = {"data": datetime.datetime.now().strftime("%d/%m"), "roas": round(roas, 2), "lucro": lucro_liquido}
        hist = user_data.get('historico', {})
        if 'GERAL' not in hist: hist['GERAL'] = []
        hist['GERAL'].insert(0, nova)
        user_data['historico'] = hist
        salvar_dados_usuario(session['usuario'], user_data)

    return render_template('index.html', r=r, historico=user_data.get('historico', {}), usuario=session['usuario'])

if __name__ == '__main__':
    app.run()
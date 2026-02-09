# criar_cliente.py
import json, os
from werkzeug.security import generate_password_hash

BASE_DIR = 'db_usuarios'
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)

def criar_novo_acesso(usuario, senha):
    user_path = os.path.join(BASE_DIR, f"{usuario.lower()}.json")
    
    if os.path.exists(user_path):
        print(f"❌ Erro: O usuário '{usuario}' já existe!")
        return

    dados = {
        "senha": generate_password_hash(senha),
        "historico": {}
    }
    
    with open(user_path, 'w') as f:
        json.dump(dados, f)
    
    print(f"✅ Sucesso! Cliente '{usuario}' criado com a senha '{senha}'.")

# --- EXECUÇÃO ---
# Quando você vender uma conta, mude os nomes abaixo e rode o script:
novo_user = "cliente_premium"
nova_pass = "senha123"

criar_novo_acesso(novo_user, nova_pass)
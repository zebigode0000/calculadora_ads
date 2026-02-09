import json

def gerar_chave(nova_chave):
    try:
        with open('chaves.json', 'r') as f:
            chaves = json.load(f)
    except:
        chaves = []
    
    chaves.append(nova_chave)
    
    with open('chaves.json', 'w') as f:
        json.dump(chaves, f)
    print(f"✅ Chave {nova_chave} gerada! Mande para o cliente.")

# Exemplo: use o nome do cliente ou um código aleatório
gerar_chave("CLIENTE-AB-123")
# config.py
import os

# Configurações da API do WhatsApp (Substitua pelos seus valores reais)
WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN", "SEU_TOKEN_DE_ACESSO_AQUI")
SENDER_PHONE_NUMBER_ID = os.environ.get("SENDER_PHONE_NUMBER_ID", "ID_DO_SEU_NUMERO_REMETENTE")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "SEU_TOKEN_DE_VERIFICACAO_WEBHOOK_AQUI")
WHATSAPP_API_VERSION = "v19.0"

# Configurações da Pizzaria
NOME_DA_PIZZARIA = "Sua Pizzaria Incrível"
LINK_CARDAPIO_ONLINE = "https://link_para_seu_cardapio.com/cardapio.pdf"
HORARIO_FUNCIONAMENTO = "Terça a Domingo, das 18h às 23h."
ENDERECO_PIZZARIA = "Rua das Pizzas, 123, Bairro Saboroso, Cidade Feliz - ES"
PIX_CHAVE = "seu_email_ou_telefone_pix@dominio.com"
TEMPO_MEDIO_PREPARO_RETIRADA = "30-40"
TEMPO_MEDIO_ENTREGA = "45-60"
PROMOCOES_DO_DIA = "Hoje temos: Pizza G Calabresa + Refri 2L por R$XX,XX!"
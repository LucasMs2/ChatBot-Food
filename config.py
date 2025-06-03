import os

# Configurações da API do WhatsApp
WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN", "SEU_TOKEN_DE_ACESSO_AQUI")
SENDER_PHONE_NUMBER_ID = os.environ.get("SENDER_PHONE_NUMBER_ID", "ID_DO_SEU_NUMERO_REMETENTE")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "SEU_TOKEN_DE_VERIFICACAO_WEBHOOK_AQUI") # Defina um token seguro
WHATSAPP_API_VERSION = "v19.0" # Verifique a versão atual

# Configurações da Pizzaria
NOME_DA_PIZZARIA = "Pizzaria Pizzas, a melhor pizzaria da galáxia"
LINK_CARDAPIO_ONLINE = "https://link_para_seu_cardapio.com/cardapio.pdf"
HORARIO_FUNCIONAMENTO = "Terça a Domingo, das 18h às 23h."
ENDERECO_PIZZARIA = "Rua das Pizzas, 123, Bairro Saboroso, Cidade Feliz - ES"
PIX_CHAVE = "seu_email_ou_telefone_pix@dominio.com"
TEMPO_MEDIO_PREPARO_RETIRADA = "30-40" # em minutos
TEMPO_MEDIO_ENTREGA = "45-60" # em minutos
PROMOCOES_DO_DIA = ""
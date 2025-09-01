# terminal_tester.py
import chatbot_logic


def print_interactive_options(interactive_payload):
    interactive_type = interactive_payload.get('type')
    print("\n[BOT]: --- Opções Clicáveis (Simulação) ---")

    if interactive_type == 'button':
        buttons = interactive_payload.get('action', {}).get('buttons', [])
        for button in buttons:
            title = button.get('reply', {}).get('title', 'Sem título')
            button_id = button.get('reply', {}).get('id', 'sem_id')
            print(f"  • {title}   | ID: {button_id}")

    elif interactive_type == 'list':
        list_button_title = interactive_payload.get('action', {}).get('button', 'Ver Opções')
        print(f"(O usuário clicaria no botão: '{list_button_title}')")
        for section in interactive_payload.get('action', {}).get('sections', []):
            print(f"\n-- Seção: {section.get('title', '')} --")
            for row in section.get('rows', []):
                title = row.get('title', 'Sem título')
                row_id = row.get('id', 'sem_id')
                print(f"  • {title}   | ID: {row_id}")

    print("----------------------------------------")


def terminal_test_chat():
    print("--- Iniciando Teste do Chatbot no Terminal ---")
    print("Digite 'exit' a qualquer momento para encerrar.")
    print("----------------------------------------------")
    test_user_id = "terminal_user_001"
    test_user_name = "Cliente Terminal"
    if test_user_id in chatbot_logic.user_sessions: del chatbot_logic.user_sessions[test_user_id]

    first_input = "oi"
    print(f"\n[{test_user_name}]: {first_input}")
    bot_response = chatbot_logic.handle_message(test_user_id, test_user_name, first_input)

    while True:
        if isinstance(bot_response, dict):
            print(f"[BOT]: {bot_response.get('text', '')}")
            if bot_response.get('interactive'): print_interactive_options(bot_response.get('interactive'))
        elif isinstance(bot_response, str):
            print(f"[BOT]: {bot_response}")
        else:
            print(f"[BOT - ERRO]: Tipo de resposta inesperado: {bot_response}")

        user_input = input(f"\n[{test_user_name}]: ")
        if user_input.lower() == 'exit':
            print("\n--- Teste encerrado ---");
            break
        bot_response = chatbot_logic.handle_message(test_user_id, test_user_name, user_input)


if __name__ == '__main__':
    terminal_test_chat()
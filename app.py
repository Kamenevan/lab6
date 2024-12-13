from flask import Flask, jsonify

# Создаем объект приложения Flask
app = Flask(__name__)

# Идентификатор инстанса (заполним позже)
instance_id = None


# Маршрут для проверки состояния
@app.route('/health', methods=['GET'])
def health():
    """
    Возвращает информацию о состоянии инстанса.
    """
    return jsonify({"status": "healthy", "instance_id": instance_id}), 200


# Маршрут для обработки запросов
@app.route('/process', methods=['GET'])
def process():
    """
    Возвращает идентификатор инстанса, на котором обрабатывается запрос.
    """
    return jsonify({"message": "Request processed", "instance_id": instance_id}), 200


# Точка входа
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python app.py <port>")
        sys.exit(1)

    # Получаем порт из аргументов командной строки
    port = int(sys.argv[1])
    # Устанавливаем идентификатор инстанса
    instance_id = f"Instance running on port {port}"
    # Запускаем приложение на указанном порту
    app.run(port=port)


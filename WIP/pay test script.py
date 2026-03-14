import requests
import json
from datetime import datetime

class CryptoBot:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://pay.crypt.bot/api"
        self.headers = {
            "Crypto-Pay-API-Token": token,
            "Content-Type": "application/json"
        }
    
    def create_invoice(self, amount, asset="USDT", description="", hidden_message="", paid_btn_name=None, paid_btn_url=None, payload=""):
        """
        Создание одноразового счета
        """
        
        url = f"{self.base_url}/createInvoice"
        
        # Подготовка данных
        data = {
            "asset": asset,
            "amount": str(amount),
            "description": description,
            "hidden_message": hidden_message,
            "payload": payload,
            "allow_comments": False,
            "allow_anonymous": False,
            "expires_in": 3600
        }
        
        # Добавляем paid_btn_name и paid_btn_url только если они указаны
        if paid_btn_name and paid_btn_url:
            data["paid_btn_name"] = paid_btn_name
            data["paid_btn_url"] = paid_btn_url
        elif paid_btn_name and not paid_btn_url:
            # Если указано только имя кнопки, используем дефолтный URL
            data["paid_btn_name"] = paid_btn_name
            data["paid_btn_url"] = "https://t.me/CryptoBot"
        
        # Удаляем пустые поля
        data = {k: v for k, v in data.items() if v is not None and v != ""}
        
        print(f"Отправляемые данные: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            print(f"Статус ответа: {response.status_code}")
            print(f"Текст ответа: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при создании счета: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Текст ошибки: {e.response.text}")
            return None

def main():
    # Настройки
    API_TOKEN = "478664:AA183lxiXRK06NSmAwdRvT19VjY40ewX5RA"
    
    # Инициализация клиента
    bot = CryptoBot(API_TOKEN)
    
    print("=== CryptoBot Invoice Creator ===")
    
    while True:
        print("\n" + "="*40)
        print("1. Создать новый счет")
        print("2. Выход")
        
        choice = input("\nВыберите действие (1-2): ").strip()
        
        if choice == "1":
            create_simple_invoice(bot)
        elif choice == "2":
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

def create_simple_invoice(bot):
    """Упрощенный процесс создания счета"""
    
    try:
        # Простой ввод данных
        amount = float(input("Введите сумму: ").strip())
        
        print("\nДоступные валюты: USDT, BTC, ETH, BNB, etc.")
        asset = input("Введите валюту [USDT]: ").strip() or "USDT"
        
        description = input("Введите описание счета: ").strip()
        
        # Настройки кнопки после оплаты
        print("\nНастройка кнопки после оплаты:")
        print("1. Без кнопки (просто уведомление)")
        print("2. Просмотреть товар (требует URL)")
        print("3. Открыть сайт (требует URL)")
        print("4. Открыть бота")
        
        btn_choice = input("Выберите вариант [1]: ").strip() or "1"
        
        paid_btn_name = None
        paid_btn_url = None
        
        if btn_choice == "2":
            paid_btn_name = "viewItem"
            paid_btn_url = input("Введите URL товара: ").strip() or "https://t.me/CryptoBot"
        elif btn_choice == "3":
            paid_btn_name = "openUrl"
            paid_btn_url = input("Введите URL сайта: ").strip() or "https://t.me/CryptoBot"
        elif btn_choice == "4":
            paid_btn_name = "openBot"
            paid_btn_url = "https://t.me/CryptoBot"
        
        # Создание счета
        print("\nСоздание счета...")
        result = bot.create_invoice(
            amount=amount,
            asset=asset.upper(),
            description=description,
            paid_btn_name=paid_btn_name,
            paid_btn_url=paid_btn_url
        )
        
        if result and result.get("ok"):
            invoice = result["result"]
            print("\n✅ Счет успешно создан!")
            print(f"ID счета: {invoice['invoice_id']}")
            print(f"Сумма: {invoice['amount']} {invoice['asset']}")
            print(f"Описание: {invoice.get('description', 'Нет')}")
            print(f"Ссылка для оплаты: {invoice['pay_url']}")
            print(f"Статус: {invoice['status']}")
            print(f"Действителен до: {datetime.fromtimestamp(invoice['expiration_date'])}")
            
            # Сохраняем ссылку в файл для удобства
            with open("invoice_links.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()}: {invoice['pay_url']} - {invoice['amount']} {invoice['asset']}\n")
                
        else:
            print("❌ Ошибка при создании счета")
            if result:
                error_info = result.get('error', {})
                print(f"Код ошибки: {error_info.get('code')}")
                print(f"Описание: {error_info.get('name')}")
            
    except ValueError:
        print("❌ Ошибка: Неверный формат суммы")
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")

if __name__ == "__main__":
    main()

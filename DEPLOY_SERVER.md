# Развертывание парсера тендеров на VPS сервере

## Подготовка сервера

### 1. Создание VPS
1. Выбери провайдера: Yandex Cloud, Timeweb, REG.RU
2. Создай VPS с Ubuntu 20.04/22.04
3. Минимальная конфигурация: 1 vCPU, 1-2GB RAM, 10GB SSD
4. Получи IP адрес и данные для SSH

### 2. Подключение к серверу
```bash
# Подключение по SSH (из PowerShell на Windows)
ssh root@YOUR_SERVER_IP

# Или через PuTTY с указанием IP и порта 22
```

### 3. Установка зависимостей на сервере
```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Python и необходимых пакетов
apt install python3 python3-pip python3-venv git wget -y

# Установка Chrome для Selenium
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/chrome.list
apt update
apt install google-chrome-stable -y

# Установка ChromeDriver
apt install chromium-chromedriver -y
```

## Загрузка проекта на сервер

### Вариант 1: Через SCP (рекомендуется)
```bash
# На твоем компьютере, из папки с проектом
scp -r . root@YOUR_SERVER_IP:/root/govparser/
```

### Вариант 2: Через Git (если проект в репозитории)
```bash
# На сервере
cd /root
git clone YOUR_REPOSITORY_URL govparser
cd govparser
```

### Вариант 3: Ручная загрузка
1. Архивируй папку govparser в ZIP
2. Используй FileZilla или WinSCP для загрузки
3. Распакуй на сервере: `unzip govparser.zip`

## Настройка проекта на сервере

```bash
# Переход в папку проекта
cd /root/govparser

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Проверка настроек config.py
nano config.py
```

## Настройка автозапуска

### 1. Создание systemd сервиса
```bash
# Создание файла сервиса
nano /etc/systemd/system/govparser.service
```

### 2. Содержимое файла сервиса:
```ini
[Unit]
Description=Government Tender Parser
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/govparser
Environment=PATH=/root/govparser/.venv/bin
ExecStart=/root/govparser/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Активация сервиса
```bash
# Перезагрузка systemd
systemctl daemon-reload

# Включение автозапуска
systemctl enable govparser.service

# Запуск сервиса
systemctl start govparser.service

# Проверка статуса
systemctl status govparser.service
```

## Мониторинг работы

### Просмотр логов
```bash
# Логи systemd
journalctl -u govparser.service -f

# Логи парсера
tail -f /root/govparser/parser.log
```

### Управление сервисом
```bash
# Остановка
systemctl stop govparser.service

# Перезапуск  
systemctl restart govparser.service

# Отключение автозапуска
systemctl disable govparser.service
```

## Настройка Chrome для сервера

Добавь в конфигурацию Chrome опции для работы на сервере без GUI:

```python
# В parsers/base_parser.py или где настраиваются опции Chrome
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')  
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--remote-debugging-port=9222')
```

## Обновление парсера

```bash
# Остановка сервиса
systemctl stop govparser.service

# Обновление файлов (через scp или git pull)
scp -r . root@YOUR_SERVER_IP:/root/govparser/

# Перезапуск сервиса
systemctl start govparser.service
```

## Безопасность

### 1. Создание отдельного пользователя
```bash
# Создание пользователя parser
useradd -m -s /bin/bash parser
su - parser

# Перенос проекта в домашнюю папку пользователя
mv /root/govparser /home/parser/
chown -R parser:parser /home/parser/govparser
```

### 2. Настройка firewall
```bash
# Установка ufw
apt install ufw -y

# Разрешение SSH
ufw allow ssh

# Включение firewall
ufw enable
```

## Примерная стоимость

- **Yandex Cloud**: 300-500₽/мес
- **Timeweb**: 200-400₽/мес  
- **REG.RU**: 250-350₽/мес
- **DigitalOcean**: $5-10/мес (~350-700₽)

## Преимущества VPS

✅ **Работает 24/7** - парсер не останавливается  
✅ **Стабильный интернет** - нет проблем с подключением  
✅ **Российский IP** - лучший доступ к .ru сайтам  
✅ **Независимость** - не зависит от твоего компьютера  
✅ **Удаленное управление** - можешь управлять из любого места  

## Альтернативы

1. **Raspberry Pi** дома с постоянным питанием (~3000₽ единоразово)
2. **Старый компьютер/ноутбук** как домашний сервер
3. **GitHub Actions** (ограниченное время выполнения)
4. **Heroku** (платно, ~7$/мес)

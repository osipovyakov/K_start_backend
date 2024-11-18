## Установка и запуск проекта

### 1. Клонирование репозитория
Склонируйте репозиторий на ваш локальный компьютер:

```bash
git clone https://github.com/osipovyakov/K_start_backend.git
```

### 2. Установка зависимостей
Создайте виртуальное окружение и активируйте его:

```bash
py -3.9 -m venv venv
source venv/Scripts/activate
```

Затем установите зависимости:
```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных
Примените миграции:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Запуск сервера
Запустите локальный сервер:

```bash
python manage.py runserver
```

Теперь swagger доступен по адресу http://127.0.0.1:8000/swagger/

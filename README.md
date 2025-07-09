# 🍽️ Foodgram - Продуктовый помощник

Foodgram — это веб-приложение, позволяющее пользователям публиковать рецепты, добавлять их в избранное, формировать список покупок и делиться своими кулинарными идеями.

## 🚀 Стек технологий

- Python 3.9
- Django 3.2
- Django REST Framework
- PostgreSQL
- Docker, Docker Compose
- Nginx
- Gunicorn
- Djoser (аутентификация через токены)

---

### 5. Проект будет доступен по адресу:

```
https://foodgram-ads.servemp3.com
```

* Админ-панель: `https://foodgram-ads.servemp3.com/admin/`
* API документация: `https://foodgram-ads.servemp3.com/api/docs/`

---

## 📂 Структура проекта

```
🔹 backend/           # Код Django-приложения
🔹 frontend/          # React-приложение
🔹 gateway/           # Конфиги Nginx
🔹 docs/              # Документация API
🔹 docker-compose.production.yml
🔹 README.md
```

---

## 🔑 Основные возможности

* Регистрация и аутентификация пользователей
* Подписки
* CRUD рецептов
* Добавление рецептов в избранное
* Формирование списка покупок
* Фильтрация рецептов по тегам
* Загрузка изображений для рецептов
* Управление пользователями и контентом через админ-панель

---

## 🛡️ Авторизация

* Для получения токена:
  * POST `https://foodgram-ads.servemp3.com/api/auth/token/login/`

---

## 🔍 Документация API

Доступна по адресу:

```
http://https://foodgram-ads.servemp3.com/api/docs/
```

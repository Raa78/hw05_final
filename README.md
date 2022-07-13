# Bloggers’ social network

## Описание проекта:
Cоциальную сеть для публикации личных дневников и постов.

Неавторизованные пользователи могут только просматривать посты.

Авторизованные пользователи могут:
* добавлять и редактировать свои посты;
* подписываться на других пользователей и удалять их из подписок;
* оставлять комментарии под постами.

## Технологии:
* Python 3.7
* Django 2.2


### Инструкция для запуска проекта:
- Клонируйте репозиторий
```
git clone git@github.com:Raa78/hw05_final.git
```
- Перейдите в папку с проектом
```
cd hw05_final
```
- В папке с проектом установите виртуальное окружение
Windows
```
python -m venv имя_виртуального_окружения
```
_например_
```
python -m venv venv
```

MacOS/Unix
```
python3 -m venv имя_виртуального_окуржения
```
_например_
```
python3 -m venv venv
```
- Активируйте виртуальное окружение
Windows
```
source venv/Scripts/activate
```

MacOS/Unix
```
source venv/bin/activate
```
_или_
```
. venv/bin/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Выполните миграции
```
python manage.py makemigrations
python manage.py migrate
```
- Перейдите в папку yatube_api и выполните команду
```
python manage.py runserver
```

### Автор проекта
Андрей Рубцов
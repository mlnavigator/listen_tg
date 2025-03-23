
Запуск через python
- Проверял на python3.10+ (возможно сработает и на более старых версиях)
- Создайте файл env в папке assets по примеру файла assets/env_example
- Данные API Telegram получите на [https://my.telegram.org/apps](https://my.telegram.org/apps)
    - Данные в разделе App configuration App api_id и App api_hash. 
- укажаите id группы Telegram в которую вам присылать отчет о найденных целевых сообщениях в переменной окружения TG_TARGET_GROUP_ID.
    - при указании id группы в TG_TARGET_GROUP_ID не используйте префикс "-" 
    - id групп и каналов в которых состоит учетная запись бота выводятся в консоль в начале при каждом запуске (id выводятся с префиксами "-" и "-100")
    - среди выведенных вы можете отобрать нужные id
- Выполните команду `python <path_to_folder>/listen.py`
- После запуска в консоли введите данные авторизации Телеграм
    - Номер телефона
    - Код пришедший от телеграм
    - пароль 2-х факторной авторизации, если у вас она есть
- После этого вы можете указанной выше командой (ее адаптацией для вашего случая)

Доп настройки
- Пример переменны окружения в файле assets/env_example
- Если надо слушать только целевые каналы:
    - задайте их id в файле assets/targets.txt в столбик - один id на одной строке
    - для групп id указывается с префиксом "-"
    - для каналов id указывается с префиксом "-100"
    - установите переменную окружения USE_ONLY_TARGETS=1
- Если надо логировать все обработанные сообщения: 
    - Установите переменную окружения USE_LOG_MESSAGES=1
    - Лог будет в файле assets/messages.txt

Если у вас не получится запустить через python (например старая ОС, конфликты окружения и пр.), то можно запустить через Docker.
Запускать надо в несколько шагов - сначала собрать и запустить контейнер интерактивно.
Затем уже запустить контейнер на постоянку

Собираем и настраиваем. Замените <path_to_folder> на путь к папке с проектом
```commandline
cd <path_to_folder>
docker build -t listen_tg .
docker run --name=listen_tg -v ./assets:/app/assets -it listen_tg /bin/bash
# после этого вы оказыаетесь в контейнере
# надо запустить проект и ввести данные от tg в консоли
python3 /app/listen.py
# На этом этапе вы можете посмотреть id выведенных групп и каналов и дозаполнить assets/env и assets/targets.txt
# прервите выполнение через ctrl + C и выйдите из контейнера. 
exit
# после этого можно удалить контейнер (все настроки в папке assets сохранятся, и запускать контейнер заново работать постоянно
docker rm listen_tg
docker run -d --restart=always -v ./assets:/app/assets --name=listen_tg listen_tg
```

Если вы на Linux то все команды докер может потребоваться вводить с sudo, если docker не настроен для работы под вашим пользователем

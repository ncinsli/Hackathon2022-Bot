# School bells v2 | Beller Bot | BridgeBell146

Система управления школьными звонками
Полностью управляется из Telegram
Этот бот - логическое продолжение репозитория https://github.com/school146/school-bells, частичная реализация TODO из README того репозитория. Бот позволяет сдвигать расписание, изменять длину любых уроков и перемен, менять расписание по json-файлу

## Запуск

```git clone https://github.com/school146/school-bells-v2/
pip3 install pyTelegramBotApi
pip3 install smbus2
pip3 install sqlite3
export BELLER_TOKEN=токен_своего_бота
screen -dmS bells python3 main.py
```
Если вы захотите использовать систему у себя в школе, следует изменить конфигурации администраторов, длины звонков по умолчанию и прочего - используйте файл configuration.py

## Команды

<Х> обозначает опциональность аргумента Х -- при отсутствии он запомлняется аргументом по умолчанию

Для не-администраторов доступна команда
**/get_timetable** - Расписание звонков 


Для администраторов доступны команды

**/ring <время в секундах>** - Вызвать звонок вручную

**/add_admin** - Добавить администратора

**/rm_admin** - Удалить администратора

**/pre_ring_edit** - Изменить интервал между предзвонком и основным звонком (в секундах)

**/lesson_duration** - Изменить длину уроков

**/lesson_duration** - Изменить длину уроков

**/break_duration** - Изменить длину перемен

**/break_duration** - Изменить длину перемен

**/shift dd.mm.yyyy +-(int)(min/h)** - Сдвинуть всё расписание

**/shift <dd.mm.yyyy> +-(int)(min/h)** - Сдвинуть всё расписание

**/resize dd.mm.yyyy lesson/break int +-int(h/min)** - Изменение длины конкретной перемены или конкретного урока в конкретный день (по правой границе)

    Пример: /shift 26.12.2022 +10min    Сдвинуть расписание 26-го декабря на 10 минут вперед 
            /shift -1h                  Сдвинуть расписание сегодня на час назад
    Пример: /resize 26.12.2022 break 1 +10min
            /resize 31.12.2022 lesson 2 -5min

**/resize <dd.mm.yyyy> lesson/break int +-int(h/min)** - Изменение длины конкретной перемены или конкретного урока в конкретный день (по правой границе)

    Пример: /resize 26.12.2022 break 1 +10min     Сделать первую перемену 26 декабря длиннее на 10 минут   
            /resize lesson 2 -5min                Сделать второй урок короче на пять минут

**/mute <dd.mm.yyyy> hh:mm** - Заглушить звонок, который должен произвенеть в заданное время

**/mute dd.mm.yyyy hh:mm** - Заглушить звонок, который должен произвенеть в заданное время

    Пример: /mute 01.12.2022 9:45      Заглушить звонок в 09:45 1 декабря 2022 года
            /mute 10:40**              Заглушить звонок в 10:40   

    Пример: /mute 01.12.2022 9:45** - Заглушить звонок в 9:45 1 декабря 2022 года

**/unmute <dd.mm.yyyy> hh:mm** - Действие, обратное **/mute**

**/unmute dd.mm.yyyy hh:mm** - Действие, обратное **/mute**

    Пример: /unmute 01.12.2022 9:45.     Убрать глушение с звонка в 09:45 1 декабря 2022 года
            /unmute 10:40**.             Убрать глушение с звонка в 10:40   

**/set_timetable** - Установка расписания из JSON

**/mute_all <dd.mm.yyyy>** - Заглушить все звонки на определенный день

**/unmute_all <dd.mm.yyyy>** - Убрать глушение со всех звонков на сегодняшний день

# Архитектура
main.py - Точка входа, обработчик команд с валидацией

timetable.middleware - промежуточный слой, группа функций, которые обрабатывают сообщения с командами по управлению расписанием, занимаются декомпозицией на аргументы и вызовом функций по управлению БД

admins.middleware - то же, но обрабатывает сообщения с командами по управлению привилегиями
 timetable.middleware - command text processors for timetable editing tools (/shift, /resize, /mute etc.)

timetable.(shifting, resizing...) - слой по управлению БД с информацией о расписании

admins.(edit, storage, validator etc.) - слой по управлению БД с информацией об адиминах
   timetable/(shifting, resizing, getting, setting etc.) - tools for SQL sync

daemon - Фоновый процесс, отвечающий за то, чтобы звонить по временамм из БД

Главный его метод, помимо run, -   
daemon.update(...) вызывается, когда расписание меняется во время работы, а так же на старте демона

configuration.py - статические переменные и конфигурационная информация

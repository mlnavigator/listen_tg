import os
import re
import json
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, Channel, PeerChat, PeerUser

from config import basedir, api_id, api_hash, target_group_id, use_log_messages, use_only_targets
from check_message import filter_is_nlp_offer

session_file_path = os.path.join(basedir, 'assets/session.session')

client = TelegramClient(session_file_path, api_id, api_hash)

target_group = None

sources = dict()

# Загрузка целевых каналов из файла
targets = []
try:
    with open(os.path.join(basedir, 'assets/targets.txt'), 'r') as fd:
        sources_raw = fd.read()

    for s in sources_raw.split('\n'):
        targets.append(s.split())
except Exception as e:
    print('Ошибка загрузки файла с целевыми каналами', e)
    print('Игнорируем список целевых каналов, слушаем все каналы')


def prepare_id(i):
    i = str(i)
    i = re.sub(r'^-100', '', i)
    i = re.sub(r'^-', '', i)
    return i


def cut_text(text, length=1000):
    """Обрезка текста до указанной длины"""
    text = str(text)
    if len(text) > length:
        text = text[:length]
        text += '...'
    return text


async def get_message_link(message):
    """Генерация ссылки на сообщение"""
    peer = message.peer_id
    if type(peer) is PeerChannel:
        contragent = await client.get_input_entity(message.peer_id.channel_id)
        contragent_id = re.sub(r'^-100', '', str(contragent.channel_id))
    elif type(peer) is PeerChat:
        contragent = await client.get_input_entity(message.peer_id.chat_id)
        contragent_id = re.sub(r'^-', '', str(contragent.chat_id))
    elif type(peer) is PeerUser:
        contragent = await client.get_input_entity(message.peer_id.user_id)
        contragent_id = str(contragent.user_id)
        return None
    else:
        return None

    try:
        channel = await client.get_entity(message.peer_id)
    except Exception as e:
        print(f"Ошибка при получении информации о канале: {e}")
        return None

    if isinstance(channel, Channel) and channel.username:
        link = f"https://t.me/{channel.username}/{message.id}"
    else:
        link = f"https://t.me/c/{contragent_id}/{message.id}"
    return link


async def send_to_target(text):
    """Отправка сообщения в целевую группу"""
    global target_group
    if target_group is None:
        target_group = await client.get_input_entity(target_group_id)
    # Если сообщение пустое, то пропускаем
    if not text.strip():
        return
    # отправка сообщения в целевую группу
    await client.send_message(target_group, text)


def filter_target(event) -> bool:
    # Проверяем, что сообщение не из личного сообщения
    if not str(event.chat_id).startswith('-'):
        return False
    # Проверяем, что сообщение из целевого канала
    if use_only_targets and len(targets) > 0:
        if str(event.chat_id) not in targets:
            return False
    # Проверяем, что сообщение не из целевой группы для репорта
    chat_id = prepare_id(event.chat_id)
    if str(chat_id) == str(target_group_id) or str(event.chat_id) == str(target_group_id):
        return False

    return True


@client.on(events.NewMessage)
async def handler(event):
    global sources

    if not filter_target(event):
        return

    message = event.message
    text = message.message or "[Нет текста]"

    link = await get_message_link(message)
    chat_id = prepare_id(event.chat_id)
    try:
        chat_title = event.chat.title if event.chat is not None else sources.get(chat_id, "Неизвестный источник")
    except Exception as e:
        print('Ошибка при получении названия канала', e)
        chat_title = "Неизвестный источник"

    msg = (f"[{message.date}]\n"
           f"Message ID: {message.id}\n"
            f"Источник: {chat_title} (ID: {event.chat_id})\n"
            f"Сообщение:\n{cut_text(text, 2000)}\n"
            f"Ссылка: {link}\n"
            f"{'=' * 40}\n")

    # Проверяем, что сообщение является предложением на NLP
    filter_result = filter_is_nlp_offer(text)
    filter_result_cut = dict()
    for k,v in filter_result.items():
        filter_result_cut[k] = cut_text(str(v), 500)

    msg = '\n' + json.dumps(filter_result_cut, indent=4, ensure_ascii=False) + "\n\n" + msg

    if filter_result and 'is_ml_offer' in filter_result and filter_result['is_ml_offer']:
        print("Предложение на NLP обнаружено!")
        await send_to_target(msg)

    print(msg)

    if use_log_messages:
        # Сохраняем в файл
        with open(os.path.join(basedir, 'assets/messages.txt'), 'a', encoding='utf-8') as f:
            f.write(msg)


async def get_info():
    global sources
    """Вспомогательная функция для отладки"""
    me = await client.get_me()
    print(f"Аккаунт: {me.username} (ID: {me.id})")

    print("\nДоступные диалоги:")
    async for dialog in client.iter_dialogs():
        # print(dialog.name, dialog.id)
        # continue
        if str(dialog.id).startswith('-'):
            print(f"{dialog.name} -> ID: {dialog.id}")
            s_id = re.sub('^-100', '', str(dialog.id))
            s_id = re.sub('^-', '', s_id)
            sources[s_id] = dialog.name


if __name__ == '__main__':
    print('log_file:', os.path.join(basedir, 'messages.txt'))
    with client:
        # Запуск отладочной информации и формирование списка источников
        client.loop.run_until_complete(get_info())
        print("\nНачало мониторинга...")
        client.run_until_disconnected()

# -*- coding: utf-8 -*-
import random
from time import sleep

import redis
import telegram

from pikabu import Api

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2


class Bot(object):
    def __init__(self, token, redis_host=None, redis_port=None):
        if token is None:
            raise Exception(u'Необходимо задать токен')
        self.default_cache_time_expire = 4 * 60 * 60
        try:
            self.redis_cache = redis.StrictRedis(host=redis_host if redis_host is not None else 'localhost',
                                                 port=redis_port if redis_port is not None else '6379')
            self.redis_cache.get('test')
        except Exception as ex:
            self.redis_cache = None
            print ex.message
        self.default_cache_time_expire = 4 * 60 * 60
        self.pikabu_api = Api()
        self.bot = telegram.Bot(token)

    def startStandalone(self):
        # get the first pending update_id, this is so we can skip over it in case
        # we get an "Unauthorized" exception.
        try:
            update_id = self.bot.getUpdates()[0].update_id
        except IndexError:
            update_id = None

        while True:
            try:
                for update in self.bot.getUpdates(offset=update_id, timeout=10):
                    # chat_id is required to reply to any message
                    update_id = update.update_id + 1
                    self._handleUpdate(update)
            except telegram.TelegramError as e:
                # These are network problems with Telegram.
                if e.message in ("Bad Gateway", "Timed out"):
                    sleep(1)
                elif e.message == "Unauthorized":
                    # The user has removed or blocked the bot.
                    update_id += 1
                else:
                    raise e
            except URLError as e:
                # These are network problems on our end.
                sleep(1)

    def setWebhook(self, host, path, cert=None):
        self.bot.setWebhook(('%s/%s' % (host, path)), certificate=cert)

    def resetWebhook(self):
        self.bot.setWebhook()

    def dispatchMessage(self, json):
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(json)
        self._handleUpdate(update)

    def _handleUpdate(self, update):
        chat_id = update.message.chat.id
        # Telegram understands UTF-8, so encode text for unicode compatibility
        text = update.message.text.encode('utf-8')
        if text is not None and text.startswith('/'):
            text = text.lower()
            if text == '/start':
                self._handleStartCommand(chat_id, text)
            elif text == '/top':
                self._handleTopCommand(chat_id, text)
            elif text == '/random':
                self._handleRandomCommand(chat_id, text)
            elif text.startswith('/tag'):
                self._handleTagCommand(chat_id, text)
            else:
                self._handleUnknownCommand(chat_id, text)
        else:
            self._handleMessage(chat_id, text)

    def _handleStartCommand(self, chat_id, text):
        hello_text = u'*Список команд бота:*\n \
                       /start - команды бота\n \
                       /top - три лучших поста на данный момент\n \
                       /random - случайный пост\n \
                       /tag _<имя>_ - случайный пост с тегом _<имя>_'
        self.bot.sendMessage(chat_id=chat_id, text=hello_text, parse_mode=telegram.ParseMode.MARKDOWN)

    def _handleTopCommand(self, chat_id, text):
        posts = self._get_cache('/hot', 0)
        if posts is None:
            self.bot.sendMessage(chat_id=chat_id,
                                 text=u'Возникла ошибка и запрос не может быть обработан %s' % telegram.Emoji.CONFUSED_FACE)
        else:
            l = len(posts) if len(posts) < 3 else 3
            for i in range(l):
                self.bot.sendMessage(chat_id=chat_id, text=posts[i])

    def _handleRandomCommand(self, chat_id, text):
        self.bot.sendChatAction(chat_id, telegram.ChatAction.TYPING)
        paths = ['/hot', '/best', '/best/week', '/best/month', '/new']
        posts = self._get_cache_enh(paths[random.randint(0, len(paths) - 1)], 0, 4,
                                    6 * 60 * 60)  # Берем посты с 20 страниц и устанавливаем время кэша в 24 часа
        if posts is not None:
            self.bot.sendMessage(chat_id=chat_id, text=posts[random.randint(0, len(posts) - 1)])
        else:
            self.bot.sendMessage(chat_id=chat_id,
                                 text=u'Возникла ошибка и запрос не может быть обработан %s' + telegram.Emoji.CONFUSED_FACE)

    def _handleTagCommand(self, chat_id, text):
        splits = text.split(' ')
        if len(splits) <= 1:
            self.bot.sendMessage(chat_id=chat_id,
                                 text=u'Необходимо указать имя тэга.\nПример: /tag длиннопост')
        else:
            tag_name = ('%20'.join(splits[1:])).decode('utf-8')
            self.bot.sendChatAction(chat_id, telegram.ChatAction.TYPING)
            posts = self._get_cache_enh(u'/search.php?t=%s' % tag_name, 0, 4,
                                        24 * 60 * 60)  # Берем посты с 4 страниц с временем кэша 24 часа
            if posts is not None:
                self.bot.sendMessage(chat_id=chat_id, text=posts[random.randint(0, len(posts) - 1)])
            else:
                self.bot.sendMessage(chat_id=chat_id,
                                     text=u'Нет постов с таким тегом')
                self.bot.sendMessage(chat_id=chat_id,
                                     text=telegram.Emoji.CONFUSED_FACE)

    def _handleUnknownCommand(self, chat_id, text):
        self.bot.sendMessage(chat_id=chat_id,
                             text=u'Я не знаю такой команды %s' % telegram.Emoji.CONFUSED_FACE.decode('utf-8'))
        # self.sendMessage(chat_id=chat_id, text=telegram.Emoji.CONFUSED_FACE)

    def _handleMessage(self, chat_id, text):
        pass

    def _handleError(self, chat_id, text):
        print(text)

    # Извлечение кэша. Если кэш присутствует, то используется он
    # В кэш кладутся посты для раздела начиная со страници page определенного количетсва
    # Если кэш просрочен или отсусттвует - то он берется с сайта
    def _get_cache_enh(self, path, page, pages_count, expire_time=None):
        key = u'%s%d-%d' % (path, page, pages_count)
        value = self.redis_cache.get(key) if self.redis_cache is not None else None
        if value is None:
            posts = list()
            for p in range(0, pages_count):
                response = self.pikabu_api.get_posts_urls(path, page + p)
                if response.ok:
                    [posts.append(post) for post in response.posts]
            if len(posts) > 0:
                if self.redis_cache is not None:
                    self.redis_cache.set(key, ' '.join(response.posts), expire_time)
                return response.posts
            else:
                if self.redis_cache is not None:
                    self.redis_cache.delete(key)
                return None
        else:
            return value.split(' ')

    # Извлечение кэша. Если кэш присутствует, то используется он
    # Если кэш просрочен или отсусттвует - то он берется с сайта
    def _get_cache(self, path, page, expire_time=None):
        return self._get_cache_enh(path, page, 1, expire_time)

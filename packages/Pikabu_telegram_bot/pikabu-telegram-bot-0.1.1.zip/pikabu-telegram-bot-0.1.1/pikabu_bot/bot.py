# -*- coding: utf-8 -*-
import random

import redis
import telegram
from pikabu import Api


class Bot(object):
    def __init__(self, token, redis_host=None, redis_port=None):
        if token is None:
            raise Exception(u'Необходимо задать токен')
        self.default_cache_time_expire = 4 * 60 * 60
        try:
            self.redis_cache = redis.StrictRedis(host=redis_host if redis_host is not None else 'localhost',
                                                 port=redis_port if redis_port is not None else '6379')
        except Exception as ex:
            self.redis_cache = None
            print ex.message
        self.pikabu_api = Api()
        self.updater = telegram.Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.addTelegramCommandHandler('start', self.handleStartCommand)
        self.dispatcher.addTelegramCommandHandler('top', self.handleTopCommand)
        self.dispatcher.addTelegramCommandHandler('tag', self.handleTagCommand)
        self.dispatcher.addTelegramCommandHandler('random', self.handleRandomCommand)
        self.dispatcher.addUnknownTelegramCommandHandler(self.handleUnknownCommand)
        self.dispatcher.addTelegramMessageHandler(self.handleMessage)
        self.dispatcher.addErrorHandler(self.handleError)
        self.update_queue = None

    def startStandalone(self):
        self.updater.start_polling(poll_interval=0.1, timeout=10)

    def setWebhook(self, host, port, path, public_cert, cert_key):
        self.update_queue = self.updater.start_webhook(listen=host, port=port, url_path=path, cert=public_cert, key=cert_key)

    def resetWebhook(self):
        self.updater.start_webhook()

    def dispatchMessage(self, update):
        if self.update_queue:
            self.update_queue.put(update)

    def handleStartCommand(self, bot, update):
        hello_text = u'*Список команд бота:*\n \
                       /start - команды бота\n \
                       /top - три лучших поста на данный момент\n \
                       /random - случайный пост\n \
                       /tag _<имя>_ - случайный пост с тегом _<имя>_'
        bot.sendMessage(chat_id=update.message.chat_id, text=hello_text, parse_mode=telegram.ParseMode.MARKDOWN)

    def handleTopCommand(self, bot, update):
        posts = self.get_cache('/hot', 0)
        if posts is None:
            bot.sendMessage(chat_id=update.message.chat_id,
                            text=u'Возникла ошибка и запрос не может быть обработан %s' % telegram.Emoji.CONFUSED_FACE)
        else:
            l = len(posts) if len(posts) < 3 else 3
            for i in range(l):
                bot.sendMessage(chat_id=update.message.chat_id, text=posts[i])

    def handleRandomCommand(self, bot, update, args):
        bot.sendChatAction(update.message.chat_id, telegram.ChatAction.TYPING)
        paths = ['/hot', '/best', '/best/week', '/best/month', '/new']
        posts = self.get_cache_enh(paths[random.randint(0, len(paths) - 1)], 0, 4,
                                   6 * 60 * 60)  # Берем посты с 20 страниц и устанавливаем время кэша в 24 часа
        if posts is not None:
            bot.sendMessage(chat_id=update.message.chat_id, text=posts[random.randint(0, len(posts) - 1)])
        else:
            bot.sendMessage(chat_id=update.message.chat_id,
                            text=u'Возникла ошибка и запрос не может быть обработан %s' + telegram.Emoji.CONFUSED_FACE)

    def handleTagCommand(self, bot, update, args):
        if len(args) == 0:
            bot.sendMessage(chat_id=update.message.chat_id,
                            text=u'Необходимо указать имя тэга.\nПример: /tag длиннопост')
        else:
            tag_name = args[0]
            bot.sendChatAction(update.message.chat_id, telegram.ChatAction.TYPING)
            posts = self.get_cache_enh(u'/tag/%s/hot' % tag_name, 0, 4,
                                       24 * 60 * 60)  # Берем посты с 4 страниц с временем кэша 24 часа
            if posts is not None:
                bot.sendMessage(chat_id=update.message.chat_id, text=posts[random.randint(0, len(posts) - 1)])
            else:
                bot.sendMessage(chat_id=update.message.chat_id,
                                text=u'Возникла ошибка и запрос не может быть обработан ' + telegram.Emoji.CONFUSED_FACE)

    def handleUnknownCommand(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=u'Я не знаю такой команды')
        bot.sendMessage(chat_id=update.message.chat_id, text=telegram.Emoji.CONFUSED_FACE)

    def handleMessage(self, bot, update):
        pass

    def handleError(self, bot, update, error):
        print(error)

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
                    self.redis_cache.set(key, None)
                return None
        else:
            return value.split(' ')

    # Извлечение кэша. Если кэш присутствует, то используется он
    # Если кэш просрочен или отсусттвует - то он берется с сайта
    def _get_cache(self, path, page, expire_time=None):
        return self.get_cache_enh(path, page, 1, expire_time)

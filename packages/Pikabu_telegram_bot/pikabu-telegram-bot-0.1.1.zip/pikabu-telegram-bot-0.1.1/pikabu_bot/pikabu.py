# -*- coding: utf-8 -*-
import lxml.html

import re
import requests

_HTTP_URL_REGEXP = 'http[s]?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpg|gif|png)'
_URL_REQUESTER = requests.Session()


# Resolve html exception
class ResolveHtmlException(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code


# Post image content
class ContentImage:
    def __init__(self, url_image, url_preview_image, preview_image_width, preview_image_height):
        self.url_image = url_image
        self.url_preview_image = url_preview_image
        self.preview_image_width = preview_image_width
        self.preview_image_height = preview_image_height

    def serialize(self):
        return {'type': 'image',
                'url_image': self.url_image,
                'url_preview_image': self.url_preview_image,
                'preview_image_width': self.preview_image_width,
                'preview_image_height': self.preview_image_height}


# Post gif image content
class ContentGif:
    def __init__(self, url_gif, url_preview_image, preview_image_width, preview_image_height, gif_size):
        self.url_gif = url_gif
        self.url_preview_image = url_preview_image
        self.preview_image_width = preview_image_width
        self.preview_image_height = preview_image_height
        self.gif_size = gif_size

    def serialize(self):
        return {'type': 'gif',
                'url_gif': self.url_gif,
                'url_preview_image': self.url_preview_image,
                'preview_image_width': self.preview_image_width,
                'preview_image_height': self.preview_image_height,
                'gif_size': self.gif_size}


# Post video content
class ContentVideo:
    def __init__(self, url_video, url_preview_image, video_duration_seconds):
        self.url_video = url_video
        self.url_preview_image = url_preview_image
        self.video_duration_seconds = video_duration_seconds

    def serialize(self):
        return {'type': 'video',
                'url_video': self.url_video,
                'url_preview_image': self.url_preview_image,
                'video_duration_seconds': self.video_duration_seconds}


# Post text content
class ContentText:
    def __init__(self, text):
        self.text = text

    def serialize(self):
        return {'type': 'text',
                'text': self.text}


# Post item
class Post(object):
    def __init__(self, post_url, post_id, title, description, author, author_profile_url, is_points_visible,
                 points_count, comments_count, tags, is_erotic, content_list):
        self.url = post_url
        self.post_id = post_id
        self.title = title
        self.description = description
        self.author = author
        self.author_profile_url = author_profile_url
        self.is_points_visible = is_points_visible
        self.rating = points_count
        self.comments_count = comments_count
        self.tags = tags
        self.is_erotic = is_erotic
        self.content_list = content_list

    def serialize(self):
        return {'url': self.url,
                'post_id': self.post_id,
                'title': self.title,
                'description': self.description,
                'author': self.author,
                'author_profile_url': self.author_profile_url,
                'is_points_visible': self.is_points_visible,
                'rating': self.rating,
                'comments_count': self.comments_count,
                'tags': [tag for tag in self.tags],
                'is_erotic': self.is_erotic,
                'content_list': [x.serialize() for x in self.content_list]}


# Api response base class
class Response:
    def __init__(self, ok, message):
        self.ok = ok
        self.message = message


# Posts resolver response class
class PostsResolverResponse(Response):
    def __init__(self, ok, message, posts):
        Response.__init__(self, ok, message)
        self.posts = posts


# Function that resolve html
def _resolve_html(api, url, headers):
    _resp = _URL_REQUESTER.get(url=url, headers=headers)
    if _resp.status_code == 200:
        if not api.XCSRF_TOKEN:
            api.XCSRF_TOKEN = _URL_REQUESTER.cookies.get_dict()['PHPSESS']
        return _resp.text
    else:
        raise ResolveHtmlException('Wrong response code', _resp.status_code)


# Function that extract video content from lxml element
def _extract_video_content(html_element):
    _url_video = html_element.attrib['data-url']
    _url_preview_image = \
        re.findall(_HTTP_URL_REGEXP, html_element.xpath('''.//div[starts-with(@style,"background-image: url(")]''')[
            0].attrib['style'])[0]
    _video_duration = int(html_element.attrib['data-duration'])
    # _video_size_dirt = html_element.attrib['style'].split(';')
    # _preview_image_width = int(
    #     _video_size_dirt[1].replace("height: ", '').replace('px', ''))
    # _preview_image_height = int(
    #     _video_size_dirt[0].replace("height: ", '').replace('px', ''))
    return ContentVideo(_url_video, _url_preview_image, _video_duration)


# Function that extract gif content from lxml element
def _extract_gif_content(html_element):
    _gif_url = \
        html_element.xpath('''.//a[contains(@class, "b-gifx__save")]''')[0].attrib[
            'href']
    _preview_url = html_element.xpath('''.//img(@class="b-gifx__image")''')[0].attrib[
        'src']
    _preview_width = int(html_element.attrib['data-width'])
    _preview_height = int(html_element.attrib['data-height'])
    _gif_size_element = html_element.xpath('''.//div[@class="b-gifx__player"]''')[0]
    _gif_size = _gif_size_element.attrib[
        'data-size-gif'] if _gif_size_element is not None else ''
    return ContentGif(_gif_url, _preview_url, _preview_width, _preview_height,
                      _gif_size)


# Function that extract gif content from lxml element
def _extract_image_content(html_element):
    _image_element = html_element.xpath(".//img")[0]
    _url_image = _image_element.attrib['src']
    _url_large_image = _image_element.attrib['data-large-image'] if _image_element.attrib[
                                                                        'data-large-image'] is not None else _url_image
    try:
        _preview_width = _image_element.attrib['width']
    except Exception:
        try:
            _preview_width = _image_element.attrib['data-width']
        except Exception:
            _preview_width = 0

    try:
        _preview_height = _image_element.attrib['height']
    except Exception:
        try:
            _preview_height = _image_element.attrib['data-height']
        except Exception:
            _preview_height = 0
    return ContentImage(_url_large_image, _url_image, _preview_width, _preview_height)


# Function that extract text content from lxml element
def _extract_text_content(html_element):
    return ContentText(lxml.html.tostring(html_element).replace('<p><br></p>', ''))


def _safe_list_get(list, index, default):
    if len(list) == 0:
        return default
    else:
        return list[0]


# Posts resolver class
class PostsResolver:
    def __init__(self, api):
        self._api = api

    def resolve_urls(self, path, page=0):
        try:
            urls = list()
            _html = _resolve_html(self._api, self._api.ENDPOINT + path,
                                  headers=self._api.DEFAULT_HEADERS)
            # parse _html
            _body = lxml.html.fromstring(_html)
            _posts_body = _body.xpath("//table[starts-with(@id, 'inner_wrap_')]")
            for _pb in _posts_body:
                try:
                    _story_info_header = _pb.xpath('''.//td[@class="b-story__main-header"]''')[0]
                    _story_title_element = _story_info_header.xpath('div[2]/a')[0]
                    _post_href = _story_title_element.attrib['href']
                    urls.append(_post_href)
                except Exception as ex:
                    print ex.message
            return PostsResolverResponse(True, 'ok', urls)
        except ResolveHtmlException as ex:
            return Response(False, '%s %d' % (ex.message, ex.code))
        except Exception as ex:
            return Response(False, ex.message)

    def resolve(self, path, page=0):
        try:
            posts = list()
            _html = _resolve_html(self._api, self._api.ENDPOINT + path,
                                  headers=self._api.DEFAULT_HEADERS)
            # parse _html
            _body = lxml.html.fromstring(_html)
            _posts_body = _body.xpath("//table[starts-with(@id, 'inner_wrap_')]")
            for _pb in _posts_body:
                try:
                    _story_rating_text = _pb.xpath('''.//li[@class="b-rating__count"]''')[0].text.strip()
                    _story_info_header = _pb.xpath('''.//td[@class="b-story__main-header"]''')[0]
                    _story_title_element = _story_info_header.xpath('div[2]/a')[0]
                    _story_description_element = _safe_list_get(_story_info_header.xpath('.//div[@class="short"]'), 0,
                                                                None)
                    _story_author_element = _story_info_header.xpath('''.//a[starts-with(@href,\
                                                                        'http://pikabu.ru/profile')]''')[0]
                    _story_comments_element = _story_info_header.xpath('''.//a[contains(@class,'b-link')]''')[0]
                    _story_info_tags_elements = _story_info_header.xpath('''.//span[@class="tag no_ch"]''')
                    _story_erotic_element = _story_info_header.xpath('''.//a[@class="story_straw"]''')
                    _story_content_element = _safe_list_get(
                        _pb.xpath('''.//div[contains(@class,'b-story__content')]'''), 0, None)

                    _post_id = int(_pb.attrib['id'].replace('inner_wrap_', ''))
                    _post_is_erotic = len(_story_erotic_element) > 0
                    _post_rating_available = _story_rating_text.isdigit()
                    _post_rating = int(_story_rating_text) if _post_rating_available else 0
                    _post_href = _story_title_element.attrib['href']
                    _post_title = _story_title_element.text.strip()
                    _post_description = _story_description_element.text.strip() if _story_description_element is not None else ''
                    _post_author = _story_author_element.text.strip()
                    _post_author_href = _story_author_element.attrib['href']
                    _post_comments_count = int(_story_comments_element.text.split(' ')[0])
                    _post_tags = list()
                    [_post_tags.append(tag.text.strip()) for tag in _story_info_tags_elements]
                    _post_content = list()
                    # have to define type of post
                    # since pikabu posts has changed we have no post type,
                    # we just need to collect every media data in html
                    # such as images, gifs, video, text
                    if _story_content_element is not None:
                        if 'b-story-blocks' in _story_content_element.attrib['class']:  # composite post
                            _story_composite_wrapper = \
                                _story_content_element.xpath('''.//div[contains(@class,'b-story-blocks__wrapper')]''')[
                                    0]
                            for _child_element in _story_composite_wrapper.iterchildren():
                                if _child_element.tag == 'div':
                                    if 'b-story-block_type_image' in _child_element.attrib['class']:  # image
                                        _content_gif_element = _safe_list_get(
                                            _child_element.xpath('''.//div[@class='b-gifx']'''), 0, None)
                                        if _content_gif_element is None:  # static image
                                            _video_element = _safe_list_get(
                                                _child_element.xpath('''.//div[@class='b-video']'''), 0, None)
                                            if _video_element is None:  # image
                                                _post_content.append(_extract_image_content(_child_element))
                                            else:  # video
                                                _post_content.append(_extract_video_content(_video_element))
                                        else:  # gif image
                                            _post_content.append(_extract_gif_content(_content_gif_element))
                                    elif 'b-story-block_type_text' in _child_element.attrib['class']:  # text
                                        _post_content.append(_extract_text_content(_child_element.getchildren()[0]))
                                    elif 'b-story-block_type_video' in _child_element.attrib['class']:  # video
                                        _post_content.append(_extract_video_content(
                                            _child_element.xpath('''.//div[@class='b-video']''')[0]))
                                    elif 'b-story-blocks__hide-wrapper' in _child_element.attrib[
                                        'class']:  # visible content ends here
                                        pass
                        elif 'b-story__content_type_media' in _story_content_element.attrib['class']:  # media post
                            _content_gif_element = _safe_list_get(
                                _story_content_element.xpath('''.//div[@class='b-gifx']'''), 0, None)
                            if _content_gif_element is None:  # static image
                                _video_element = _safe_list_get(
                                    _story_content_element.xpath('''.//div[@class='b-video']'''), 0, None)
                                if _video_element is None:  # image
                                    _post_content.append(_extract_image_content(_story_content_element))
                                else:  # video
                                    _post_content.append(_extract_video_content(_video_element))
                            else:  # gif image
                                _post_content.append(_extract_gif_content(_content_gif_element))
                        elif 'b-story__content_type_text' in _story_content_element.attrib['class']:  # text post
                            _post_content.append(_extract_text_content(_story_content_element))
                    else:
                        raise Exception('No post content')
                    if len(_post_content) is 0:
                        raise Exception('No post content. Parsing problem')
                    post = Post(_post_href, _post_id, _post_title, _post_description,
                                _post_author, _post_author_href, _post_rating_available, _post_rating,
                                _post_comments_count, _post_tags, _post_is_erotic, _post_content)
                    posts.append(post)
                    # print post.serialize()
                    # print json.dumps(post.serialize())
                except Exception as ex:
                    print 'Parse exception for post %s (%d) %s' % (_post_title, _post_id, ex.message)
            if len(posts) == 0:
                raise Exception('No posts was downloaded')
            return PostsResolverResponse(True, 'ok', posts)
        except ResolveHtmlException as ex:
            return Response(False, '%s %d' % (ex.message, ex.code))
        except Exception as ex:
            return Response(False, ex.message)


# Api class
class Api:
    def __init__(self, username=None, password=None):
        # constants fields
        self.ENDPOINT = 'http://pikabu.ru'
        self.DEFAULT_HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) \
                          AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
            "Referer": "http://pikabu.ru/",
            "Host": "pikabu.ru",
            "Origin": "pikabu.ru"
        }
        self.AUTH_URL = self.ENDPOINT + 'ajax/ajax_login.php'
        self.XCSRF_TOKEN = None
        self.POST_HEADERS = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }
        # class dynamic fields
        self._logged = False
        self._username = username
        self._password = password
        self._posts_resolver = PostsResolver(self)

    def get_posts_urls(self, path, page=0):
        return self._posts_resolver.resolve_urls(path, page)

    def get_posts(self, path, page=0):
        return self._posts_resolver.resolve(path, page)

    def is_logged(self):
        return self._logged

    def authenticate(self):
        if self._logged:
            return Response(True)  # OK. Already logged
        # authenticate
        return Response(True)  # OK

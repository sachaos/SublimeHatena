#!/usr/bin/env python
# coding:utf-8

import sublime
import sublime_plugin

import json
import base64
import datetime
import hashlib
import random
import time
import urllib
import os
from xml.etree.ElementTree import fromstring

package_file = os.path.normpath(os.path.abspath(__file__))
package_path = os.path.dirname(package_file)

USER_AGENT = {'User-Agent': 'SublimeHatena/0.1'}

HATENA_SETTINGS = "Hatena.sublime-settings"

DEBUG = True

if DEBUG:
    def LOG(*args):
        print("SublimeHatena:", *args)
else:
    def LOG(*args):
        pass

############################################################
#               セッティング用
############################################################
def load_settings():
    settings = sublime.load_settings(HATENA_SETTINGS)
    if settings:
        LOG(settings.get("user_name"))
        return settings

############################################################
#               ポスト用
############################################################


TEMPLATE = """\
<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app">
  <title>{title}</title>
  <author><name>{name}</name></author>
  <content type="text/plain">{body}</content>
  <updated>{timestamp}</updated>
  {categories}
  <app:control>
    <app:draft>{draft}</app:draft>
  </app:control>
</entry>
"""

ARTICLE_HEADER = {
    "title": "",
    "name": "",
    "body": "",
    "timestamp": "",
    "categories": "",
    "draft": "no"
}


def make_categories_tag(categories):
    categories = map(lambda x: x.strip(), categories.split(","))
    category_tags = ""
    for category in categories:
        category_tags += '<category term="{}" />'.format(category)
    return category_tags


def parse_article_header(header_text):
    lines = header_text.strip().split("\n")
    article_header = ARTICLE_HEADER.copy()
    for line in lines:
        key, values = line.split(":")
        article_header[key.strip()] = values.strip()
    return article_header


def parse_article(article_text):
    if article_text.find("---") == 0:
        # extract header
        article_header_start = article_text.find("---") + 3
        article_header_end = article_text[3:].find("---") + 3
        article_header = article_text[article_header_start: article_header_end]
        # parse header
        article_information = parse_article_header(article_header)
        # extract body
        article_body_start = article_header_end + 3
        article_information["body"] = article_text[article_body_start:]
    else:
        article_information = ARTICLE_HEADER.copy()
        article_information["draft"] = "yes"
        article_information["body"] = article_text
    return article_information


def make_xml(article_info):
    article_info["categories"] = make_categories_tag(article_info["categories"])
    made_xml = TEMPLATE.format(**article_info)
    return made_xml


def create_wsse(username, password):
    # """X-WSSEヘッダの内容を作成
    # ユーザネームとAPIキーからWSSE認証用文字列を作成し、返します。
    # Args:
    #     @username: はてなID
    #     @password: はてなブログで配布されるAPIキー
    # Returns:
    #     WSSE認証用文字列
    # """

    # セキュリティトークン
    nonce = hashlib.sha1(str(time.time()).encode('utf-8') + str(random.random()).encode('utf-8')).digest()
    nonce = base64.b64encode(nonce).decode()
    # Nonceの作成時刻
    created = datetime.datetime.now().isoformat() + "Z"
    # PasswordDigest
    sha = hashlib.sha1((str(nonce)+created+password).encode("utf-8")).digest()
    digest = base64.b64encode(sha).decode()
    # WSSE認証用文字列として整形して返す
    return 'UsernameToken Username="{0}", PasswordDigest="{1}", Nonce="{2}", Created="{3}"'.format(username, digest, nonce, created)


def request_to_hatena(url, data, wsse):
    headers = {"X-WSSE": wsse}
    if data:
        data = data.encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        responce = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())
        responce = None
    return responce


def post_article(post_text):
    # account_settings.jsonからはてなアカウントを読み込み
    settings = load_settings()
    # テキストをパースして辞書に格納
    article_info = parse_article(post_text)
    # パースした辞書を元にXML文章をテンプレートに埋め込む
    article_xml = make_xml(article_info)
    # 送信先
    url = "http://blog.hatena.ne.jp/{0}/{1}/atom/entry".format(settings["user_name"], settings["blog_id"])
    # WSSE認証のための文字列をさくせい
    wsse = create_wsse(settings["user_name"], settings["api_key"])
    # リクエストを送る
    res = request_to_hatena(url, article_xml, wsse)
    if res:
        return True
    else:
        return False


class PostHatenaArticleCommand(sublime_plugin.WindowCommand):

    def run(self):
        view = self.window.active_view()
        view_text = view.substr(sublime.Region(0, view.size()))
        if post_article(view_text):
            sublime.status_message("SublimeHatena: The article has been posted correctly")
        else:
            sublime.status_message("SublimeHatena: Sorry, Error occured")


############################################################
#               記事作成用
############################################################

META_SNIPPET = """\
---
title: $1
categories:$2
---

$0

"""

# 既存のカテゴリーを取得(入力補完用)
def get_categories():
    # account_settings.jsonからはてなアカウントを読み込み
    settings = load_settings()
    # WSSE認証のための文字列を作成
    wsse = create_wsse(settings["user_name"], settings["api_key"])
    url = "https://blog.hatena.ne.jp/{0}/{1}/atom/category".format(settings["user_name"], settings["blog_id"])
    res = request_to_hatena(url, None, wsse)
    categories_xml = res.read()
    elem = fromstring(categories_xml)
    return map(lambda x: x.attrib["term"], elem.findall("*"))

class HatenaListener(sublime_plugin.EventListener):

    categories = get_categories()

    def on_query_completions(self, view, prefix, locations):
        loc = locations[0]
        if not view.scope_name(loc).startswith("text.html.markdown.hatena meta.metadata.hatena"):
            return None
        line = view.substr(view.line(loc)).lstrip()
        if line.startswith("categories"):
            complete_categories = [(category, category) for category in self.__class__.categories if category.startswith(prefix)]
            return complete_categories
        return None


# 新しいタブに記事のひな形を作成する。
class NewHatenaArticleCommand(sublime_plugin.WindowCommand):

    def run(self):
        view = self.window.new_file()
        view.set_syntax_file("Packages/SublimeHatena/Hatena.tmLanguage")
        view.set_status("SublimeHatena", "New Article has made")
        view.set_scratch(True)
        view.run_command("insert_snippet", {"contents": META_SNIPPET})
        sublime.set_timeout(lambda: view.run_command("auto_complete"), 10)

SublimeHatena
---

# これはなに？

SublimeText3からmarkdown記法で書かれたテキストを
はてなブログに投稿する為のプラグインです。

# なにがうれしいのか？

* SublimeTextで記事が書けてそのまま投稿できる。
* カテゴリーを補完できるのが便利。
* SublimeTextだとmarkdownが書きやすいのでその恩恵を受ける事が出来る。

# 使い方

## インストール

```
$ cd {パッケージをおいてるところ}
$ git clone https://github.com/sachaos/SublimeHatena.git
```


## account_settings.jsonを用意する

こんな風にaccount_setting.jsonを書いて``{Sublime Textの場所}/Packages/SublimeHatena/``上においてください。

```
[
   {
       "user_name": "******",
       "blog_id": "******.hatenablog.com",
       "api_key": "*********" # ブログの詳細設定に書いている
   }
]
```

## command + shift + p

### Hatena: New empty article

新しい記事を作成します

### Hatena: Post this article

現在開いているタブをはてなブログに投稿します。
ヘッダがない場合、下書きとして投稿することになっています。

__どんな物でも投稿してしまうので気をつけてください！__

## ヘッダの情報の追加

初期では以下のようになっていますが、
要素を加える事が可能です。

```
---
title: 
categories:
---
```

例えば、

```
---
title: this is title
name: hogehoge # author を設定
categories:PHP, Composer
draft: yes # 下書きとして投稿する
---
```

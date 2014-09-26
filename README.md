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

## accountの設定をする

インストールするとアカウントの設定がなされていない場合、
packages/User/以下にSublimeHatena.sublime-settingsというファイルが自動的に作成されます。

JSON形式でユーザー名、ブログID、APIキー(はてなブログの詳細設定に記載されている)を書き込んでください。

```
{
    "user_name": "your_user_name",
    "blog_id": "your_blog_id.hatenablog.com",
    "api_key": "your_api_key"
}

```

コマンドパレットに以下のコマンドが出ていれば正常に登録できています。

![サンプル](http://i.gyazo.com/e1c1072c61f8f62362ad09e14a3b47d0.png)

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

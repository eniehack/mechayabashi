# mechayabashi

TwitterなどのSNSの投稿からマルコフ連鎖を用いて文章を生成するBot

## features

- 様々なinput
    - Twitter Archive(`.js`)
    - nitter RSS
- 様々なoutput
    - Discord bot
    - Misskey bot
    - CLI app
- W.I.P.: feedback from human reaction

## dependency

- poetry
- python

## install

1. `git clone & cd`
2. `poetry install`
3. `poetry run src/importer/*.py`: ベースとなるデータ（`.csv`）の作成
    - misskeyから取得する(W.I.P.): `poetry run src/importer/misskey.py`
    - nitterから取得する: `poetry run src/importer/nitter.py`
    - Twitterのアーカイブデータから取得する: `poetry run src/importer/twitter_archive.py`
4. `poetry run src/ngram.py`: `.csv`データからngramを作成しSQLiteデータベースを作成
5. 文章を作成
    - discord botの場合: `poetry run src/discord.py`
    - misskey botの場合: `poetry run src/misskey.py`
    - CLIの場合: `poetry run src/make_sentence.py`
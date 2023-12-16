# 概要
Jupyter Notebookでの静的解析をサポートする。  

 - flake8による静的解析
 - spellcheckerによるスペルチェック

[pycodestyle_magic](https://github.com/mattijn/pycodestyle_magic)ではstylecheckとflake8が使用できるが、現時点のcolabで正常に動作しなかったため[pycodestyle_magic](https://github.com/mattijn/pycodestyle_magic)を参考に実装した。  

## 利用方法
### 静的解析
#### 単一セルに対する静的解析
「%%flake8」セルマジックにより、指定のセル中のコードをflake8でチェックを行う。

```
%%flake8
a =   3
```

この場合、以下のような出力がされる

--max_line_lengthを使用することで行の最大文字するを指定できる

```
%%flake8 --max_line_length=256
```


--ignoreで特定の警告を除外できる。複数除外する場合はコンマで区切る

```
%flake8 --ignore=E501,W292
```

#### 複数セルに対する静的解析
「%flake8_on」ラインマジックと「%flake8_off」に挟まれたセルについてflake8の静的解析を行う  

flake8_onには--ignore, --max_line_lengthを指定可能である。　　

### スペルチェック
アルファベットに対してのみスペルチェックを行う

#### 単一セルに対するスペルチェック

```
%%spell_checker
b = "I have a penci."
```



外部ファイルに以下のような、ignore.txt

```
```


# 開発ドキュメント
## ビルド方法

```
flit build 
```

## テスト
## ローカルでのユニットテスト

```
ipython tests/test_notebook_static_analyzer.py
```


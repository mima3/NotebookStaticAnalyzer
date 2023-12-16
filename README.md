# 概要
Jupyter Notebookでの静的解析をサポートする。  

 - flake8による静的解析
 - spellcheckerによるスペルチェック

[pycodestyle_magic](https://github.com/mattijn/pycodestyle_magic)ではstylecheckとflake8が使用できるが、現時点のcolabで正常に動作しなかったため[pycodestyle_magic](https://github.com/mattijn/pycodestyle_magic)を参考に実装した。  

## 利用方法
Google Colaboratoryに[サンプルノート](colab/NotebookStaticAnalyzerTest.ipynb)をアップロードして動作を確認可能


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


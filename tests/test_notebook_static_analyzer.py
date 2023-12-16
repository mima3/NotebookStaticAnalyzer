import unittest
from IPython.testing.globalipapp import get_ipython
# tests/test_notebook_static_analyzer.py
import sys
import os
from unittest.mock import patch
from io import StringIO

# notebook_static_analyzer.py へのパスを追加
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from notebook_static_analyzer import load_ipython_extension  # noqa: E402


class TestMagicFunction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # IPythonインスタンスの取得
        cls.ip = get_ipython()
        # マジック関数をロード
        load_ipython_extension(cls.ip)

    def test_flake8で引数を指定しない(self):
        code = """a =   5
b = "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
print("test", a)
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell_magic('flake8', '', code)
            output = fake_out.getvalue()

            # 期待される出力と比較
            self.assertIn(
                '2 : 4 E222 multiple spaces after operator',
                output,
                "flake8のエラー結果が表示されていること")
            self.assertIn(
                '3 : 80 E501 line too long (166 > 79 characters)',
                output,
                "flake8のエラー結果が表示されていること")
            self.assertIn(
                'test 5',
                output,
                "コードが実行されていること")

    def test_flake8でignore引数を指定する(self):
        code = """a =   5
b = "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
print("test", a)
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell_magic('flake8', '--ignore=E222', code)
            output = fake_out.getvalue()

            # 期待される出力と比較
            self.assertNotIn(
                '2 : 4 E222 multiple spaces after operator',
                output,
                "無視したエラーは表示されないこと")
            self.assertIn(
                '3 : 80 E501 line too long (166 > 79 characters)',
                output,
                "flake8のエラー結果が表示されていること")
            self.assertIn(
                'test 5',
                output,
                "コードが実行されていること")

    def test_flake8でmax_line_length引数を指定する(self):
        code = """a =   5
b = "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
print("test", a)
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell_magic('flake8', '--max_line_length=255', code)
            output = fake_out.getvalue()

            # 期待される出力と比較
            self.assertIn(
                '2 : 4 E222 multiple spaces after operator',
                output,
                "無視したエラーは表示されないこと")
            self.assertNotIn(
                '3 : 80 E501 line too long (166 > 79 characters)',
                output,
                "flake8のエラー結果が表示されていること")
            self.assertIn(
                'test 5',
                output,
                "コードが実行されていること")

    def test_spell_checkerで引数を指定しない(self):
        code = """b = "I have a penci."
print(b)
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell_magic('spell_checker', '', code)
            output = fake_out.getvalue()
            self.assertIn(
                '2: penci',
                output,
                "スペルミスの検知")
            self.assertIn(
                '2: b',
                output,
                "スペルミスの検知")
            self.assertIn(
                '3: b',
                output,
                "スペルミスの検知")
            self.assertIn(
                'I have a penci.',
                output,
                "コードが実行されていること")

    def test_spell_checkerでignore_word_pathを指定した(self):
        code = """b = "I have a penci."
print(b)
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell_magic('spell_checker', '--ignore_word_path=tests/ignore_word_list.txt', code)
            output = fake_out.getvalue()
            self.assertNotIn(
                '2: penci',
                output,
                "無視した単語はスペルミスとして検知されないこと")
            self.assertIn(
                '2: b',
                output,
                "スペルミスの検知")
            self.assertIn(
                '3: b',
                output,
                "スペルミスの検知")
            self.assertIn(
                'I have a penci.',
                output,
                "コードが実行されていること")

    def test_spell_checkerでmin_lenを指定して1文字はスペルチェックしない(self):
        code = """b = "I have a penci."
print(b)
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell_magic('spell_checker', '--min_len=2', code)
            output = fake_out.getvalue()
            self.assertIn(
                '2: penci',
                output,
                "スペルミスの検知")
            self.assertNotIn(
                '2: b',
                output,
                "短い文字をスペルミスとしない")
            self.assertNotIn(
                '3: b',
                output,
                "短い文字をスペルミスとしない")
            self.assertIn(
                'I have a penci.',
                output,
                "コードが実行されていること")

    def test_spell_onとoffの確認(self):
        code = """b = "I have a penci."
print(b)
"""
        # spell_checker_onの前はスペルチェックしない
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell(code)
            output = fake_out.getvalue()
            self.assertNotIn(
                '1: penci',
                output,
                "無視した単語はスペルミスとして検知されないこと")
            self.assertNotIn(
                '1: b',
                output,
                "スペルチェックをしていないこと")
            self.assertNotIn(
                '2: b',
                output,
                "スペルチェックをしていないこと")
            self.assertIn(
                'I have a penci.',
                output,
                "コードが実行されていること")
        # spell_checker_onの後はスペルチェックする
        self.ip.run_line_magic('spell_checker_on', '--ignore_word_path=tests/ignore_word_list.txt')
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell(code)
            output = fake_out.getvalue()
            self.assertNotIn(
                '1: penci',
                output,
                "無視した単語はスペルミスとして検知されないこと")
            self.assertIn(
                '1: b',
                output,
                "スペルミスの検知")
            self.assertIn(
                '2: b',
                output,
                "スペルミスの検知")
            self.assertIn(
                'I have a penci.',
                output,
                "コードが実行されていること")
        # spell_checker_offの後はスペルチェックしない
        self.ip.run_line_magic('spell_checker_off', '')
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell(code)
            output = fake_out.getvalue()
            self.assertNotIn(
                '1: penci',
                output,
                "無視した単語はスペルミスとして検知されないこと")
            self.assertNotIn(
                '1: b',
                output,
                "スペルチェックをしていないこと")
            self.assertNotIn(
                '2: b',
                output,
                "スペルチェックをしていないこと")
            self.assertIn(
                'I have a penci.',
                output,
                "コードが実行されていること")

    def test_flake8_onとoffの確認(self):
        code = """a =   5
b = "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
print("test", a)
"""
        # flake8_onの前は静的解析を実施しない
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell(code)
            output = fake_out.getvalue()

            # 期待される出力と比較
            self.assertNotIn(
                '1 : 4 E222 multiple spaces after operator',
                output,
                "無視したエラーは表示されないこと")
            self.assertNotIn(
                '2 : 80 E501 line too long (166 > 79 characters)',
                output,
                "flake8を実施しない")
            self.assertIn(
                'test 5',
                output,
                "コードが実行されていること")

        # flake8_onののちは静的解析を実施する
        self.ip.run_line_magic('flake8_on', '--ignore=E222')
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell(code)
            output = fake_out.getvalue()

            # 期待される出力と比較
            self.assertNotIn(
                '1 : 4 E222 multiple spaces after operator',
                output,
                "無視したエラーは表示されないこと")
            self.assertIn(
                '2 : 80 E501 line too long (166 > 79 characters)',
                output,
                "flake8のエラー結果が表示されていること")
            self.assertIn(
                'test 5',
                output,
                "コードが実行されていること")
        # flake8_offののちは静的解析を実施しない
        self.ip.run_line_magic('flake8_off', '')
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.ip.run_cell(code)
            output = fake_out.getvalue()

            # 期待される出力と比較
            self.assertNotIn(
                '1 : 4 E222 multiple spaces after operator',
                output,
                "無視したエラーは表示されないこと")
            self.assertNotIn(
                '2 : 80 E501 line too long (166 > 79 characters)',
                output,
                "flake8を実施しない")
            self.assertIn(
                'test 5',
                output,
                "コードが実行されていること")


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)

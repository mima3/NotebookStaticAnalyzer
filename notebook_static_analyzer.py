"""
flake8とスペルチェックを行うためのマジック関数です。

%spell_checker_on
%flake8_on
a =    "i have a pencii"

spell check result...
2: pencii
flake8 ...
2 : 4 E222 multiple spaces after operator
"""

__version__ = '0.1'

import re
from spellchecker import SpellChecker
import tempfile
import subprocess
import json

from IPython.core.magic import register_cell_magic
from IPython.core.magic import register_line_magic
from IPython.core import magic_arguments
from IPython import get_ipython


class SpellCheckerWrapper():
    def __init__(self, ignore_word_path: str = None):
        self.spell = SpellChecker()
        if ignore_word_path:
            with open(ignore_word_path) as f:
                for word in f:
                    word = re.sub(r"\s+", "", word)
                    if not word:
                        continue
                    self.spell.word_frequency.add(word)

    def remove_non_alphabetic_chars(self, text: str):
        # 非アルファベット文字を空白に置換
        return re.sub(r'[^a-zA-Z\s]', ' ', text)

    def check_text(self, text, min_len: int = 1):
        text = self.remove_non_alphabetic_chars(text)
        lines = text.split('\n')
        line_cnt = 1
        result = []
        for line in lines:
            words = line.split()
            miss_spelled = self.spell.unknown(words)
            for word in miss_spelled:
                if len(word) < min_len:
                    # 短い文字についてはスペルミスとはしない
                    continue
                result.append({
                    'line': line_cnt,
                    'word': word
                })
            line_cnt += 1
        return result

    def check_file(self, file_path: str, min_len: int = 1):
        with open(file_path, 'r') as file:
            content = file.read()
            return self.check_text(content, min_len)


class SpellCheckerWatcher(object):
    def __init__(self, ip, min_len, offset, ignore_word_path):
        self.shell = ip
        self.offset = offset
        self.min_len = min_len
        self.ignore_word_path = ignore_word_path

    def auto_run_magic_spell(self, result):
        run_magic_spell(
            result.info.raw_cell,
            self.offset,
            self.min_len,
            self.ignore_word_path)
        if result.error_before_exec:
            print('Error before execution: %s' % result.error_before_exec)


class Flake8Watcher(object):
    def __init__(self, ip, offset, max_length, ignore_codes):
        self.shell = ip
        self.offset = offset
        self.max_length = max_length
        self.ignore_codes = ignore_codes

    def auto_run_magic_flake8(self, result):
        run_magic_flake8(
            result.info.raw_cell,
            self.offset,
            self.max_length,
            self.ignore_codes)
        if result.error_before_exec:
            print('Error before execution: %s' % result.error_before_exec)


spell_checker_vw = None
flake8_vm = None


def load_ipython_extension(ip):
    pass


def unload_ipython_extension(ip):
    pass


def run_magic_flake8(cell, offset, max_length, ignore_codes):
    """flake8 cell magic"""
    if cell.startswith(('!', '%%', '%')):
        return
    with tempfile.NamedTemporaryFile(mode='r+', delete=True) as f:
        # save to file
        f.write(cell)
        # make sure it's written
        f.flush()
        cmd_args = [
            'flake8',
            '--format=json'
        ]
        if max_length:
            cmd_args.append(f"--max-line-length={max_length}")
        if ignore_codes:
            cmd_args.append(f"--ignore={','.join(ignore_codes)}")
        cmd_args.append(f.name)
        result = subprocess.run(cmd_args, capture_output=True, text=True)
        result_json = json.loads(result.stdout)
        print("flake8 ...")
        for item in result_json[f.name]:
            print(f"{item['line_number']+offset} : {item['column_number']} {item['code']} {item['text']}")  # noqa: E501


def run_magic_spell(cell, offset, min_len, ignore_word_path):
    spell = SpellCheckerWrapper(ignore_word_path)
    with tempfile.NamedTemporaryFile(mode='r+', delete=True) as f:
        # save to file
        f.write(cell)
        # make sure it's written
        f.flush()
        result = spell.check_file(f.name, min_len)
        print('spell check result...')
        for item in result:
            print(f"{item['line'] + offset}: {item['word']}")


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    '--offset_line',
    '-o',
    help='set the line offset number.'
)
@magic_arguments.argument(
    '--min_len',
    '-l',
    help='set the minium character length.'
)
@magic_arguments.argument(
    '--ignore_word_path',
    '-i',
    help='set ignore word list path.'
)
@register_cell_magic
def spell_checker(line, cell):
    """当該セルのスペルチェックを行う"""
    ip = get_ipython()
    ip.run_cell(cell)

    args = magic_arguments.parse_argstring(spell_checker, line)
    min_len = 0
    if args.min_len:
        min_len = int(args.min_len)
    offset = 1
    if args.offset_line:
        offset = int(args.offset_line)
    run_magic_spell(cell, offset, min_len, args.ignore_word_path)


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    '--offset_line',
    '-o',
    help='set the line offset number.'
)
@magic_arguments.argument(
    '--min_len',
    '-l',
    help='set the minium character length.'
)
@magic_arguments.argument(
    '--ignore_word_path',
    '-i',
    help='set ignore word list path.'
)
@register_line_magic
def spell_checker_on(line):
    """以降、実行時にセルのスペルチェックを実施する"""
    global spell_checker_vw
    if not spell_checker_vw:
        ip = get_ipython()
        args = magic_arguments.parse_argstring(spell_checker_on, line)
        min_len = 0
        if args.min_len:
            min_len = int(args.min_len)
        offset = 0
        if args.offset_line:
            offset = int(args.offset_line)
        spell_checker_vw = SpellCheckerWatcher(
            ip,
            min_len,
            offset,
            args.ignore_word_path
        )
        spell_checker_vw.shell.events.register(
            'post_run_cell',
            spell_checker_vw.auto_run_magic_spell
        )
    else:
        print('already spell_checker is on.')


@register_line_magic
def spell_checker_off(line):
    """以降、実行時にセルのスペルチェックを実施しない"""
    global spell_checker_vw
    if not spell_checker_vw:
        print('not execute spell_checker_on')
    spell_checker_vw.shell.events.unregister(
        'post_run_cell',
        spell_checker_vw.auto_run_magic_spell
    )
    spell_checker_vw = None


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    '--offset_line',
    '-o',
    help='set the line offset number.'
)
@magic_arguments.argument(
    '--ignore',
    '-i',
    help='ignore option, comma separated errors'
)
@magic_arguments.argument(
    '--max_line_length',
    '-m',
    help='set the max line length'
)
@register_cell_magic
def flake8(line, cell):
    """当該セルの静的解析を実施する"""
    ip = get_ipython()
    ip.run_cell(cell)
    args = magic_arguments.parse_argstring(flake8, line)

    ignore_codes = []
    if args.ignore:
        ignore_codes = list(set(ignore_codes + args.ignore.split(',')))
    max_line_length = None
    if args.max_line_length:
        max_line_length = int(args.max_line_length)
    offset = 1
    if args.offset_line:
        offset = int(args.offset_line)
    run_magic_flake8(cell, offset, max_line_length, ignore_codes)


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    '--offset_line',
    '-o',
    help='set the line offset number.'
)
@magic_arguments.argument(
    '--ignore',
    '-i',
    help='ignore option, comma separated errors'
)
@magic_arguments.argument(
    '--max_line_length',
    '-m',
    help='set the max line length'
)
@register_line_magic
def flake8_on(line):
    """以降、実行時にセルの静的解析を実施する"""
    global flake8_vm
    if not flake8_vm:
        ip = get_ipython()
        args = magic_arguments.parse_argstring(flake8_on, line)
        ignore_codes = []
        if args.ignore:
            ignore_codes = list(set(ignore_codes + args.ignore.split(',')))
        max_line_length = None
        if args.max_line_length:
            max_line_length = int(args.max_line_length)
        offset = 0
        if args.offset_line:
            offset = int(args.offset_line)
        flake8_vm = Flake8Watcher(ip, offset, max_line_length, ignore_codes)
        flake8_vm.shell.events.register(
            'post_run_cell',
            flake8_vm.auto_run_magic_flake8
        )
    else:
        print('already flake8 is on.')


@register_line_magic
def flake8_off(line):
    """以降、実行時にセルの静的解析を実施しない"""
    global flake8_vm
    if not flake8_vm:
        print('not execute flake8_on')
    flake8_vm.shell.events.unregister(
        'post_run_cell',
        flake8_vm.auto_run_magic_flake8
    )
    flake8_vm = None

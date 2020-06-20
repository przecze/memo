#!/usr/bin/env python3
from cmd import Cmd
from bs4 import BeautifulSoup
import subprocess
import requests
import os
import sys
import argparse
from collections import defaultdict
from cmd import Cmd
from tempfile import NamedTemporaryFile
import io
from contextlib import redirect_stdout

class Tee(object):
    def __init__(self, target):
        self.target = target
        self.stdout = sys.stdout
    def write(self, data):
        self.target.write(data)
        self.stdout.write(data)

def do_add(inp):
    print("checking word ", inp)
    entries = requests.get(f'https://www.dwds.de/api/wb/snippet?q={inp}').json()
    urls = {e['url'].split('#')[0] for e in entries}
    meanings = []
    full_text = ""
    for word_page in urls:
        print(f"Parsing page {word_page}")
        soup = BeautifulSoup(requests.get(word_page).text, features="lxml")
        words = soup.findAll("h1", {"class":"dwdswb-ft-lemmaansatz"})
        buf = Tee(io.StringIO())
        with redirect_stdout(buf):
            for word in words:
                print()
                print('# ', word.text, ' #')
                grammar = word.find_next("span", {"class": "dwdswb-ft-blocktext"})
                print('(', grammar.text, ')')
                print("Meanings:")
                meanings_divs = word.find_next("div", {"class":"dwdswb-lesarten"})
                meanings_divs = meanings_divs.findAll("div", {"class":"dwdswb-lesart"}, recursive = False)
                for meaning_div in meanings_divs:
                    try:
                        meaning = meaning_div.find_next("span", {"class", "dwdswb-definition"}).text
                        print(f'[{len(meanings)+1}]: {meaning}')
                        meanings.append((word.text, grammar.text, meaning))
                    except AttributeError:
                        print("[*] (meaning without text)")
                print("===============")
            captured_output = buf.target.getvalue()
            full_text += captured_output
    if not meanings:
        print("No meanings to display!")
        return False
    while True:
        try:
            selection = input(f"Select (1-{len(meanings)}):")
            if ',' in selection:
                selection = selection.split(',')
            selected = [meanings[int(s)-1] for s in selection]
            break
        except IndexError:
            print("Wrong index. Try again.")
        except ValueError:
            print("Incorrect format. Try again.")

    # Group selected meanings by (word, grammar) pairs
    selected_by_words = defaultdict(list)
    for *wg, meaning in selected:
        selected_by_words[(*wg,)].append(meaning)

    for (word, grammar), meanings in selected_by_words.items():

        if len(meanings) > 1:
            meanings = '* '+'\n* '.join(meanings)
        else:
            [meanings] = meanings

        # Manual edit in vim
        with NamedTemporaryFile(mode='w+t', prefix='word_') as word_file, \
             NamedTemporaryFile(mode='w+t', prefix='grammar_') as grammar_file, \
             NamedTemporaryFile(mode='w+t', prefix='definition_') as meaning_file, \
             NamedTemporaryFile(mode='w+t', prefix='full_text_') as text_file:
            for f, contents in [(word_file, word),
                                (grammar_file, grammar),
                                (meaning_file, meanings),
                                (text_file, full_text)]:
                f.write(contents)
                f.flush()
            command = ' '.join(['vim', f'-c "lefta vsplit {grammar_file.name} | split {word_file.name} | split {meaning_file.name}"', text_file.name])
            subprocess.check_call(command, shell=True)
            def read_temp_file(temp_file):
                with open(temp_file.name) as f:
                    return f.read()
            word, grammar, meanings = map(read_temp_file, (word_file, grammar_file, meaning_file))
            
        # Send to memodrop
        with open("shared/entry.txt", "w") as f:
            print(word, file=f)
            print(grammar, file=f)
            print(meanings, file=f)
        subprocess.check_call(["docker-compose", "exec", "memodrop", "./add_memodrop.py"])

if __name__ == '__main__':
    while(True):
        try:
            a = input("Please provide a word: ")
        except KeyboardInterrupt:
            print()
            print("Bye!")
            break
        if a:
            try:
                do_add(a)
            except KeyboardInterrupt:
                print("Aborting...")

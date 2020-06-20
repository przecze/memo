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

def do_add(inp):
    print("checking word ", inp)
    entries = requests.get(f'https://www.dwds.de/api/wb/snippet?q={inp}').json()
    urls = {e['url'].split('#')[0] for e in entries}
    meanings = []
    for word_page in urls:
        print(f"Parsing page {word_page}")
        soup = BeautifulSoup(requests.get(word_page).text, features="lxml")
        words = soup.findAll("h1", {"class":"dwdswb-ft-lemmaansatz"})
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
    selected_by_words = defaultdict(list)
    for *word, meaning in selected:
        selected_by_words[(*word,)].append(meaning)
    for word, meanings in selected_by_words.items():
        with open("shared/entry.txt", "w") as f:
            print(word[0], file=f)
            print(word[1], file=f)
            print('* '+'\n* '.join(meanings), file=f)
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

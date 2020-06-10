#!/usr/bin/env python3
from cmd import Cmd
from bs4 import BeautifulSoup
import subprocess
import requests
import os
import sys
import argparse
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
            meanings_div = word.find_next("div", {"class":"dwdswb-lesarten"})
            meanings_list = meanings_div.findAll("div", {"class":"dwdswb-lesart"}, recursive = False)
            meaning_texts = [m.find_next("span", {"class", "dwdswb-definition"}).text for m in meanings_list]
            for m in meaning_texts:
                print(f'[{len(meanings)}]: {m}')
                meanings.append((word.text, grammar.text, m))
            print("===============")
    if not meanings:
        return False
    selection = input()
    selected = meanings[int(selection)]
    with open("shared/entry.txt", "w") as f:
        print(selected[0], file=f)
        print(selected[1], file=f)
        print(selected[2], file=f)
    subprocess.check_call(["docker-compose", "exec", "memodrop", "./add_memodrop.py"])

if __name__ == '__main__':
    while(True):
        a = input("Please provide a word: ")
        do_add(a)

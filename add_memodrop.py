#!/usr/bin/env python3
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memodrop.settings")
django.setup()
from cards.models import *
from categories.models import *

if __name__ == '__main__':
    with open("shared/entry.txt", "r") as f:
        lines = f.readlines()
    [word, grammar, definition] = lines
    # Definition as answer
    Card(category=Category.objects.get(name="German"),
         question=f"{word} (Bedeutung?)",
         hint=grammar,
         answer=definition).save()
    # Word as answer
    Card(category=Category.objects.get(name="German"),
         question=definition,
         hint=grammar,
         answer=word).save()
    # Grammar as answer
    Card(category=Category.objects.get(name="German"),
         question=f"{word} (Grammatik?)",
         hint=definition,
         answer=grammar).save()

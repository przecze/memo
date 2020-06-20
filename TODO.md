* Better searching for words:
  * Case insensitive
  * Ignore german symbols
  * Ignore declination
  * Allow typos
* Auto database backups
* Simplify setup
* Don't add grammar card for adjectives
* Handle verbs with empty grammar
* Refactor add.py into functions
* Use yaml for serialization. Idea:
```
word: "der Word goes here" 
grammar: "grammar goes here
meaning: >
 * This means sth
 * and also sth else
cards:
  - question: word
    note: "(Bedeutung ?)"
    hint: grammar
    answer: meaning
  - question: meaning
    answer: word
  - question: word
    note: "(Grammatik ?)"
    hint: meaning
    answer: grammar
```

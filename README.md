# bLaTheR
A very simple, one file, pure-Python predictive text generator, with few
external dependencies. This is not a serious tool; only an entertaining
diversion.

### About

bLaTheR is a simple travesty generator. It takes a text file (or files) and 
generates a travesty that has the same statistical properties as the
input: same vocabulary, same average sentence length. Whatever you want
to measure about the input will be the same in the output. 

Note that this program is unaware of grammar, parts of speech, sentence
patterns, nor any of the other attributes of textual analysis that make 
for higher quality travesties. It is a good example of the 80/20 rule, in
that it usually produces coherent output, and the improvements that can be
made would swell the code size by more than one order of magnitude.

### Execution
```bash
python blather.py [--size {percentage}] [--depth {int}] --input {filename}
```

The `--size` parameter defaults to `10`, meaning the travesty will be 10%
the size of the original. 

The `--depth` sets the number of words that it backtracks. When using short
texts as input, a `depth` of four or five is the max for interesting
results that do not simply reproduce large sections of the input. For input
texts in the 500,000 word range, a `depth` of 8 or 9 is good.

`--input` can be a wildcard filespec. If you are using `*.txt` as the input
you must remember to put the the filespec in single quotes to avoid `bash`
globbing it before the value is read by the program.

### Logging

bLaTheR uses Python's logging module, and creates a file named `blather.log` 
in `$PWD`.

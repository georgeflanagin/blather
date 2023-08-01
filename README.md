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

```
usage: 

blather [-h] [-b BLATHER] [-c 1,..,n ] [-d DEPTH] -i INPUT [-o OUTPUT] 
        [-Z SIZE] [--verbose VERBOSE]

What bLaTheR does, bLaTheR does best. Namely, bLaTheR.

optional arguments:
  -h, --help            show this help message and exit
  -b BLATHER, --blather BLATHER
                        Name of the output blather file.
  -c {1,..,n-2}, --cores Number of cores to use. Max is two less than the number 
                        present on the CPU.
  -d DEPTH, --depth DEPTH
                        Depth of the backtracking in the predictive text algorithm.
  -i INPUT, --input INPUT
                        Name of input file. Accepts wildcard file names.
  -o OUTPUT, --output OUTPUT
  -Z SIZE, --size SIZE  Size of the output as a percent of the original input
  --verbose VERBOSE     Set the logging level. Defaults to 10, which is DEBUG.
```

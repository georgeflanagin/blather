# bLaTheR
A very simple, one file, pure-Python predictive text generator, with no
external dependencies. As a demonstration, it is entertaining.

### About
This is a one file, simple, predictive text generator. It takes a text file and 
generates a "travesty" that has the same statistical properties as the
input: same vocabulary, same average sentence length. Whatever you want
to measure about the input will be the same in the output. You might or might
not like the result.

Outside of entertainment, the only purpose might be testing.

Note that this program is unaware of grammar, parts of speech, sentence
patterns, nor any of the other attributes of textual analysis that make 
for higher quality travesties. It is a good example of the 80/20 rule, in
that it usually produces coherent output, and the improvements that can be
made would swell the code size by more than one order of magnitude.

### Execution
``` python blather.py -h
usage: bLaTheR [-h] [--fmt] -i INPUT [-o OUTPUT] [-d DEPTH] [-Z SIZE] [--verbose VERBOSE]

What bLaTheR does, bLaTheR does best. Namely, bLaTheR.

options:
  -h, --help            show this help message and exit
  --fmt                 Wrap/format the output to 70 columns.
  -i INPUT, --input INPUT
                        Name of input file.
  -o OUTPUT, --output OUTPUT
  -d DEPTH, --depth DEPTH
                        Depth of the backtracking in the predictive text algorithm.
  -Z SIZE, --size SIZE  Size of the output as a percent of the original input
  --verbose VERBOSE     Set the logging level. Defaults to 10
```

### Testing

Feed it some input and see what happens. It is only designed to work with 
text, and makes no attempt to verify that the input file _is_ text. 

### Performance

It is a single threaded program, so the performance is entirely the domain 
of your processor's clock speed. It does not do any math, and it only does
I/O at the beginning and end to read the input and write the output. 

Here is the 1.2 megabyte text of _Moby Dick_ being processed on an AMD Ryzen 9:

```
[bywords-new?][BillEvans(georgeflanagin):////blather]: /usr/bin/time -v python blather.py --depth 5 -i mobydick.txt 
Document sliced into 239530 slices.
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Writing blather to mobydick.txt.blather
	Command being timed: "python blather.py --depth 5 -i mobydick.txt"
	User time (seconds): 1.29
	System time (seconds): 0.09
	Percent of CPU this job got: 99%
	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:01.39
	Average shared text size (kbytes): 0
	Average unshared data size (kbytes): 0
	Average stack size (kbytes): 0
	Average total size (kbytes): 0
	Maximum resident set size (kbytes): 205648
	Average resident set size (kbytes): 0
	Major (requiring I/O) page faults: 0
	Minor (reclaiming a frame) page faults: 44826
	Voluntary context switches: 5
	Involuntary context switches: 15
	Swaps: 0
	File system inputs: 0
	File system outputs: 232
	Socket messages sent: 0
	Socket messages received: 0
	Signals delivered: 0
	Page size (bytes): 4096
	Exit status: 0

```


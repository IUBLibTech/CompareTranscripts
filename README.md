# CompareTranscripts
Tools to compare ASR transcripts with metrics

The `compare_transcripts` tool will load a reference transcript and one or
more hypothesis transcripts and compare them.  It supports loading text, webvtt,
whisper json, and json produced by 3play.  The file format is automatically
detected.

When running the comparison, the usual gang of statistics are produced:
* word error rate
* match error rate
* word information lost / word information preserved
* number of hits, substitutions, insertions and deletions

Additionally, it will try to detect these ASR issues:
* hallucinations - the addition of words which were not there
* dropouts - ignoring words that weren't there

## Transcript normalization
There are three places where the transcript content can be modified to provide
consistency between the different transcripts.

### Loading
When the transcript is loaded and converted into a list of words, the 
format-specific loader should remove anything that is specific to that format.

The loader classes take `strip_meta` and `strip_speaker` parameters to control
the removal of out-of-band information.

`strip_meta` will remove content which isn't actually spoken.  Description of
sounds or music, or other inserted metadata.

For example, in a 3play transcript there can be words surrounded by `[?` 
and `?]` tokens which indicate the transcriber was unsure of the text.  These
tokens are removed.  

`strip_speaker` will remove any speaker identification information that's in
the transcript text.

### Transformation
Since the editorial standards of each transcript may be different, there are
many phrases or words which may be different but mean the same thing.  Numbers
can be tricky, as well as currency

* $2
* two dollars

Are really the same thing but will mismatch since the transcripts are processed
on a word-by-word basis.  The above would consist of a substitution and an
insert.

During the transformation phase, list of transcript words can be passed to
different functions and they can alter the list as needed -- including adding an
removing words.  In the above example, the `currency` will modify `$2` into
`two dollars`.

Transformation functions should look at the transcription as a whole and make
what are effectively style changes.  

Slighly related, The Guardian uses (used?) regular expressions to verify the
writers were following the style guidelines:
https://www.theguardian.com/info/2021/jan/26/how-we-made-typerighter-the-guardians-style-guide-checker

This is similar behavior.

The result of the transformation becomes the canonical transcript text.

### Filtering

The filtering phase of the pipeline modifies single words to allow identical
words to match, even if they look different.  Removing punctuation characters
and case folding are two examples here.  

The word count should not be modified since these are word-for-word 
modifications



## The Comparison
At this point the text of the reference and the hypothesis should be normalized
in the same way.  The comparison uses jiwer to retrieve the "usual" statistics, 
but there are additional detections to find hallucinations and dropouts

### Hallucination / Dropout Detection

The hallucination and dropout detection is based on detecting runs of edits and
checking the length of the run and looking at the ratio of inserts (in the
case of hallucinations) or deletions (in the case of dropbouts) and comparing
it to a ratio.  Runs anchored at the beginning of the transcript, at the
end of the transcript, or in the middle of the transcript can use different
parameters.

The default settings are (percentages show, but 0.0 - 1.0 is used internally):
| Parameter                 | Hallucination | Dropout       |
|---------------------------|---------------|---------------|
| Primary edits for a run   | Inserts       | Deletions     |
| Other allowed edits       | Substitutions | Substitutions |
| Min Length (start)        | 2             | 2             |
| Primary Edit Ratio (start)| 100%          | 100%          |
| Min Length (mid)          | 4             | 4             |
| Primary Edit Ratio (mid)  | 100%          | 100%          |
| Min Length (end)          | 4             | 4             |
| Primary Edit Ratio (end)  | 100%          | 100%          |

Since the ratios are all 100%, any run of edits found must all be the
primary edit -- to be an hallucination at the end of the transcript it has to
be at least 4 words long and only consist of insertions.  

By lowering the ratio the number of hallucinations or dropbouts detected will 
likely increase since words that nearly matched an existing word and was treated 
as a substitution would be allowed.  


## Rendering
Once the comparison(s) have been computed, the results are rendered.  There are
three renderings available

In all renderings, the `--comparison-words` option on `compare_transcripts` or 
the `original_words` parameter in the rendering functions control whether 
the original word from the transcript (post-transformation) is shown or if 
the actual words compared are shown.

Examples of the renderings are in the `test/*/*.{html,txt,csv}` directory.


### HTML
The HTML rendering uses a Jinja2 template to format the results.  It is possible
to use a different template.  The usual statistics are reported as well as any
hallucinations or dropouts.  Edits relative to the reference transcript are 
displayed using a style similar to tracking edits in a text editor.

### Text
The text rendering also uses a Jinja2 template, which can be overridden by the
user.  The transcripts are reported linarly, and the edits are shown in 
three line triples indiating Reference transcript, Hypothesis transcript, and
Edits.

If the `--text-deferences` option is selected, only the lines which have
edits will be reported.

### CSV
The CSV format only records the statistics and doesn't show the edits



## Usage
The code can be used as a library for other tools or from the command line
using the `compare_transcripts` tool:

Obligitory help:
```
usage: compare_transcripts [-h] [--debug] 
    [--html-template HTML_TEMPLATE] 
    [--html-insert-class HTML_INSERT_CLASS] 
    [--html-delete-class HTML_DELETE_CLASS] 
    [--html-one-edit] 
    [--text-width TEXT_WIDTH] 
    [--text-differences]
    [--start-hallucination-length START_HALLUCINATION_LENGTH] 
    [--start-hallucination-ratio START_HALLUCINATION_RATIO] 
    [--mid-hallucination-length MID_HALLUCINATION_LENGTH]
    [--mid-hallucination-ratio MID_HALLUCINATION_RATIO] 
    [--end-hallucination-length END_HALLUCINATION_LENGTH] 
    [--end-hallucination-ratio END_HALLUCINATION_RATIO] 
    [--hallucination-length HALLUCINATION_LENGTH]
    [--hallucination-ratio HALLUCINATION_RATIO] 
    [--start-dropout-length START_DROPOUT_LENGTH] 
    [--start-dropout-ratio START_DROPOUT_RATIO] 
    [--mid-dropout-length MID_DROPOUT_LENGTH] 
    [--mid-dropout-ratio MID_DROPOUT_RATIO]
    [--end-dropout-length END_DROPOUT_LENGTH] 
    [--end-dropout-ratio END_DROPOUT_RATIO] 
    [--dropout-length DROPOUT_LENGTH] 
    [--dropout-ratio DROPOUT_RATIO] 
    --output OUTPUT [--output-format {html,txt,csv}]
    [--comparison-words]
    reference hypothesis [hypothesis ...]

positional arguments:
  reference             Reference transcript
  hypothesis            Hypothesis transcript(s)

options:
  -h, --help            show this help message and exit
  --debug               Enable debugging messages
  --html-template HTML_TEMPLATE
                        HTML template file
  --html-insert-class HTML_INSERT_CLASS
                        CSS class to use for insert text
  --html-delete-class HTML_DELETE_CLASS
                        CSS class to use for deleted text
  --html-one-edit       don't split the text for readability
  --text-width TEXT_WIDTH
                        Width for fixed width text output
  --text-differences    Only show the edit differences in text output
  --start-hallucination-length START_HALLUCINATION_LENGTH
                        Hallucination length at the start of the transcript
  --start-hallucination-ratio START_HALLUCINATION_RATIO
                        Ratio of inserts to total length of hallucination at the start of the transcript
  --mid-hallucination-length MID_HALLUCINATION_LENGTH
                        Hallucination length int he middle of the transcript
  --mid-hallucination-ratio MID_HALLUCINATION_RATIO
                        Ratio of inserts to total length of hallucination in the middle of the transcript
  --end-hallucination-length END_HALLUCINATION_LENGTH
                        Hallucination length at the end of the transcript
  --end-hallucination-ratio END_HALLUCINATION_RATIO
                        Ratio of inserts to total length of hallucination at the end of the transcript
  --hallucination-length HALLUCINATION_LENGTH
                        Set all of the hallucination lengths
  --hallucination-ratio HALLUCINATION_RATIO
                        Set all of the hallucination ratios
  --start-dropout-length START_DROPOUT_LENGTH
                        dropout length at the start of the transcript
  --start-dropout-ratio START_DROPOUT_RATIO
                        Ratio of inserts to total length of dropout at the start of the transcript
  --mid-dropout-length MID_DROPOUT_LENGTH
                        dropout length int he middle of the transcript
  --mid-dropout-ratio MID_DROPOUT_RATIO
                        Ratio of inserts to total length of dropout in the middle of the transcript
  --end-dropout-length END_DROPOUT_LENGTH
                        dropout length at the end of the transcript
  --end-dropout-ratio END_DROPOUT_RATIO
                        Ratio of inserts to total length of dropout at the end of the transcript
  --dropout-length DROPOUT_LENGTH
                        Set all of the dropout lengths
  --dropout-ratio DROPOUT_RATIO
                        Set all of the dropout ratios
  --output OUTPUT       Output file
  --output-format {html,txt,csv}
                        Output format (default guess from extension, html, txt, or csv)
  --comparison-words    Show comparison words instead of original words

```







# Environment Setup

## Linux  (maybe Mac and WSL too)
Create the virtual environment and install the libraries:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

NOTE: This was built on Fedora Linux 41 using Python 3.13.1.  I don't think
there is anything specific to 3.13, but I could be wrong.
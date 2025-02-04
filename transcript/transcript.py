import json
import logging
from pathlib import Path
import re
from typing import Self
import yaml

class Transcript:
    def __init__(self):
        self.type: str = None
        self.words: list[str] = []


    @staticmethod
    def load_file(file: Path) -> Self:
        """Load a transcript file"""
        for xscript_class in (ThreePlayTranscript, WhisperTranscript, TextTranscript):
            try:
                return xscript_class(file)                
            except Exception:
                logging.debug(f"Cannot load {file} as a {type(xscript_class)}")
        
        raise Exception("Cannot determine what kind of transcript this is!")                


    def strip_metawords(self):
        """Remove words which are not actually spoken.  Things like [Music]"""


    def strip_punctuation(self):
        """Remove punctuation characters from the beginning and end of the words"""




class TextTranscript(Transcript):
    """A transcript which is simply a text file"""
    def __init__(self, file: Path):
        self.type = "Text"
        with open(file) as f:
            for l in f.readlines():
                self.words.extend(l.strip().split())




class WhisperTranscript(Transcript):
    """A transcript in whisper json format
    We can identify this format by:
    * It's a JSON file (although IU sometimes stores them as YAML)
    * Keys:  
      * words:  string
      * segments: list
      * language: string 
    """
    def __init__(self, file: Path):
        with open(file) as f:
            data = yaml.safe_load(f)
        for k, dt in (('words', str), 
                      ('segments', list),
                      ('language', str)):
            if k not in data:
                raise KeyError(f"Not a whisper transcript, missing {k} key")
            if not isinstance(data[k], dt):
                raise KeyError(f"Not a whisper transcript Key {k} is not a {dt}")
            
        # looks good.  Grab all of the words
        self.type = "Whisper"
        for seg in data['segments']:
            for w in seg['words']:
                self.words.append(w['word'].strip())


class ThreePlayTranscript(Transcript):
    """A transcript in 3play json format
    We can identify this format by:
    * It's a JSON file
    * Keys:  
      * words:  list of lists
      * paragraphs: list of numbers
      * speakers: dict    
    """
    def __init__(self, file: Path):
        with open(file) as f:
            data = json.load(f)
        for k, dt in (('words', list), 
                      ('paragraphs', list),
                      ('speakers', dict)):
            if k not in data:
                raise KeyError(f"Not a 3play transcript, missing {k} key")
            if not isinstance(data[k], dt):
                raise KeyError(f"Not a 3play transcript, key {k} is not a {dt}")
            
        # looks good.  Grab all of the words
        self.type = "3Play"
        for _, w in data['words']:
            if w != '':
                self.words.append(w)




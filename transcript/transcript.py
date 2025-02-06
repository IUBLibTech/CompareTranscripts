import json
import logging
from pathlib import Path
import re
from typing import Any
import yaml

class Transcript:
    def __init__(self):
        self.type: str = None
        self.data: Any
        self.metadata: dict[str, Any] = {}

    @staticmethod
    def load_file(file: Path) -> 'Transcript':
        """Load a transcript file"""
        for xscript_class in (ThreePlayTranscript, WhisperTranscript, TextTranscript):
            try:
                t = xscript_class(file)         
                t.metadata['transcript_file'] = file.name
                return t
            except Exception as e:
                logging.debug(f"Cannot load {file} as a {type(xscript_class)}: {e}")
        
        raise Exception("Cannot determine what kind of transcript this is!")                


    def get_words(self, 
                  strip_meta: bool=True,
                  strip_speaker: bool=True) -> list[str]:
        """Get all of the individual words for a transcript, filtering some
        words out:
        * strip_meta will remove things like sound annotations, etc
        * strip_speaker will remove any inline speaker identification   
        """
        raise NotImplementedError()



class TextTranscript(Transcript):
    """A transcript which is simply a text file"""
    def __init__(self, file: Path):
        super().__init__()
        self.type = "Text"
        self.data = file.read_text().strip()


    def get_words(self, 
                  strip_meta: bool=True, 
                  strip_speaker: bool=True) -> list[str]:
        words = []
        for line in self.data.splitlines():
            if strip_speaker:
                line = re.sub(r'^[A-Z ]+:', ' ', line)
            if strip_meta:                
                line = re.sub(r'\[.*?\]', ' ', line)
            words.extend(line.split())
        return words


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
        super().__init__()
        with open(file) as f:
            data = yaml.safe_load(f)
        for k, dt in (('text', str), 
                      ('segments', list),
                      ('language', str)):
            if k not in data:
                raise KeyError(f"Not a whisper transcript, missing {k} key")
            if not isinstance(data[k], dt):
                raise KeyError(f"Not a whisper transcript Key {k} is not a {dt}")
                        
        # looks good.
        self.type = "Whisper"
        self.data = data

    def get_words(self, 
                  strip_meta: bool=True, 
                  strip_speaker: bool=True) -> list[str]:
        words = []
        for seg in self.data['segments']:
            if strip_meta:
                if re.match(r'\s*\[', seg['text']) or re.match(r'\s*\(\*', seg['text']):
                    # these are annotations.
                    continue
            # if timestamps were present, then we get a 'words key in the segment,
            # otherwise we just get the text.
            if 'words' in seg:
                seg_words = [x['word'] for x in seg['words']]
            else:
                seg_words = seg['text'].split()
            
            for w in seg_words:                
                if strip_meta:
                    w = w.replace('♪', '')
                w = w.strip()
                if w != '':
                    words.append(w)
        return words


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
        super().__init__()
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
        self.data = data
        

    def get_words(self, 
                  strip_meta: bool=True, 
                  strip_speaker: bool=True) -> list[str]:
        words = []
        for w in [x for x in self.data['words'] if x[1] != '']:
            if strip_speaker:
                if w[0] in self.data['speakers']:
                    w[1] = ''
            w = w[1]              
                        
            if strip_meta:
                w = re.sub(r'\[\?', ' ', w) # remove leading ambiguity marker
                w = re.sub(r'\?\]', ' ', w) # remove trailing ambituity marker
                w = re.sub(r'\[.*?\]', ' ', w) # remove sound annotation
                w = re.sub(r'</?i>', ' ', w) # remove the italic markers
                w = re.sub(r'\([A-Z\s]*\)', ' ', w)  # different style of sound notation 
            w = w.strip()
            if w != '':
                words.append(w)
        return words
        

from collections import namedtuple
import jiwer
import logging
from .transcript import Transcript

"""
Word edit is an edit for a transcript:  ref and hyp are the words that were
compared (or None if it was not present originally), edit is the type of edit 
(None, 'S', 'I','D'), and refword and hypword are the original transcript words
"""
WordEdit = namedtuple('WordEdit', ['ref', 'hyp', 'edit', 'refword', 'hypword'])


class Compare:
    """Generate comparison data for two transcripts"""
    def __init__(self, reference: list[str], hypothesis: list[str],
                 transforms: list[callable]=None,
                 filters: list[callable]=None):
        self.ref_words: list[str] = reference
        self.hyp_words: list[str] = hypothesis

        # run any transformations -- the result will become our offical
        # transcript
        if transforms:
            for t in transforms:
                self.ref_words = t(self.ref_words)
                self.hyp_words = t(self.hyp_words)

        # run the filters to make comparison easier.
        ref_words = self.ref_words
        hyp_words = self.hyp_words
        if filters:
            for f in filters:
                ref_words = f(ref_words)
                hyp_words = f(hyp_words)


        self.comp: dict = vars(jiwer.process_words(' '.join(ref_words), 
                                                   ' '.join(hyp_words)))

    
    def statistics(self) -> dict[str, float]:
        """Comparison statistics"""
        return {'wer': self.comp['wer'],
                'mer': self.comp['mer'],
                'wil': self.comp['wil'],
                'wip': self.comp['wip']}


    def edit_statistics(self) -> dict[str, float]:
        """Edit Statistics"""
        return {'hits': self.comp['hits'],
                'substitutions': self.comp['substitutions'],
                'insertions': self.comp['insertions'],
                'deletions': self.comp['deletions']}


    def edits(self) -> list[WordEdit]:
        """return a list WordEdits representing the edits between the transcripts."""

        # syncronize the original words.  
        rwords = " ".join(self.ref_words).split()
        hwords = " ".join(self.hyp_words).split()
        results = []
        for gt, hp, chunks in zip(self.comp['references'], self.comp['hypotheses'], self.comp['alignments']):            
            for chunk in chunks:
                if chunk.type in ('equal', 'substitute'):
                    # copy ref, and hyp words
                    t = None if chunk.type == 'equal' else 'S'
                    for i in range(chunk.ref_end_idx - chunk.ref_start_idx):                
                        results.append(WordEdit(gt[i + chunk.ref_start_idx],
                                                hp[i + chunk.hyp_start_idx],
                                                t,
                                                rwords[i + chunk.ref_start_idx],
                                                hwords[i + chunk.hyp_start_idx]))

                elif chunk.type == 'insert':
                    # hyp has an additional word that's not in ref.                
                    for i in range(chunk.hyp_end_idx - chunk.hyp_start_idx):                
                        results.append(WordEdit(None,
                                                hp[i + chunk.hyp_start_idx],
                                                'I',
                                                None,
                                                hwords[i + chunk.hyp_start_idx]))
                elif chunk.type == 'delete':
                    # ref has an additional word that's not in hyp.                
                    for i in range(chunk.ref_end_idx - chunk.ref_start_idx): 
                        results.append(WordEdit(gt[i + chunk.ref_start_idx],
                                                None,
                                                'D',
                                                rwords[i + chunk.ref_start_idx],
                                                None))

        return results



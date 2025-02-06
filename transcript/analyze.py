from transcript.compare import WordEdit

def find_hallucinations(edits: list[WordEdit],
                        start_length: int=2, start_ratio: float=1.0,
                        mid_length: int=4, mid_ratio: float=1.0,
                        end_length: int=4, end_ratio: float=1.0) -> list[list[WordEdit]]:
    """Find likely hallucinations based on runs of inserts.
    Hallucinations are searched in three different places:  the very beginning,
    the very end, and in the middle.

    Search the edits for an insert.  if the edit before it was a substitution
    back up one.  Move forward until there's a match or a delete.  If the
    distance is >= *_threshold AND the ratio of insert/subs is greater than 
    *_ratio, it is likely an hallucination.
    """
    results = []
    # first find the number of inserts or at the beginning of the transcripts.
    current = 0
    in_hallucination = False
    hallucination_start = 0
    for current, ed in enumerate(edits):
        if not in_hallucination:
            if ed.edit == 'I':
                # back up until there's an edit that isn't a substitution.
                hallucination_start = current
                in_hallucination = True
                while edits[hallucination_start - 1].edit == 'S':
                    hallucination_start -= 1
                    if hallucination_start == -1:
                        hallucination_start = 0
                        break                
        else:
            if ed.edit not in ('S', 'I') or current == len(edits) - 1:
                # this is the end of the hallucination.
                in_hallucination = False
                this_hallucination = [x for x in edits[hallucination_start:current]]                
                
                if hallucination_start == 0:
                    # use the start parameters
                    exp_ratio = start_ratio
                    exp_threshold = start_length
                elif current == len(edits) - 1:
                    # use the end parameters.
                    exp_ratio = end_ratio
                    exp_threshold = end_length
                else:
                    exp_ratio = mid_ratio
                    exp_threshold = mid_length

                if len(this_hallucination) >= exp_threshold:                    
                    insert_count = sum([1 for x in this_hallucination if x.edit == 'I'])
                    ratio = insert_count / len(this_hallucination)
                    if ratio >= exp_ratio:
                        results.append({'start': hallucination_start, 'edits': this_hallucination})

    return results


def find_dropouts(edits: list[WordEdit]):
    """Finding dropouts is similar to finding hallucinations.  Instead of looking
    for """




def find_runs(edits: list[WordEdit], 
                        start_length: int=2, start_ratio: float=1.0,
                        mid_length: int=4, mid_ratio: float=1.0,
                        end_length: int=4, end_ratio: float=1.0) -> list[list[WordEdit]]:
    """Find likely hallucinations based on runs of inserts.
    Hallucinations are searched in three different places:  the very beginning,
    the very end, and in the middle.

    Search the edits for an insert.  if the edit before it was a substitution
    back up one.  Move forward until there's a match or a delete.  If the
    distance is >= *_threshold AND the ratio of insert/subs is greater than 
    *_ratio, it is likely an hallucination.
    """
    results = []
    # first find the number of inserts or at the beginning of the transcripts.
    current = 0
    in_hallucination = False
    hallucination_start = 0
    for current, ed in enumerate(edits):
        if not in_hallucination:
            if ed.edit == 'I':
                # back up until there's an edit that isn't a substitution.
                hallucination_start = current
                in_hallucination = True
                while edits[hallucination_start - 1].edit == 'S':
                    hallucination_start -= 1
                    if hallucination_start == -1:
                        hallucination_start = 0
                        break                
        else:
            if ed.edit not in ('S', 'I') or current == len(edits) - 1:
                # this is the end of the hallucination.
                in_hallucination = False
                this_hallucination = [x for x in edits[hallucination_start:current]]                
                
                if hallucination_start == 0:
                    # use the start parameters
                    exp_ratio = start_ratio
                    exp_threshold = start_length
                elif current == len(edits) - 1:
                    # use the end parameters.
                    exp_ratio = end_ratio
                    exp_threshold = end_length
                else:
                    exp_ratio = mid_ratio
                    exp_threshold = mid_length

                if len(this_hallucination) >= exp_threshold:                    
                    insert_count = sum([1 for x in this_hallucination if x.edit == 'I'])
                    ratio = insert_count / len(this_hallucination)
                    if ratio >= exp_ratio:
                        results.append({'start': hallucination_start, 'edits': this_hallucination})

    return results
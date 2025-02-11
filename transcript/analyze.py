from transcript.compare import WordEdit
import logging

def find_hallucinations(edits: list[WordEdit],
                        start_length: int=2, start_ratio: float=1.0,
                        mid_length: int=4, mid_ratio: float=1.0,
                        end_length: int=4, end_ratio: float=1.0) -> list[list[WordEdit]]:
    """Hallucinations are runs which are primary inserts but can include substitutions"""
    return find_runs('I', edits, start_length, start_ratio,
                     mid_length, mid_ratio, end_length, end_ratio,
                     allowed_edits='S')


def find_dropouts(edits: list[WordEdit],
                  start_length: int=2, start_ratio: float=1.0,
                  mid_length: int=4, mid_ratio: float=1.0,
                  end_length: int=4, end_ratio: float=1.0):
    """Find dropouts by search for deletions but allow substitutions"""
    return find_runs('D', edits, start_length, start_ratio,
                     mid_length, mid_ratio, end_length, end_ratio,
                     allowed_edits='S')



def find_runs(primary_edit: str, edits: list[WordEdit], 
              start_length: int=2, start_ratio: float=1.0,
              mid_length: int=4, mid_ratio: float=1.0,
              end_length: int=4, end_ratio: float=1.0,
              allowed_edits: str | tuple = None) -> list[list[WordEdit]]:
    """Find runs of edits of a specific type, allowing other edits if specified.
    Once a run is found, compare it against the length and ratio of our target
    to overall length and if it passes, add it to the list.
    """
    if allowed_edits is None:
        allowed_edits = ()
    if isinstance(allowed_edits, str):
        allowed_edits = (allowed_edits,)

    all_edits = (primary_edit, *allowed_edits)

    results = []
    # first find the number of inserts or at the beginning of the transcripts.
    current = 0
    in_run = False
    run_start = 0
    for current, ed in enumerate(edits):
        if not in_run:
            if ed.edit == primary_edit:
                # back up until there's an edit that isn't a substitution.
                run_start = current
                in_run = True
                while edits[run_start - 1].edit in allowed_edits:
                    run_start -= 1
                    if run_start == -1:
                        run_start = 0
                        break                
        else:
            if ed.edit not in all_edits or current == len(edits) - 1:
                # this is the end of the hallucination.
                in_run = False
                this_run = [x for x in edits[run_start:current]]                
                
                if run_start == 0:
                    # use the start parameters
                    exp_ratio = start_ratio
                    exp_len = start_length
                elif current == len(edits) - 1:
                    # use the end parameters.
                    exp_ratio = end_ratio
                    exp_len = end_length
                else:
                    exp_ratio = mid_ratio
                    exp_len = mid_length

                if len(this_run) >= exp_len:                    
                    insert_count = sum([1 for x in this_run if x.edit == primary_edit])
                    ratio = insert_count / len(this_run)
                    if ratio >= exp_ratio:
                        results.append({'start': run_start, 'edits': this_run})
                    else:
                        logging.debug(f"Run discarded because {exp_ratio} > {ratio}: {this_run}")

    return results
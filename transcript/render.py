import html
from .compare import WordEdit, Compare


def pad_wordedit(wordedit: WordEdit) -> WordEdit:
    """Given a word edit pad all of the words so they have the same width"""
    ref, hyp, edit, refword, hypword = ['' if x is None else x for x in wordedit]    
    clen = max(len(ref), len(hyp))
    olen = max(len(refword), len(hypword))    
    ref = ref.ljust(clen)
    hyp = hyp.ljust(clen)
    refword = refword.ljust(olen)
    hypword = hypword.ljust(olen)
    if edit == '':
        edit = None
    return WordEdit(ref, hyp, edit, refword, hypword)
    

def fixed_width_text(edits: list[WordEdit], width=75, only_differences=False,
                     original_words=False) -> str:
    """Render the edits as fixed width text in groups of REF/HYP/CHG."""
    results = [{'ref': '', 'hyp': '', 'chg': '', 'dif': 0}]
    for edit in edits:
        edit = pad_wordedit(edit)
        rword = edit.refword if original_words else edit.ref
        hword = edit.hypword if original_words else edit.hyp
        wlen = len(rword)
        d = 0
        if edit.edit is None:
            ctext = ' ' * wlen
        elif edit.edit == 'S':
            ctext = 'S' * wlen
            d = 1
        elif edit.edit == 'I':
            ctext = 'I' * wlen
            rword = '*' * wlen
            d = 1
        elif edit.edit == 'D':
            ctext = 'D' * wlen
            hword = '*' * wlen
            d = 1

        if len(results[-1]['ref']) + len(ctext) > width:
            results.append({'ref': '', 'hyp': '', 'chg': '', 'dif': 0})

        results[-1]['dif'] += d
        results[-1]['ref'] += rword + " "
        results[-1]['hyp'] += hword + " " 
        results[-1]['chg'] += ctext + " "       

    if only_differences:
        results = [x for x in results if x['dif'] > 0]

    # render the differences as text.
    report = []
    for s in results:
        report.append(f"REF: {s['ref']}")
        report.append(f"HYP: {s['hyp']}")
        report.append(f"CHG: {s['chg']}")
        report.append("")        

    return "\n".join(report)


def html_difference(edits: list[WordEdit], original_words: bool=False,
                    insert_class='insert', delete_class='delete') -> str:
    """Render the text as html with <span> sections for the same/add/remove bits"""
    html_text = ""
    # go through the edits and change all of the None values for the words to 
    # an empty string.
    

    for edit in edits:        
        print(edit.refword, edit.hypword)
        rword = html.escape(edit.refword if original_words else edit.ref)
        hword = html.escape(edit.hypword if original_words else edit.hyp)
        if edit.edit is None:
            html_text += hword + " "
        elif edit.edit == 'S':
            html_text += f'<span class="{delete_class}">{rword}</span><span class="{insert_class}">{hword}</span> '
        elif edit.edit == 'I':
            html_text += f'<span class="{insert_class}">{hword}</span> '
        elif edit.edit == 'D':
            html_text += f'<span class="{delete_class}">{rword}</span> '

    return html_text

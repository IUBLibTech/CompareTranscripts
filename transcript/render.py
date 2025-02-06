import html
from .compare import WordEdit, Compare


def pad_wordedit(wordedit: WordEdit) -> WordEdit:
    """Given a word edit pad all of the words so they have the same width"""
    ref, hyp, edit, refword, hypword = wordedit    
    clen = max(len(ref), len(hyp))
    olen = max(len(refword), len(hypword))    
    ref = ref.ljust(clen)
    hyp = hyp.ljust(clen)
    refword = refword.ljust(olen)
    hypword = hypword.ljust(olen)
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
        if edit.edit == '':
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
                    insert_class: str='insert', delete_class: str='delete',
                    split_sentences: bool=False) -> str:
    """Render the text as html with <span> sections for the same/add/remove bits"""
    html_text = ""
    sentence_length = 0
    for edit in edits:        
        rword = html.escape(edit.refword if original_words else edit.ref)
        hword = html.escape(edit.hypword if original_words else edit.hyp)
        if edit.edit == '':
            html_text += hword + " "
        elif edit.edit == 'S':
            html_text += f'<span class="{delete_class}">{rword}</span><span class="{insert_class}">{hword}</span> '
        elif edit.edit == 'I':
            html_text += f'<span class="{insert_class}">{hword}</span> '
        elif edit.edit == 'D':
            html_text += f'<span class="{delete_class}">{rword}</span> '
        sentence_length += 1

        if split_sentences and sentence_length > 0 and edit.refword != '' and edit.refword.strip()[-1] in ('!', '.', '?'):
            html_text += (edit.refword.strip()[-1] if not original_words else '') + "<p>"
            sentence_length = 0

    return html_text

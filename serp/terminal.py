"""Plain terminal report, with no dashboard or terminal control sequences."""


def clean(value):
    return ''.join(c if c.isprintable() or c == '\n' else ' ' for c in str(value))


def render(report):
    lines = ['jev / intent triage', clean(report['disclaimer']), '']
    for index, row in enumerate(report['results'], 1):
        decision = row['decision']
        lines.extend([f"[{index:02}] {clean(row['query'])}",
                      f"  {clean(decision['route'])} | confidence {decision['confidence']:.2f}",
                      f"  {clean(row['title'])}", f"  {clean(row['snippet'])}",
                      f"  Page review required: {decision['requires_page_review']}", ''])
    lines.append(f"{len(report['results'])} results | mode={clean(report['mode'])}")
    return '\n'.join(lines)

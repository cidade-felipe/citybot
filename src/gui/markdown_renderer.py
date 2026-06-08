import math
import re
import tkinter as tk
from tkinter import font as tkfont
import webbrowser


INLINE_TOKEN_RE = re.compile(
    r'(`[^`\n]+`|\*\*\*[^*\n]+?\*\*\*|\*\*[^*\n]+?\*\*|'
    r'(?<!\*)\*[^*\n]+?\*(?!\*)|\[[^\]\n]+\]\([^)]+\))'
)
LINK_RE = re.compile(r'^\[([^\]]+)\]\(([^)]+)\)$')
HEADING_RE = re.compile(r'^(#{1,3})\s+(.+)$')
LIST_RE = re.compile(r'^(\s*)([-+*]|\d+[.)])\s+(.+)$')
TABLE_SEPARATOR_RE = re.compile(r'^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$')


def create_markdown_message(parent, text, fonts, colors, bg_color, fg_color, is_user=False):
    width = _estimate_width(text)
    height = _estimate_height(text, width)
    widget = tk.Text(
        parent,
        width=width,
        height=height,
        wrap='word',
        bg=bg_color,
        fg=fg_color,
        bd=0,
        relief='flat',
        highlightthickness=0,
        padx=0,
        pady=0,
        cursor='arrow',
        takefocus=0,
        font=fonts['text'],
        selectbackground=colors.get('accent_secondary', '#0099cc'),
        selectforeground=colors.get('text_primary', '#ffffff'),
    )
    _configure_tags(widget, fonts, colors, bg_color, fg_color, is_user)
    _render_markdown(widget, text)
    widget.configure(state='disabled')
    return widget


def _configure_tags(widget, fonts, colors, bg_color, fg_color, is_user):
    base = tkfont.Font(font=fonts['text'])
    mono = tkfont.Font(font=fonts.get('mono', fonts['text']))
    bold = _font_variant(base, weight='bold')
    italic = _font_variant(base, slant='italic')
    bold_italic = _font_variant(base, weight='bold', slant='italic')
    mono_bold = _font_variant(mono, weight='bold')
    heading_1 = _font_variant(base, size=base.actual('size') + 5, weight='bold')
    heading_2 = _font_variant(base, size=base.actual('size') + 3, weight='bold')
    heading_3 = _font_variant(base, size=base.actual('size') + 1, weight='bold')

    code_bg = '#d7f8ff' if is_user else '#111111'
    code_fg = colors.get('bg_primary', '#0f0f0f') if is_user else '#f4f4f4'
    link_fg = '#00384f' if is_user else colors.get('accent', '#00d4ff')
    quote_fg = '#12313a' if is_user else colors.get('text_secondary', '#b0b0b0')
    heading_fg = fg_color if is_user else colors.get('accent', fg_color)

    widget._markdown_fonts = [base, mono, bold, italic, bold_italic, mono_bold, heading_1, heading_2, heading_3]
    widget._markdown_link_color = link_fg

    widget.tag_configure('bold', font=bold)
    widget.tag_configure('italic', font=italic)
    widget.tag_configure('bold_italic', font=bold_italic)
    widget.tag_configure('inline_code', font=mono, background=code_bg, foreground=code_fg)
    widget.tag_configure(
        'code_block',
        font=mono,
        background=code_bg,
        foreground=code_fg,
        lmargin1=12,
        lmargin2=12,
        spacing1=4,
        spacing3=4,
    )
    widget.tag_configure('h1', font=heading_1, foreground=heading_fg, spacing1=8, spacing3=4)
    widget.tag_configure('h2', font=heading_2, foreground=heading_fg, spacing1=7, spacing3=3)
    widget.tag_configure('h3', font=heading_3, foreground=heading_fg, spacing1=6, spacing3=2)
    widget.tag_configure('list_marker', font=bold, foreground=fg_color)
    widget.tag_configure('quote', foreground=quote_fg, lmargin1=12, lmargin2=12)
    widget.tag_configure('rule', foreground=colors.get('border', '#333333'))
    widget.tag_configure('paragraph', spacing3=2)
    widget.tag_configure('link_url', foreground=link_fg)
    widget.tag_configure('table_header', font=mono_bold, spacing1=4)
    widget.tag_configure('table_row', font=mono, lmargin1=12, lmargin2=12)
    widget.tag_configure('table_rule', font=mono, foreground=colors.get('border', '#333333'), lmargin1=12)


def _font_variant(base, **changes):
    font = tkfont.Font(font=base)
    font.configure(**changes)
    return font


def _render_markdown(widget, text):
    lines = text.splitlines() or ['']
    in_code_block = False
    link_counter = [0]
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith('```'):
            in_code_block = not in_code_block
            index += 1
            continue

        if in_code_block:
            widget.insert('end', line.rstrip() + '\n', ('code_block',))
            index += 1
            continue

        if _starts_table(lines, index):
            index = _insert_table(widget, lines, index)
            continue

        if not stripped:
            widget.insert('end', '\n')
            index += 1
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            _insert_inline(widget, heading_match.group(2).strip(), (f'h{level}',), link_counter)
            widget.insert('end', '\n')
            index += 1
            continue

        if stripped in {'---', '***', '___'}:
            widget.insert('end', '-' * 48 + '\n', ('rule',))
            index += 1
            continue

        if line.lstrip().startswith('>'):
            quote_text = line.lstrip()[1:].strip()
            widget.insert('end', '| ', ('quote',))
            _insert_inline(widget, quote_text, ('quote',), link_counter)
            widget.insert('end', '\n')
            index += 1
            continue

        list_match = LIST_RE.match(line)
        if list_match:
            indent, marker, content = list_match.groups()
            visual_indent = ' ' * min(len(indent), 6)
            widget.insert('end', visual_indent + marker + ' ', ('list_marker',))
            _insert_inline(widget, content, ('paragraph',), link_counter)
            widget.insert('end', '\n')
            index += 1
            continue

        _insert_inline(widget, line, ('paragraph',), link_counter)
        widget.insert('end', '\n')
        index += 1

    _trim_final_newline(widget)


def _starts_table(lines, index):
    if index + 1 >= len(lines):
        return False

    return _is_table_row(lines[index]) and bool(TABLE_SEPARATOR_RE.match(lines[index + 1]))


def _is_table_row(line):
    stripped = line.strip()
    return stripped.startswith('|') and stripped.endswith('|') and stripped.count('|') >= 2


def _insert_table(widget, lines, start_index):
    header = _split_table_row(lines[start_index])
    body_rows = []
    index = start_index + 2

    while index < len(lines) and _is_table_row(lines[index]):
        body_rows.append(_split_table_row(lines[index]))
        index += 1

    rows = [header] + body_rows
    column_count = max((len(row) for row in rows), default=0)
    normalized_rows = [_normalize_table_row(row, column_count) for row in rows]
    widths = _table_widths(normalized_rows)

    widget.insert('end', _format_table_row(normalized_rows[0], widths) + '\n', ('table_header', 'table_row'))
    widget.insert('end', _format_table_rule(widths) + '\n', ('table_rule',))

    for row in normalized_rows[1:]:
        widget.insert('end', _format_table_row(row, widths) + '\n', ('table_row',))

    return index


def _split_table_row(line):
    stripped = line.strip().strip('|')
    return [cell.strip() for cell in stripped.split('|')]


def _normalize_table_row(row, column_count):
    return row + [''] * max(0, column_count - len(row))


def _table_widths(rows):
    return [
        max(len(_plain_cell(row[column])) for row in rows)
        for column in range(len(rows[0]))
    ]


def _format_table_row(row, widths):
    cells = [
        _plain_cell(cell).ljust(widths[index])
        for index, cell in enumerate(row)
    ]
    return '  '.join(cells).rstrip()


def _format_table_rule(widths):
    return '  '.join('-' * width for width in widths).rstrip()


def _plain_cell(text):
    text = re.sub(r'(\*\*\*|\*\*|\*)', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', text)
    return text


def _insert_inline(widget, text, base_tags, link_counter):
    position = 0
    base_tags = tuple(base_tags)

    for match in INLINE_TOKEN_RE.finditer(text):
        if match.start() > position:
            widget.insert('end', text[position:match.start()], base_tags)

        token = match.group(0)
        if token.startswith('`') and token.endswith('`'):
            widget.insert('end', token[1:-1], base_tags + ('inline_code',))
        elif token.startswith('***') and token.endswith('***'):
            widget.insert('end', token[3:-3], base_tags + ('bold_italic',))
        elif token.startswith('**') and token.endswith('**'):
            widget.insert('end', token[2:-2], base_tags + ('bold',))
        elif token.startswith('*') and token.endswith('*'):
            widget.insert('end', token[1:-1], base_tags + ('italic',))
        else:
            _insert_link_or_text(widget, token, base_tags, link_counter)

        position = match.end()

    if position < len(text):
        widget.insert('end', text[position:], base_tags)


def _insert_link_or_text(widget, token, base_tags, link_counter):
    match = LINK_RE.match(token)
    if not match:
        widget.insert('end', token, base_tags)
        return

    label, url = match.groups()
    tag_name = f'link_{link_counter[0]}'
    link_counter[0] += 1

    widget.tag_configure(tag_name, foreground=widget._markdown_link_color, underline=True)
    widget.tag_bind(tag_name, '<Button-1>', lambda _event, target=url: webbrowser.open(target))
    widget.tag_bind(tag_name, '<Enter>', lambda _event: widget.configure(cursor='hand2'))
    widget.tag_bind(tag_name, '<Leave>', lambda _event: widget.configure(cursor='arrow'))
    widget.insert('end', label, base_tags + (tag_name,))


def _trim_final_newline(widget):
    content = widget.get('1.0', 'end-1c')
    if content.endswith('\n'):
        widget.delete('end-2c', 'end-1c')


def _estimate_width(text, max_width=86):
    plain = _plain_for_size(text)
    longest = max((len(line.expandtabs(4)) for line in plain.splitlines()), default=0)
    return max(18, min(max_width, longest + 2))


def _estimate_height(text, width):
    plain = _plain_for_size(text)
    lines = plain.splitlines() or ['']
    total = 0
    for line in lines:
        length = max(1, len(line.expandtabs(4)))
        total += max(1, math.ceil(length / max(1, width)))
    return max(1, total)


def _plain_for_size(text):
    text = re.sub(r'```', '', text)
    text = re.sub(r'(\*\*\*|\*\*|\*)', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', text)
    text = re.sub(r'^#{1,3}\s+', '', text, flags=re.MULTILINE)
    return text

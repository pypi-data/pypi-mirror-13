from __future__ import unicode_literals

from math import ceil

from django import template
from django.core.urlresolvers import reverse

from nano.badge.models import Badge
from nano.tools import grouper

register = template.Library()

# \u25cf BLACK CIRCLE
# \u26ab MEDIUM BLACK CIRCLE (not as common)
SYMBOLS = {
    100: '\u25cf',
    200: '\u25cf',
    300: '\u25cf',
}

SYMBOL_NAMES = {
    100: 'bronze',
    200: 'silver',
    300: 'gold',
}

def sum_badges(user):
    levels = {}
    for badge in user.badges.all():
        levels[badge.level] = levels.setdefault(badge.level, 0) + 1

    return levels

def get_badges_for_user(user):
    inner_template = '<span class="b%i" title="%s %s badge%s">%s</span>%i'
    levels = sum_badges(user)
    sorted_levels = reversed(sorted(levels.keys()))
    badge_list = []
    for level in sorted_levels:
        name = SYMBOL_NAMES[level]
        symbol = SYMBOLS[level]
        num_levels = levels[level]
        plural = 's' if num_levels > 1 else ''
        badge_list.append(inner_template % (level, num_levels, name, plural, symbol, num_levels))
    return badge_list

@register.simple_tag
def show_badges(user):
    outer_template = '<span>%s</span>'

    badge_list = get_badges_for_user(user)

    if badge_list:
        return outer_template % '\xa0'.join(badge_list)
    return ''

@register.simple_tag
def show_badges_as_table(user, cols=4):
    outer_template = '<table>%s</table>'
    cell = '<td>%s</td>'
    row = '<tr>%s</tr>\n'
    single_col = '<tr><td>%s</td></tr>\n'

    badge_list = get_badges_for_user(user)

    if cols == 1:
        return [single_col % badge for badge in badge_list]
    elif cols > 1:
        piecesize = int(ceil(len(badge_list) / float(cols)))
        badge_lists = grouper(piecesize, badge_list)
        outer = []
        go_over = list(range(cols))
        for p in range(piecesize):
            inner = []
            for i in go_over:
                inner.append(cell % badge_list[i][p])
            outer.append(row % ''.join(inner))

    return outer_template % ''.join(outer)

@register.simple_tag
def show_badge(badge):
    if not badge: return ''
    template = '<span class="badge"><a href="%(link)s"><span class="b%(level)i" >%(symbol)s</span> %(name)s</a></span>'
    fillin = {
        'level': badge.level,
        'symbol': SYMBOLS[badge.level],
        'name': badge.name,
        'link': reverse('badge-detail', args=[badge.id]),
    }
    return template % fillin

@register.simple_tag
def show_badge_and_freq(badge):
    template = '<span class="badge-freq">%s (%i)</span>'
    badge_text = show_badge(badge)
    return template % (badge_text, badge.receivers.count())

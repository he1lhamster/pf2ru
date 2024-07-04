import gettext
import re

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

from routers.converters import convert_links, convert_to_traits, links_to_text, d_type, d_route
from users.auth.auth import current_user, current_user_optional


def trans(message: str, lang: str | None = 'en') -> str:
    try:
        return gettext.translation(
            "messages", localedir="locales", languages=[lang]
        ).gettext(message)
    except FileNotFoundError:
        return message


def lower_no_spaces(value: str) -> str:
    return value.lower().replace(' ', '-')


def replace_links(text: str) -> str:
    pattern = r'\[\[([^|\]]+)\|([^]]+)\]\]'
    matches: list = re.findall(pattern, text)

    for m in matches:
        link_addr, link_text = m
        link_type, link_id = link_addr.split('/')


def traits_to_text(text: str) -> str:
    if not text:
        return ""
    pattern = r'\[\[([^|\]]+)\|([^]]+)\]\]'
    matches = re.findall(pattern, text)
    new_text = ",".join([x[1] for x in matches])

    return new_text


action_dict = {
    '[one-action]': '1',
    '[two-actions]': '2',
    '[three-actions]': '3',
    '[free-action]': '4',
    '[reaction]': '5',
    # None: '-2'
}


def action_to_icon(value: str) -> str:
    if not value:
        return ""

    bracketed_text = re.findall(r"\[.*?\]", value)
    value = ''.join(bracketed_text)

    for x in action_dict:
        value = value.replace(x, f'<span class="action-icon">{action_dict[x]}</span>')
    return value


def action_to_value(value: str) -> str:
    if not value:
        return "-2"

    bracketed_text = re.findall(r"\[.*?\]", value)
    value = ''.join(bracketed_text)

    for x in action_dict:
        value = value.replace(x, f'{action_dict[x]}')
    return value


def price_to_val(value: str) -> float:
    if not value: return 0
    value = value.replace(',', '')
    value = value.split('(')[0]
    price_types = {
        "pp": 10,
        "gp": 1,
        "sp": 0.1,
        "cp": 0.01,
    }
    matches: list = re.findall(r'(\b\d+\s+(?:gp|sp|pp|cp)\b)', value)

    new_value = 0.0
    for m in matches:
        val, price_type = m.split(' ')
        new_value += int(val) * price_types[price_type]

    return round(new_value, 2)


def lvl_to_int(val: str) -> int:
    if val is None or val == '': return '-'
    val = val.split(' ')[-1].strip().strip('+')
    return int(val)


def none_to_hyphen(value: str) -> str:
    if value != 0 and (value is None or value == ''): return '-'
    return value


def to_list(value: str) -> str:
    return ", ".join([x for x in value.split(',')]) if value else "-"


def to_url(value: str) -> str:
    return d_type[value][0].lower() if value in d_type else value.lower()


def to_a_links(value: str) -> str:
    return convert_links(value)


def to_text(value: str) -> str:
    return links_to_text(value)


def to_traits_output(value: str) -> str:
    return convert_to_traits(value)


def viewbox_r(value):
    rendered = templates.env.from_string(value).render(viewbox=viewbox_macro)
    return convert_links(rendered)


def type_to_route(value):
    if value and value in d_type:
        return d_type[value][0]
    return None


def type_output(value, lang: str = 'en'):
    value = value.lower()
    if value and value in d_type:
        return d_type[value][3] if lang == 'ru' else d_type[value][2]
    return None


def type_to_rus(value):
    if value and value in d_type:
        return d_type[value][3]
    return None


def route_to_rus(value):
    if value and value in d_route:
        return d_type[d_route[value][0]][3]
    return None


async def NewTemplateResponse(name, context, *args, **kwargs):
    context.update({
        'trans': trans,
        'user': context['request'].state.user,
        # 'user': user,
    })
    return templates.TemplateResponse(name, context, *args, **kwargs)


templates = Jinja2Templates("templates")
templates.env.filters['lower_no_spaces'] = lower_no_spaces
templates.env.filters['action_to_icon'] = action_to_icon
templates.env.filters['action_to_value'] = action_to_value
templates.env.filters['to_url'] = to_url
templates.env.filters['to_a_links'] = to_a_links
templates.env.filters['to_text'] = to_text
templates.env.filters['to_traits_output'] = to_traits_output
templates.env.filters['price_to_val'] = price_to_val
templates.env.filters['lvl_to_int'] = lvl_to_int
templates.env.filters['traits_to_text'] = traits_to_text
templates.env.filters['none_to_hyphen'] = none_to_hyphen
templates.env.filters['to_list'] = to_list
templates.env.filters['type_to_route'] = type_to_route
templates.env.filters['type_to_rus'] = type_to_rus
templates.env.filters['route_to_rus'] = route_to_rus

templates.env.filters['type_output'] = type_output

templates.env.filters['viewbox_r'] = viewbox_r

templates.env.add_extension('jinja2.ext.i18n')
templates.env.globals['no_trans'] = lambda x: x + "==="

template_viewbox = templates.env.get_template("viewbox.html")
viewbox_macro = template_viewbox.module.viewbox

# def render_macros(value):
#     # Render the value containing macros
#     return templates.env.from_string(value).render(viewbox=viewbox_macro)

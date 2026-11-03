"""Stable `file=N` ordering for files in `config_template`.

`file=N` is a 1-based index into `list_templates()`. `PINNED_TEMPLATES` is the
order those files had when the directory was sorted by filename, plus
`config_1.14` appended at the end. New template files are added after this
prefix (sorted by name) so `file=1` through `file=6` keep pointing at the
same files.

A request that omits `file=` does not use index 0. It selects
`DEFAULT_TEMPLATE` by name.
"""

import os

PINNED_TEMPLATES = [
    "config_template_groups_rule_set_tun",       # file=1
    "config_template_groups_rule_set_tun_fakeip",  # file=2
    "config_template_no_groups_tun_VN",          # file=3
    "sb-config-1.12",                            # file=4
    "sb-config-1.14",                            # file=5
    "config_1.14",                               # file=6
]

# Used when the subscription URL has no `file=` parameter.
DEFAULT_TEMPLATE = "config_1.14"


def list_templates(template_dir="config_template"):
    try:
        files = os.listdir(template_dir)
    except FileNotFoundError:
        return []
    names = []
    for file in files:
        stem, ext = os.path.splitext(file)
        if ext == ".json":
            names.append(stem)
    present = set(names)
    ordered = [name for name in PINNED_TEMPLATES if name in present]
    ordered.extend(sorted(name for name in names if name not in PINNED_TEMPLATES))
    return ordered


def default_template_index(template_list=None, template_dir="config_template"):
    if template_list is None:
        template_list = list_templates(template_dir)
    if DEFAULT_TEMPLATE in template_list:
        return template_list.index(DEFAULT_TEMPLATE)
    return 0

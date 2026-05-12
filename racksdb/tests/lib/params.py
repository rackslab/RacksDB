# Copyright (c) 2026 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import functools
import re


def _normalize_case(case):
    if isinstance(case, tuple):
        return case
    return (case,)


def _slugify_case(case):
    text = "_".join(str(item) for item in _normalize_case(case))
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower()
    return slug or "case"


def expand_params(cases):
    def decorator(func):
        func._racksdb_expand_cases = list(cases)
        return func

    return decorator


def _make_expanded_test(func, args):
    @functools.wraps(func)
    def expanded(self):
        return func(self, *args)

    return expanded


def expand_parameterized_tests(cls):
    for name, value in list(vars(cls).items()):
        cases = getattr(value, "_racksdb_expand_cases", None)
        if cases is None:
            continue

        for index, case in enumerate(cases, start=1):
            args = _normalize_case(case)
            slug = _slugify_case(case)
            expanded_name = f"{name}_{index:03d}_{slug}"
            setattr(cls, expanded_name, _make_expanded_test(value, args))

        delattr(cls, name)

    return cls

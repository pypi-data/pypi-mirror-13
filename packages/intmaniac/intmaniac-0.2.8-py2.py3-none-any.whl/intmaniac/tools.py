#!/usr/bin/env python


def deep_merge(d0, d1):
    d = {}
    for k, v in d1.items():
        if type(v) == dict and k in d0 and type(d0[k]) == dict:
                d[k] = deep_merge(d0[k], v)
        else:
            d[k] = v
    for k, v in d0.items():
        if k not in d1:
            d[k] = v
    return d


if __name__ == "__main__":
    print("Don't do this :)")
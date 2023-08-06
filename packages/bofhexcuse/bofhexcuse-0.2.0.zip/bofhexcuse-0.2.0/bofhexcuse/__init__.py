import json
import os
import random
import re


__all__ = ['generate_excuse', 'bofh_excuse']


token_regex = re.compile('{(\w+)}')


def generate_excuse(excuse_dict, key='start'):
    """Generates a random excuse from a simple template dict.

    Based off of drow's generator.js (public domain).
    Grok it here: http://donjon.bin.sh/code/random/generator.js

    :param excuse_dict: Excuse template dict
    :type excuse_dict: dict
    :param key: Starting key to generate from
    :type key: str
    :return: Excuse string
    :rtype: str
    """

    data = excuse_dict.get(key)

    #if isinstance(data, list):
    result = random.choice(data)
    #else:
        #result = random.choice(data.values())

    for match in token_regex.findall(result):
        word = generate_excuse(excuse_dict, match) or match
        result = result.replace('{{{0}}}'.format(match), word)

    return result


def bofh_excuse(how_many=1):
    """Generate random BOFH themed technical excuses!

    :param how_many: Number of excuses to generate. (default 1)
    :type how_many: int
    :return: A list of `how_many` excuses.
    :rtype: list
    """

    excuse_path = os.path.join(os.path.dirname(__file__), 'bofh_excuses.json')
    with open(excuse_path, 'r') as _f:
        excuse_dict = json.load(_f)

    return [generate_excuse(excuse_dict) for _ in xrange(how_many)]


def main():
    for excuse in bofh_excuse():
        print excuse


if __name__ == '__main__':
    main()

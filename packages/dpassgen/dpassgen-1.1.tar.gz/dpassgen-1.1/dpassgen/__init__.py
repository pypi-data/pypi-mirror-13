# dpassgen
#
# Copyright 2016 John Dulaney <jdulaney@fedoraproject.org>
#
# dpassgen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dpassgen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dpassgen.  If not, see <http://www.gnu.org/licenses/>.



import argparse
import os
import random
import sys

def get_words(number):
    """Get $number of words"""
    try:
        if os.path.exists('/usr/share/dict/words'):
            with open('/usr/share/dict/words', 'r') as words_file:
                words = words_file.read().splitlines()
        else:
            with open('/usr/dict/words', 'r') as words_file:
                words = words_file.read().splitlines()
    except IOError:
        print('Could not locate system words file')
        sys.exit()
    words_length = len(words)
    password = ''
    for index in range(0, number):
        rando = random.SystemRandom().randint(1, words_length)
        password += words[rando]
    return password


def dpassgen_cli():
    """cli entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument('number', help='Number of words to use in password')
    try:
        number = int(parser.parse_args().number)
    except ValueError:
        print('Usage:  dpassgen number')
        print('Returns a password consisting of <number> of words')
        sys.exit()

    print(get_words(number))
    return 0


if __name__ == '__main__':
    dpassgen_cli()

import re

import modeled


class extract(modeled.property):

    def __init__(self, regex, **options):

        def getter(command):
            match = re.search(regex, command.text)
            return match.group(1)

        options['fget'] = getter
        super().__init__(**options)

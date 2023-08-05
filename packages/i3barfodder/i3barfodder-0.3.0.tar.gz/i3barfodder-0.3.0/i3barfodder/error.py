# Released under GPL3 terms (see LICENSE file)

class Validation(Exception): pass
class InvalidKey(Validation): pass
class InvalidValue(Validation): pass

class Argument(Exception): pass

class Config(Exception): pass
class ConfigParser(Config): pass


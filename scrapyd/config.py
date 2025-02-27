import glob
import io
from configparser import ConfigParser, NoOptionError, NoSectionError
from os.path import expanduser
from twisted.python import log
import sys
from scrapy.utils.conf import closest_scrapy_cfg
from pkgutil import get_data

# sys.path.append()

class Config(object):
    """A ConfigParser wrapper to support defaults when calling instance
    methods, and also tied to a single section"""

    SECTION = 'scrapyd'

    def __init__(self, values=None, extra_sources=()):
        if values is None:
            sources = self._getsources()
            default_config = get_data(__package__, 'default_scrapyd.conf').decode('utf8')
            self.cp = ConfigParser()
            self.cp.read_string(default_config)
            sources.extend(extra_sources)
            for fname in sources:
                try:
                    with io.open(fname) as fp:
                        self.cfg_path = fname
                        self.cp.read_file(fp)
                except (IOError, OSError):
                    pass
        else:
            self.cp = ConfigParser(values)
            self.cp.add_section(self.SECTION)

    def _getsources(self):
        sources = ['/etc/scrapyd/scrapyd.conf', r'd:\scrapyd\scrapyd.conf']
        sources += sorted(glob.glob('/etc/scrapyd/conf.d/*'))
        sources += ['scrapyd.conf']
        sources += [expanduser('~/.scrapyd.conf')]
        scrapy_cfg = closest_scrapy_cfg()
        if scrapy_cfg:
            sources.append(scrapy_cfg)
        return sources

    def _getany(self, method, option, default):
        try:
            return method(self.SECTION, option)
        except (NoSectionError, NoOptionError):
            if default is not None:
                return default
            raise

    def get(self, option, default=None):
        return self._getany(self.cp.get, option, default)

    def set(self, option, value, section='scrapyd'):
        self.cp.set(section, option, value)
        f = open(self.cfg_path, 'w')
        self.cp.write(f)
        f.close()

    def getint(self, option, default=None):
        return self._getany(self.cp.getint, option, default)

    def getfloat(self, option, default=None):
        return self._getany(self.cp.getfloat, option, default)

    def getboolean(self, option, default=None):
        return self._getany(self.cp.getboolean, option, default)

    def items(self, section, default=None):
        try:
            return self.cp.items(section)
        except (NoSectionError, NoOptionError):
            if default is not None:
                return default
            raise

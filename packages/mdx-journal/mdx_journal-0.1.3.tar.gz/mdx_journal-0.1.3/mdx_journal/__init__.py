import re
from markdown.preprocessors import Preprocessor
from markdown import Extension

__version__ = "0.1.1"


class JournalPreprocessor(Preprocessor):
    pattern_time = re.compile(r'^(\d{4})$')
    pattern_date = re.compile(r'^(\d{4}-\d{2}-\d{2})$')

    def run(self, lines):
        return [self._t1(self._t2(line)) for line in lines]

    def _t1(self, line):
        return self.pattern_time.sub(self._replacer_time, line)

    def _t2(self, line):
        return self.pattern_date.sub(self._replacer_date, line)

    def _replacer_time(self, match):
        time_str = match.groups()
        return '<h4>%s</h4>' % (time_str)

    def _replacer_date(self, match):
        time_str = match.groups()
        return '<h3>%s</h3>' % (time_str)


class JournalExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('journal', JournalPreprocessor(md), '<reference')


def makeExtension(configs=None):
    return JournalExtension(configs=configs)

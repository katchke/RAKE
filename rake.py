import re


class RAKE(object):
    def __init__(self, stopwords):
        self._stop = re.compile('|'.join([r'\b' + word + r'(?![\w-])' for word in stopwords]), re.IGNORECASE)

    def run(self, text):
        tokens = self._pre_process(text)
        candidates = self._process(tokens)

        sorted_keywords = sorted(candidates.iteritems(), key=lambda x: x[1], reverse=True)
        keywords = [(kw[0], kw[1]) for kw in sorted_keywords if len(kw[0].split(' ')) < 4 and len(kw[0]) < 30]

        return keywords

    def _is_num(self, text):
        try:
            _ = float(text) if '.' in text else int(text)
            return True
        except ValueError:
            return False

    def _pre_process(self, text):
        delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
        sents = delimiters.split(text)

        tokens = []

        for sent in sents:
            # A phrase is everything between two stopwords
            phrases = re.sub(self._stop, '|', sent.strip()).split('|')
            tokens.extend([phrase.strip().lower() for phrase in phrases if phrase != ''])

        return tokens

    def _process(self, tokens):
        def split(phrase):
            splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')

            return [w.strip().lower() for w in splitter.split(phrase) if w != '' and not self._is_num(w)]

        freq = {}
        deg = {}

        for token in tokens:
            words = split(token)

            for word in words:
                freq[word] = freq.get(word, 0) + 1
                deg[word] = deg.get(word, 0) + len(words) - 1

        _ = [deg.update({item: deg[item] + freq[item]}) for item in freq]

        # Calculate scores = deg(w)/freq(w)
        scores = {item: deg[item] / (freq[item] * 1.0) for item in freq}

        candidates = {token: sum([scores[word] for word in split(token)]) for token in tokens}

        return candidates

# -*- coding:utf-8 -*-
import re
from collections import defaultdict

from xml.sax.handler import ContentHandler


EXTRA_SPACES_REGEXP = re.compile(ur'\s+', flags=re.U)


def get_stop_words():
    stopwords = u'a|about|all|an|and|any|are|as|at|be|but|by|can|do|for|from|have|i|if|in|is|it|my|no|not|of|on|one|or|so|that|the|there|they|this|to|was|we|what|which|will|with|would|you|а|або|авжеж|аж|але|атож|б|без|би|бо|був|буде|будем|будемо|будет|будете|будеш|будешь|буду|будут|будуть|будь|будьмо|будьте|була|були|було|бути|бы|был|была|были|было|быть|в|вам|вами|вас|ваш|ваша|ваше|вашим|вашими|ваших|вашого|вашому|вашою|вашої|вашу|ваші|вашій|вашім|ввесь|весь|вже|ви|во|воно|вот|все|всего|всей|всем|всеми|всему|всех|всею|всього|всьому|всю|вся|всё|всі|всій|всім|всіма|всіх|всією|всієї|вы|від|він|да|де|для|до|дуже|еге|его|ее|ей|ему|если|есть|еще|ещё|ею|её|ж|же|з|за|зі|и|из|или|им|ими|их|й|його|йому|к|как|кем|кимось|ко|когда|кого|когось|ком|кому|комусь|которая|которого|которое|которой|котором|которому|которою|которую|которые|который|которым|которыми|которых|кто|кім|ледве|лиш|лише|майже|мене|меня|мені|мне|мной|мною|мовби|мог|моги|могите|могла|могли|могло|мого|ой|могу|могут|мое|моего|моей|моем|моему|моею|можем|может|можете|можешь|мои|моим|моими|моих|мой|мочь|мою|моя|моё|моём|моє|моєму|моєю|моєї|мої|моїй|моїм|моїми|моїх|мы|між|мій|на|навіть|над|нам|нами|нас|наче|начебто|наш|наша|наше|нашего|нашей|нашем|нашему|нашею|наши|нашим|нашими|наших|нашого|нашому|нашою|нашої|нашу|наші|нашій|нашім|не|невже|него|нее|ней|нем|немов|нему|неначе|нет|нехай|нею|неё|неї|ним|ними|них|но|ну|нього|ньому|нём|ні|ніби|нібито|ній|ніким|нікого|нікому|нікім|нім|ніхто|нічим|нічого|нічому|ніщо|ніяка|ніяке|ніякий|ніяким|ніяких|ніякого|ніякому|ніякою|ніякої|ніякі|ніякій|о|об|од|один|одна|одни|одним|одними|одних|одно|одного|одной|одном|одному|одною|одну|он|она|они|оно|от|отак|ото|оце|оцей|оцеє|оцим|оцими|оцих|оцього|оцьому|оцю|оцюю|оця|оцяя|оці|оцій|оцім|оцією|оцієї|оції|по|поки|при|про|під|с|сам|сама|саме|самий|самим|самими|самих|само|самого|самому|самою|самої|саму|самі|самій|самім|свого|свое|своего|своей|своем|своему|своею|свои|своим|своими|своих|свой|свою|своя|своё|своём|своє|своєму|своєю|своєї|свої|своїй|своїм|своїми|своїх|свій|се|себе|себя|сей|сими|сих|собой|собою|собі|сього|сьому|сю|ся|сі|сій|сім|сією|сієї|та|так|така|такая|таке|таки|такие|такий|таким|такими|таких|такого|такое|такой|таком|такому|такою|такої|таку|такую|такі|такій|такім|тая|твого|твою|твоя|твоє|твоєму|твоєю|твоєї|твої|твоїй|твоїм|твоїми|твоїх|твій|те|тебе|тебя|тем|теми|тех|теє|ти|тим|тими|тих|то|тобой|тобою|тобі|того|той|только|том|тому|тот|тою|тої|ту|тую|ты|ті|тій|тільки|тім|тією|тієї|тії|у|увесь|уже|усе|усього|усьому|усю|уся|усі|усій|усім|усіма|усіх|усією|усієї|хай|хоч|хто|хтось|хіба|це|цей|цеє|цим|цими|цих|цього|цьому|цю|цюю|ця|цяя|ці|цій|цім|цією|цієї|ції|чего|чем|чему|чи|чий|чийого|чийому|чим|чимось|чимсь|чию|чия|чиє|чиєму|чиєю|чиєї|чиї|чиїй|чиїм|чиїми|чиїх|чого|чогось|чому|чомусь|что|чтобы|чём|чім|чімсь|ще|що|щоб|щось|эта|эти|этим|этими|этих|это|этого|этой|этом|этому|этот|эту|я|як|яка|якась|яке|якесь|який|якийсь|яким|якими|якимись|якимось|якимсь|яких|якихось|якого|якогось|якому|якомусь|якою|якоюсь|якої|якоїсь|якраз|яку|якусь|якщо|які|якій|якійсь|якім|якімось|якімсь|якісь|є|і|із|іякими|їй|їм|їх|їхнього|їхньому|їхньою|їхньої|їхню|їхня|їхнє|їхні|їхній|їхнім|їхніми|їхніх|її|http|www'
    return set(stopwords.split('|'))


def normalize(string):
    return re.sub(EXTRA_SPACES_REGEXP, u' ', string.strip())


class TextHandler(ContentHandler):
    non_alpha_num_re = re.compile(ur'\W', re.U | re.I | re.M)
    replace_e_re = re.compile(ur'ё', re.U | re.M)
    whitespace_re = re.compile(ur'[\S]+', re.U | re.M)

    allowed_tags = {'b', 'strong', 'em', 'i', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'h1', 'title', 'description'}

    def __init__(self):
        ContentHandler.__init__(self)

        tags = ['title', 'h1', 'a', 'h2h6', 'beis', 'body', 'metadescription', 'text']
        self.result = {tag: {'texts': [], 'word_count': 0} for tag in tags}
        self.stopwords = get_stop_words()
        self.current_element = None
        self.path = []

    def startElement(self, name, attrs):
        if not name:
            return

        name = name.lower()

        self.path.append(name)
        if name == 'meta':
            attr_names = attrs.getNames()
            if 'content' not in attr_names or 'name' not in attr_names:
                return
            name_value = attrs.getValue('name')
            if name_value == 'description':
                content_value = attrs.getValue('content')
                self.add_content_to_result('metadescription', content_value)
            return

        if (self.current_element == 'h1' or (self.current_element == 'a' and name != 'h1')
           or name not in self.allowed_tags):
            return

        self.current_element = name

    def endElement(self, name):
        name = name.lower()
        if self.path:
            pop_tag = self.path.pop(-1)
            while pop_tag != name and self.path:
                pop_tag = self.path.pop(-1)

        if (self.current_element == 'h1' and name != 'h1') or (self.current_element == 'a' and name != 'a')\
           or (self.current_element == 'h1' and name == "h1" and 'h1' in self.path):
            return
        elif self.current_element == 'h1' and name == "h1" and 'a' in self.path:
            self.current_element = 'a'
            return
        else:
            if self.path:
                n = -1
                self.current_element = self.path[n]
                while self.current_element not in self.allowed_tags:
                    n -= 1
                    try:
                        self.current_element = self.path[n]
                    except IndexError:
                        self.current_element = None
                        break
            self.current_element = None

    def characters(self, content):
        content = content.strip()

        p = self.current_element

        if p != 'title' and p != 'meta':
            self.add_content_to_result('body', content)

        tag = None
        if p in ['h1', 'a', 'title']:
            tag = p
        elif p in ['b', 'strong', 'em', 'i']:
            tag = 'beis'
        elif p in ['h2', 'h3', 'h4', 'h5', 'h6']:
            tag = 'h2h6'
        elif p != 'title' and p != 'meta':
            tag = 'text'

        self.add_content_to_result(tag, content)

    def add_content_to_result(self, tag, content):
        if tag in self.result:
            self.result[tag]['texts'].append(content)
            self.result[tag]['word_count'] += self._get_words_count(content)

    def _get_words_count(self, text):
        text = unicode(text.lower())
        text = self.non_alpha_num_re.sub(' ', text)
        text = self.replace_e_re.sub(u'е', text)

        counter = 0
        for word in self.whitespace_re.findall(text):
            if word not in self.stopwords:
                counter += 1
        return counter


class NewTextHandler(ContentHandler):
    whitespace_re = re.compile(ur'[\S]+', re.U | re.M)

    def __init__(self):
        """
        В text_fragment должны попасть то что попадает в body и длинне 50 слов
        В plain_text должно попасть то что короче 50 слов
        """
        ContentHandler.__init__(self)
        self.tags = defaultdict(lambda: {'texts': [], 'word_count': 0})
        self.path = []

    def startElement(self, name, attrs):
        self.path.append(name.lower())
        self.tags[self.current_tag]['texts'].append(u'')

    def endElement(self, name):
        ended_tag = self.path.pop(-1)
        ended_content = self.tags[ended_tag]['texts'][-1]

        prev_tag = self.current_tag
        if prev_tag:
            if prev_tag == 'body':
                words_count = self.get_words_count(ended_content)
                new_tag = 'text_fragment' if words_count < 50 else 'plain_text'
                self.tags[new_tag]['texts'].append(ended_content)
                self.tags[new_tag]['word_count'] += words_count

                self.tags['body']['texts'].append(ended_content)
                self.tags['body']['word_count'] += words_count
            else:
                self.tags[prev_tag]['texts'][-1] += u' ' + ended_content
                self.tags[prev_tag]['word_count'] += self.get_words_count(ended_content)

    def characters(self, content):
        content = content.strip()
        self.tags[self.current_tag]['texts'][-1] += u' ' + content
        self.tags[self.current_tag]['word_count'] += self.get_words_count(content)

    def get_words_count(self, content):
        return len(self.whitespace_re.findall(content))

    @property
    def current_tag(self):
        return self.path[-1] if self.path else None

    @property
    def result(self):
        tags = ['title', 'h1', 'a', 'body', 'plain_text', 'text_fragment']
        result = {}
        for tag in tags:
            if tag in self.tags:
                value = self.tags[tag]
                result[tag] = {
                    'texts': filter(bool, map(normalize, value['texts'])),
                    'word_count': value['word_count']
                }

        return result


class ErrorHandler(object):
    def error(self, exception):
        pass

    def fatalError(self, exception):
        pass

    def warning(self, exception):
        pass

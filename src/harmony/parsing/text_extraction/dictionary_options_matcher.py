'''
MIT License

Copyright (c) 2023 Ulster University (https://www.ulster.ac.uk).
Project: Harmony (https://harmonydata.ac.uk)
Maintainer: Thomas Wood (https://fastdatascience.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import spacy
items = ['yes no',
 'not true somewhat true certainly true',
 'not at all a little bit moderately quite a bit extremely',
 'none of the time rarely some of the time often all of the time',
 'not true somewhat or sometimes true very true or often true',
 'never rarely sometimes often always',
 'not true quite true very true',
 'certainly true sometimes true not true',
 'strongly disagree disagree agree strongly agree',
 'not at all true somewhat true mainly true definitely true',
 'rarely never occasionally often almost always always',
 'very true quite true not true',
 'doesn t apply applies a bit moderately applies certainly applies',
 'strongly disagree disagree neither agree nor disagree agree strongly agree',
 'definitely agree slightly agree slightly disagree definitely disagree',
 'true sometimes true not true',
 'strongly disagree slightly disagree slightly agree strongly agree',
 'agree strongly agree a little neither agree or disagree disagree a little disagree strongly',
 'definitely disagree slightly disagree slightly agree definitely agree',
 'not true sometimes true true',
 'not also true just a little true pretty much true very much true',
 'never or rarely sometimes often very often',
 'strongly agree agree disagree strongly disagree',
 'doesn t apply applies somewhat certainly applies',
 'not at all like child not much like child somewhat like child quite like child exactly like child',
 'not at all several days more than half the days nearly every day',
 'very rarely rarely occasionally somewhat often often very often',
 'very rarely less than half the time about half the time more than half the time almost always',
 'no somewhat yes',
 'not at all true sometimes true definitely true',
 'very often often not very often never',
 'behaviour not characteristic of the child behaviour somewhat characteristic of the child behaviour characteristic of the child',
 'true sometimes not at all',
 'often sometimes not often never',
 'no not true sometimes somewhat yes very true',
 'not at all no more than usual rather more than usual much more than usual',
 'never or almost never true usually not true sometimes but infrequently true occasionally true often true usually true always or almost always true',
 'very inaccurate moderately inaccurate neither inaccurate or accurate moderately accurate very accurate',
 'a lot somewhat a little not at all',
 'extremely untrue slightly untrue neither true nor untrue slightly untrue extremely untrue',
 'very inaccurate moderately inaccurate neither inaccurate nor accurate moderately accurate very accurate',
 'very much so moderately so somewhat not at all',
 'no a little somewhat yes',
 'never almost never sometimes fairly often very often',
 'a lot some a little not at all',
 'not true sometimes true',
 'never seldom sometimes often very often',
 'no maybe yes',
 'not true somewhat true certainly true don t know',
 'none questionable mild moderate marked severe',
 'not at all true somewhat true very true definitely true',
 'not at all true hardly ever true sometimes true often true always true',
 'none 1 2 times 3 5 times more than 5 times',
 'not true somewhat true very true definitely true',
 'disagree completely disagree somewhat neutral agree somewhat agree completely',
 'strongly disagree moderately disagree mildly disagree neither agree or disagree mildly agree moderately agree strongly agree',
 'not at all true somewhat true very true',
 'not true sometimes true often true almost always true',
 'most of the time some of the time rarely or never',
 'never always',
 'no change for the better a small change for the better a medium change for the better a big change for the better',
 'very slightly or not at all a little moderately quite a bit extremely',
 'almost always true often true sometimes true seldom true never true',
 'not at all once 2-5 times 6 or more times',
 'describes me very well describes me a bit does not describe me very well does not describe me at all',
 'never very rarely sometimes quite often always',
 'almost never never some of the time half of the time most of the time almost always always',
 'not at all a little mostly especially',
 'rarely or none of the time less than 1 day some or a little of the time 1 2 days occasionally or a moderate amount of time 3 4 days most or all of the time 5 7 days ',
 'very slightly not at all a little moderately quite a bit extremely',
 'not at all somewhat moderately so very much so',
 'rarely or none of the time less than a day some or a little of the time 1 to 2 days occasionally 3 to 4 days all of the time 5 to 7 days',
 'strongly disagree disagree neither disagree agree agree strongly agree',
 'yes nearly always yes often yes sometimes no never',
 'rarely or none of the time less than one day some or a little of the time 1 2 days occasionally or a moderate amount of the time 3 4 days most or all of the time 5 7 days ',
 'strongly disagree moderately disagree neither agree or disagree moderately agree strongly agree',
 'strongly disagree moderately disagree neither disagree nor agree moderately agree strongly agree',
 'not true at all somewhat true mainly true definitely true',
 'rarely or none of the time less than 1 day some or a little of the time 1 2 days occasionally or moderate amount of time 3 4 days most or all of the time 5 7 days ',
 'certainly applies applies somewhat doesn t apply',
 'not at all just a little pretty much very much',
 'often sometime not often never',
 'far below average below average slightly below average average slightly above average above average far above average',
 'all of the time most of the time more than half of the time less than half of the time some of the time at no time',
 'yes no items all of the time most of the time a good bit of the time some of the time a little of the time none of the time not at all no more than usual moderately quite a bit extremely',
 'totally agree agree somewhat neutral disagree somewhat totally disagree',
 'never seldom sometimes often always',
 'not true at all just a little true pretty much true very much true',
 'strongly agree slightly agree slightly disagree strongly disagree',
 'strongly disagree disagree slightly disagree neither agree nor disagree slightly agree agree strongly agree',
 'very little a little some much very much',
 'not true at all somewhat all very true definitely true',
 'never sometimes often nearly always',
 'not at all true of me a little true of me pretty much true of me very much true of me prefer not to say',
 'not at all a little often a lot all the time',
 'strongly agree agree disagree strongly disagree can t say',
 'not true quite or sometimes true very or often true',
 'strongly disagree disagree nither disagree or agree agree strongly agree',
 'never sometimes frequently',
 'all of the time most of the time some of the time a little of the time none of the time',
 'very much quite a bit moderately a little not at all',
 'most days at least once a week less than once a week never',
 'none mild moderate clear extreme',
 'not at all to a slight degree to a moderate degree to a great degree all the time',
 'better than usual same as usual less than usual much less than usual',
 'yes no unsure',
 'not at all characteristic of child a little characteristic of child somewhat a characteristic of child very characteristic of child entirely characteristic of child',
 'none or almost none of the time some of the time most of the time all or almost all or the time',
 'never rarely 1 2 times per month 1 2 times per week 3 times per week',
 'absent partially present present',
 'blue really true for me blue sort of true for me red really true for me red sort of true for me',
 'extremely satisfied moderately satisfied can t decide moderately dissatisfied extremely dissatisfied not an issue',
 'true false',
 'extremely untrue quite untrue slightly untrue neither true nor false slightly true quite true extremely true',
 'never once twice 3 4 times 5 ',
 'definitely false mostly false mostly true definitely true',
 'very slightly a little moderately quite a bit extremely',
 'never rarely quite often very often always',
 'a lot worse than average a bit worse than average about average a bit better than average a lot better than average',
 'not at all yes occasionally yes most of the time',
 'no 1 2 days per week 3 4 days per week 5 6 days per week daily',
 'none of the time a little of the time some of the time most of the time all of the time',
 'always mostly sometimes never',
 'not at all a little quite a lot a great deal',
 'did not occur occasionally quite often a lot',
 'i did not do this once or twice every few weeks about once a week several times a week or more',
 'disagree strongly disagree moderately disagree a little neither agree nor disagree agree a little agree moderately agree strongly',
 'strongly disagree disagree neither disagree nor agree agree strongly agree',
 'almost always most of the time sometimes never',
 'almost always true often true sometimes true not often true never true',
 'never once or twice less than monthly monthly weekly daily or almost daily',
 'absolutely untrue mostly untrue somewhat untrue can t say true or false somewhat true mostly true absolutely true',
 'all of the time most of the time a good bit of the time some of the time a little of the time none of the time not at all no more than usual moderately quite a bit extremely',
 'agree strongly agree disagree disagree strongly',
 'not at all hardly true moderately true exactly true',
 'not true at all hardly true moderately true exactly true',
 'certainly true somewhat true not true',
 'very false for me moderately false for me slightly false for me slightly true for me moderately true for me very true for me',
 'never occasionally half of the time most of the time all of the time',
 'never sometimes often',
 'no a little a lot',
 'is often like this is sometimes like this is never like this',
 'free response',
 'almost never sometimes often almost always',
 'never sometimes often always',
 'about every day more than once a week about every week about every month rarely or never',
 'strongly disagree mildly disagree neutral mildly agree strongly agree',
 'almost never sometimes about half the time most of the time almost always',
 'agree mostly agree mostly disagree disagree',
 'free response number of times',
 'not at all several days over half the days nearly every day',
 'free response number',
 'not at all true several days more than half the days nearly every day',
 'strongly disagree disagree neither agree or disagree agree strongly agree',
 'not true at all rarely true sometimes true often true always true',
 'strongly disagree disagree undecided agree strongly agree',
 'always most of the time sometimes rarely never don t know refusal',
 'not at all occasionally quite often very often',
 'agree a lot agree a bit not sure disagree a bit disagree a lot',
 'never occasionally some of the time most of the time all of the time',
 'not true at all somewhat true certainly true',
 'extremely untrue slightly untrue neither true nor untrue slightly true extremely true',
 'never rarely from time to time fairly often very often',
 'all of the time most of the time a good bit of the time some of the time a little of the time none of the time',
 'not at all concerned a bit concerned very concerned extremely concerned',
 'no 1 2 days 3 4 days 5 6 days daily',
 'yes unsure no',
 'very dissatisfied quite dissatisfied slightly dissatisfied neutral slightly satisfied quite satisfied very satisfied',
 'does not apply applies sometimes applies often',
 'never rarely sometimes often very often',
 'according to handley et al 2004 the primary measures of performance for this task are accuracy on the stop signal trials with mean reaction time and primary trial accuracy also reported ',
 'not at all a little moderately a lot extremely',
 'all of the time most of the time some of the time a little of the time none o the time',
 'never monthly or less 2 4 times a month 2 3 times a week 4 or more times a week',
 'strongly agree agree slightly agree neither agree nor disagree slightly disagree disagree strongly disagree',
 'strongly agree disagree slightly disagree neither agree nor disagree slightly agree agree strongly agree',
 'rarely occasionally often almost always',
 'participants indicate their answer by choosing from a selection of five of silhouette images indicating a range of body sizes ',
 'strongly disagree disagree neutral agree strongly agree don t know',
 'not true at all somewhat true very true definitely true',
 'not at all several days more than half the days nearly everyday',
 'yes since the covid 19 pandemic yes but not since the covid 19 pandemic no',
 'not at all a little bit somewhat very much extremely',
 'very satisfied satisfied dissatisfied very dissatisfied',
 'the ados ratings that correspond to dsm iv criteria were summed to produce an overall score a score of seven or more is the threshold used to identify an inclusive category of non specific pdd the recommended threshold of 10 or more is applied in this report to indicate a case of asd ',
 'non smoker ex smoker light smoker 10 moderate smoker 10 19 heavy smoker 20 ',
 'no a little a lot it terrifies me',
 'very sad moderately sad a mixture of happiness and sadness moderately happy very happy',
 'no never yes in the past 3 months yes but not in the last 3 months',
 'i haven t it has happened once or twice 2 3 times a month about once a week several times a week',
 'rarely never sometimes often always']
nlp =spacy.blank("en")
import re
from spacy.matcher import Matcher

num_regex = re.compile(r'^\d+$')

options_matcher = Matcher(nlp.vocab)
patterns = []
for i in items:
    pattern = []
    for w in i.split(" "):
        if num_regex.match(w):
            pattern.append({"LIKE_NUM":True})
        else:
            pattern.append({"NORM":w})
        pattern.append({"IS_PUNCT":True, "OP":"?"})
    patterns.append(pattern)

pattern = [{"LENGTH":1, "OP":"?"},{"LENGTH":1, "OP":"?"},{"LENGTH":1},{"LENGTH":1},{"LENGTH":1},{"LENGTH":1},{"ORTH":"\n"}]
patterns.append(pattern)
options_matcher.add("OPTIONS", patterns)
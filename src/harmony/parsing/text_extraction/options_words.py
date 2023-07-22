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

OPTIONS_WORDS = {'attractive', 'sometimes', 'some or a little of the time', 'true', 'some times', 'not at all', 'none',
                 'somewhat true', 'not likely', 'often', 'cinco vezes', 'very likely', 'igual',
                 'algumas vezes verdadeira', 'very easy', 'tanto quanto sabe', 'totally',
                 'occasionally or a moderate amount of time', 'um pouco', 'extremamente', 'neither agree nor disagree',
                 'unattractive', 'always', 'a lot', 'some of the time', 'mais ou menos verdadeiro', 'sim',
                 'unappealing', 'raramente', 'concordo totalmente', 'totalmente de acordo', 'provavelmente não', 'não',
                 '1-5 meses', 'fair', 'sempre', 'uma vez', 'às vezes', 'rarely', 'extremely difficult',
                 'discordo totalmente', 'dificuldades graves', 'probably not', 'abaixo da média exigida pela escola',
                 'neither likely nor unlikely', 'yes', 'nada', "i don't like it at all", 'limited a little', 'melhor',
                 'não concordo nem discordo', 'mais que muito', 'probably', 'mais ou menos', 'strongly agree',
                 'frequentemente', 'totally agree', 'insuficiente', 'mais de 1 ano', 'não gosto nada', 'very',
                 'likely', 'not likely at all', 'concordo parcialmente', 'all of the time', 'extremely',
                 'very important', 'strongly disagree', 'disagree slightly', 'none of these', 'uma pouco',
                 'menos de 1 mês', 'duas vezes', 'more than half the days', 'disagree', 'excellent',
                 'none of the time', 'not limited at all', 'uma pouco verdadeira', 'pior', 'poor', 'não sei',
                 'agree strongly', 'falso', 'rarely or none of the time', 'muito', 'nunca', 'limited a lot',
                 'somewhat appealing', 'verdade', 'certainly true', 'daily', 'not difficult at all', 'appealing',
                 'somewhat disagree', 'quatro vezes', 'verdadeiro', 'disagree strongly', 'agree', 'several days',
                 'não sabe', 'most of the time', '6-12 meses', 'discordo parcialmente', 'provavelmente',
                 'a moderate amount of time', 'neither agree or disagree', 'about the same',
                 'muitas vezes ou quase sempre', 'neutral', 'não sabe/não se aplica', 'difficult', 'never',
                 'most or all of the time', 'a little', 'agree slightly', 'very appealing',
                 'neither easy nor difficult', 'very good', 'não é verdadeito', 'pequenas dificuldades',
                 'very difficult', 'mais de cinco vezes', 'dificuldades bem definidas', 'algumas vezes', 'definitely',
                 'três vezes', 'nearly every day', 'good', 'no', 'not true', 'nunca ou raramente',
                 'muito verdadeira ou frequentemente verdadeira', 'não é verdade', 'claro que compraria',
                 'somewhat agree', 'easy', "most days",
                 "at least once a week",
                 "at least once a month",
                 "several times a year",
                 "once a year or less",
                 "never or almost never",
                 "some days, but not all days",
                 "every day",
                 "more than once a day",
                 "once a day",
                 "less often but at least once a month",
                 "less than once a month",
                 "very confident",
                 "slightly confident",
                 "not at all confident",
                 "very true",
                 "partly true",
                 "not true at all",
                 "other", }

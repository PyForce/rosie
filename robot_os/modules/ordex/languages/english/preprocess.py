# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 11:02:54 2015

@author: Toni
"""

#### IMPORT ####
print('    importing nltk ...')
import nltk
from ... import base
from . import utils

__all__=['preprocess']

#### PREPROCESSING FUNCTIONS ####

def preprocess(text):
    """
    Order extraction system preprocessing.
    
    Sentence and word segmentation (tokenization), morphological analysis and pre-syntactic analysis
    
    :param text: sequence of words
    :type text: str
    :return: list of syntactic trees
    :type: list(nltk.Tree(list(tuple(str, str))))
    
    >>> preprocess('The black cat')
    [nltk.Tree('S', [nltk.Tree('NONE', [('The', 'DT'), ('black', 'JJ'), ('cat', 'NN')])])]
    """
    #---- tokenize ----
    sents=nltk.sent_tokenize(text)    
    sents=[nltk.word_tokenize(s) for s in sents]
    #---- POS tag ----
    sents=[_fix_pos_tag(s) for s in sents]
    #---- chunking ----
    sents=[_regexp_chunker(s) for s in sents]
    return sents

def _fix_pos_tag(sentence):
    """
    Fix the POS tagged.
    
    :param sentence: sequence of tokens to be tagged
    :type sentence: list(str)
    :return:  fixed tagged tokens
    :rtype: list(tuple(str, str))
    """
    sentence.insert(0,'you')
    sentence=nltk.pos_tag(sentence)
    del sentence[0]
    for item in range(len(sentence)):
        #### PREPOSITION ####
        #==== of ====
        if sentence[item]==('of','IN'):
            sentence[item]=('of','OF')
        #==== next/close to ====
        elif sentence[item][0] in ['next','close']:
            try:
                if sentence[item+1]==('to','TO'):
                    sentence[item]=(sentence[item][0],'IN')
            except: pass
        #==== from ====
        elif sentence[item]==('from','IN'):
            sentence[item]=('from','FROM')
        #==== around ====
        elif sentence[item][0]=='around':
            sentence[item]=('around','IN')
        #### OTHERS ####
        elif sentence[item][0]=='bed':
            sentence[item]=('bed','NN')
        #### WORDS OF TIME ####
        #==== o'clock ====
        elif sentence[item][0]=="o'clock":
            sentence[item]=("o'clock",'JJ')
            #---- hour(CDTO) o'clock ----
            try:
                if sentence[item-1][1]=='CD':
                    sentence[item-1]=(sentence[item-1][0],'CDTO')
            except: pass
        #==== past ====
        elif sentence[item]==('past','NN'):
            sentence[item]=('past','JJ')
        #==== quarter (15 minutes) ====
        elif sentence[item][0]=='quarter':
            try:
                if sentence[item+1][0] in ['past','to']:
                    sentence[item]=('15','CD')
            except: pass
        #==== half (30 minutes) ====
        elif sentence[item][0]=='half':
            try:
                if sentence[item+1][0]=='past':
                    sentence[item]=('30','CD')
            except: pass
        #==== second (time or ordinal) ====
        elif sentence[item][0]=='second':
            try:
                if sentence[item-1][1]=='CD':
                    sentence[item]=('second','NN')
                    continue
            except: pass
            #---- ordinal (2nd) ----
            sentence[item]=('2nd','OD')
        #==== tonight ====
        elif sentence[item]==('tonight','JJ'):
            sentence[item]=('tonight', 'NN')
        #### TIME ####
        #==== time ====
        elif sentence[item][1]=='CD':
            #---- cardinal ----
            cardinal=utils.keyword(sentence[item],'cardinal')
            if cardinal:
                sentence[item]=(cardinal,'CD')
            #---- hh:mm am/pm ----
            elif sentence[item][0].endswith('am'):
                sentence[item]=(sentence[item][0],'CDTM')
            elif sentence[item][0].endswith('pm'):
                sentence[item]=(sentence[item][0],'CDTM')
            #---- hh:mm ----
            else:
                try:
                    if sentence[item][0][-3] in ['.',':']:
                        sentence[item]=(sentence[item][0],'CDT')
                except: pass
                #---- ordinal ----
                try:
                    if sentence[item][0][-2:] in ['st','nd','rt','th']:
                        if sentence[item][0][-3].isdigit():
                            sentence[item]=(sentence[item][0],'OD')
                except: pass
        #### NUMBERS #####
        #==== ordinal numbers ====
        elif sentence[item][1] in ['JJ','NN']:
            ordinal=utils.keyword(sentence[item],'ordinal')
            if ordinal:
                sentence[item]=(ordinal,'OD')
            else:
                try:
                    if sentence[item][0][-2:] in ['st','nd','rt','th']:
                        if sentence[item][0][-3].isdigit():
                            sentence[item]=(sentence[item][0],'OD')
                except: pass
        #==== cardinal numbers ====
        else:
            cardinal=utils.keyword(sentence[item],'cardinal')
            if cardinal:
                sentence[item]=(cardinal,'CD')
    return sentence

def _regexp_chunker(sentences):
    """
    Segments and labels multitoken sequences.
    
    :param sentence: tagged tokens
    :type sentence: list(tuple(str, str))
    :return: syntactic trees
    :rtype: nltk.Tree(list(tuple(str, str)))
    """
    grammar = r"""
    #####################################
    #      INTERROGATIVE SENTENCES      #
    #####################################
    
    #future "going to" (TO BE + SUBJECT + going to + VERB + COMPLEMENT?)
    INT_FGT: {<VB(P|Z)>(<PRP>|(<DT|PRP\$>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<VBG><TO><VB(P)?><.*>*<\.>}
    
    #future continuous (Will + SUBJECT + be + VERB-ing + COMPLEMENT?)
    INT_FC: {<MD>(<PRP>|(<DT|PRP\$>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<VB><VBG><.*>*<\.>}   
    
    #future perfect (Will + SUBJECT + have + VERB(past participle) + COMPLEMENT?)
    INT_FP: {<MD>(<PRP>|(<DT|PRP\$>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<VB><VBN><.*>*<\.>}
    
    #future "will" (Will + SUBJECT + VERB + COMPLEMENT?)
    INT_FW: {<MD>(<PRP>|(<DT|PRP\$>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<VB><.*>*<\.>}
    
    #present simple (Do/Does + SUBJECT + VERB + COMPLEMENT?)
    INT_PRS: {<VB(P|Z)>(<PRP>|(<DT|PRP\$>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<VB(P)?><.*>*<\.>}
    
    #present continuous (TO BE + SUBJECT + VERB-ing + COMPLEMENT?)
    INT_PRC: {<VB(P|Z)>(<PRP>|(<DT|PRP\$>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<VBG><.*>*<\.>}
    
    #present perfect (Have/Has + SUBJECT + VERB(past participle) + COMPLEMENT?)
    #interrogative "to have" (Have/Has + SUBJECT + got + COMPLEMENT?)
    INT_PRP_TH: {<VB(P|Z)><PRP><RB>?<VBD><.*>*<\.>}
    
    #present perfect continuous (Have/Has + SUBJECT + been + VERB-ing + COMPLEMENT?)
    INT_PRPC: {<VB(P|Z)><PRP><VBN><VBG><.*>*<\.>}
    
    #past simple (Did + SUBJECT + VERB + COMPLEMENT?)
    INT_PAS: {<VBD><PRP><VB(P)?><.*>*<\.>}
    
    #past continuous (Was/Were + SUBJECT + VERB-ing + COMPLEMENT?)
    INT_PAC: {<VBD><PRP><VBG><.*>*<\.>}
    
    #past perfect (Had + SUBJECT + VERB(past participle) + COMPLEMENT?)
    INT_PAP: {<VBD><PRP><VBD><.*>*<\.>}
    
    #past perfect continuous (Had + SUBJECT + been + VERB-ing + COMPLEMENT?)
    INT_PAPC: {<VBD><PRP><VBN><VBG><.*>*<\.>}
    
    
    #interrogative "to be" (TO BE + SUBJECT + COMPLEMENT?)
    INT_WTB: {<VB(P|Z)>(<PRP>|(<DT|PRP\$>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<.*>*<\.>}
    
    #interrogative "there" (Is/Are there + COMPLEMENT?)
    INT_WTH: {<VB(P|Z)><EX|RB><.*>*<\.>}
    
    
    #interrogative pronoun
    WH_C: {<W.*><.*>*<\.>}
    
    #interrogative pronoun (extra)
    WH_EX: {<W.*><INT_.*>}
    
    #####################################
    #              SENTENCES            #
    #####################################    
    
    #modal auxiliary verbs (SUBJECT + MODAL VERB + VERB + COMPLEMENT)
    SEN_MV: {<PRP><MD><RB>?<VB><.*>*}
    
    #####################################
    #        IMPERATIVE SENTENCES       #
    #####################################
    
    #imperative negative (Let's not + VERB + COMPLEMENT)
    IMP_N$: {<VB(D)?><POS|PRP><RB><VB.*> (<CD.*|DT|EX|FROM|IN|JJ.*|LS|NN.*|OD|OF|P.*|R.*|TO|VB.*> (<CC|,><CD.*|DT|JJ.*|NN.*|OD|OF|POS|TO>)*)*}
    
    #imperative negative (Don't + VERB + COMPLEMENT)
    IMP_N: {<VBP><RB><VB.*> (<CD.*|DT|EX|FROM|IN|JJ.*|LS|NN.*|OD|OF|P.*|R.*|TO|VB.*> (<CC|,><CD.*|DT|JJ.*|NN.*|OD|OF|POS|TO>)*)*}

    #imperative affirmative (Let's + VERB + COMPLEMENT)
    IMP_A$: {<VB(D)?><POS|PRP><VB.*> (<CD.*|DT|EX|FROM|IN|JJ.*|LS|NN.*|OD|OF|P.*|R.*|TO|VB.*> (<CC|,><CD.*|DT|JJ.*|NN.*|OD|OF|POS|TO>)*)*}

    #present simple affirmative (You + VERB + COMPLEMENT)
    AFF_PRS: {<PRP><VBP><DT|IN|JJ.*|NN.*|OF>+}

    #### NONE ####
    NONE: {<\$|CD.*|DT|EX|FROM|FW|IN|JJ.*|LS|MD|NN.*|OD|OF|P.*|R.*|SYM|TO|UH|W.*> <VB.*>}
    
    #imperative affirmative (VERB + COMPLEMENT)
    IMP_A: {<VB.*> (<CD.*|DT|EX|FROM|IN|JJ.*|LS|NN.*|OD|OF|P.*|R.*|TO|VB.*> (<CC|,><CD.*|DT|JJ.*|NN.*|OD|OF|POS|TO>)*)*}
    
    #conditional -1 (If PRESENT SIMPLE AFFIRMATIVE, IMPERATIVE)
    COND-1: {<IN><AFF_PRS><,><IMP_.*>}
    """
    chunker = nltk.RegexpParser(grammar)
    result = chunker.parse(sentences)
    if base.DRAW:
        result.draw()
    return result
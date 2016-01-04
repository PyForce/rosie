# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 10:49:22 2015

@author: Toni
"""

#### IMPORT ####

from ... import base
from . import utils

import nltk
from datetime import datetime, timedelta

__all__=['process']

#### SOURCES ####
print('    loading pos_tag ...')
nltk.pos_tag(['.'])
print('    loading lemmatizer ...')
lemmatizer=nltk.WordNetLemmatizer()
#lemmatizer.lemmatize('','v')

COMMAND_CMD=[]
COMMANDS_CURRENT=[]
COMMANDS_FORBIDDEN=[]
COMMANDS_ENDED=[]

PRAGMATIC_SUBJECT=''

################### GRAMMAR ###################
def process(sentences):
    """
    Order extraction system processing.

    Syntactic analysis, semantic analysis and pragmatic analysis

    :param text: list of syntactic trees
    :type text: list(nltk.Tree(list(tuple(str, str))))
    :return: list of commands
    :type: list(list(tuple(str, dict(str))))

    >>> process([nltk.Tree('S', [nltk.Tree('IMP_A', [('stop', 'VB')])])])
    """
    for sent in sentences:
        #---- process each sentence ----
        for s in sent:
            #---- process classified sentence ----    
            if type(s) is nltk.tree.Tree:
                _sentence_process(s)
            elif type(s) is tuple:
                pass

def _sentence_process(sentence):
    #==== imperative affirmative ====
    if sentence.label()=='IMP_A':
        imperative_affirmative(sentence)
    elif sentence.label()=='IMP_A$':
        imperative_affirmative(sentence[2:])
    #==== imperative negative ====
    elif sentence.label()=='IMP_N':
        imperative_negative(sentence)
    elif sentence.label()=='IMP_N$':
        imperative_negative(sentence[1:])
    #==== interrogative PRESENT ====
    elif sentence.label()=='INT_PRS':
        present_simple(sentence)
    elif sentence.label()=='INT_PRC':
        present_continuous(sentence)
    elif sentence.label()=='INT_PRP_TH':
        if sentence[2][0]=='got':
            interrogative_to_have(sentence)
        else:
            present_perfect(sentence)
    elif sentence.label()=='INT_PRPC':
        present_perfect_continuous(sentence)
    #==== interrogative PAST ====
    elif sentence.label()=='INT_PAS':
        past_simple(sentence)
    elif sentence.label()=='INT_PAC':
        past_continuous(sentence)
    elif sentence.label()=='INT_PAP':
        past_perfect(sentence)
    elif sentence.label()=='INT_PAPC':
        past_perfect_continuous(sentence)
    #==== interrogative FUTURE ====
    elif sentence.label()=='INT_FGT':
        future_going_to(sentence)
    elif sentence.label()=='INT_FW':
        future_will(sentence)
    elif sentence.label()=='INT_FC':
        future_continuous(sentence)
    elif sentence.label()=='INT_FP':
        future_perfect(sentence)
    #==== interrogative ====
    elif sentence.label()=='INT_WTH':
        interrogative_there(sentence)
    elif sentence.label()=='INT_WTB':
        interrogative_to_be(sentence)
    elif sentence.label()=='WH_C':
        interrogative_Wh_questions(sentence)
    #==== sentence ====
    elif sentence.label()=='SEN_MV':
        modal_auxiliary_verb(sentence)
    elif sentence.label()=='COND-1':
        conditional_minus1(sentence)

def _chunk_imperative_complement(sent, draw=False):
    grammar = r"""
    CTO: {<TO><DT|PRP\$>?<JJ.*>*<NN.*>+}
    CNR: {<DT>?<CD>+<NN.*>}

    #phrasal verb (multi-word verb)
    MWV: {<VB.*><EX|JJ.*|LS|NN.*|P.*|R.*|VB.*>}
    """
    cp = nltk.RegexpParser(grammar)
    result = cp.parse(sent)
    if draw:
        result.draw()
    return result

def _chunk_extractor(sent, draw=False):
    grammar = r"""
    # prepositions of place
    INF: {<IN><NN><OF>}
    INT: {<IN><TO>}

    #complement
    COMP: {<VB.*><CD|DT|EX|JJ.*|LS|NN.*|P.*|R.*|TO|VB.*>+}

    ###############################
    #         TIME PHRASES        #
    ###############################

    # time (minutes past hour)
    #DESIGN modificar para -after-
    TP_PS: {<DT>?<CD><NNS>?<JJ><CD><NN>?}
    # time (minutes to hour)
    TP_TO: {<DT>?<CD><NNS>?<TO|OF><CD><NN>?}
    # time (hour minutes)
    TP_HM: {<CD><CD><NN>?}

    # time clock (hour.minutes)
    TPCLK: {<CDT.*><NN|JJ>?}

    ###############################
    #         DATE PHRASES        #
    ###############################

    # day and part of day
    DP_DP: {<NNP><NN>}
    DP_POD: {<DT><NN><OF><DT><OD>}
    
    # day (ordinal/cardinal MOUNTH)
    DP_CD: {(<CD><NNP>)|(<NNP><CD>)}
    DP_OD: {(<DT>?<OD><OF>?<NNP>)|(<NNP><DT>?<OD>)}
    
    ###############################
    #         NOUN PHRASES        #
    ###############################

    # saxon genitive
    NP_SG: {<DT>?<JJ.*>*<NN.*>+<POS><JJ.*>*<NN.*>+}
    
    # non personal or animal possession
    NP_NPP: {<DT|PRP\$>?<JJ.*>*<NN.*>+<OF><DT>?<JJ.*>*<NN.*>+}
    
    ## length of time (day-hour-minute-second)
    LOT: {<CD><NN(S)?>(<CC|,><CD><NN(S)?>)*}
    
    # noun phrase simple
    NP_S: {<DT|PRP\$>?<JJ.*>*<NN.*>+}
    
    ###############################
    #    PREPOSITIONAL PHRASES    #
    ###############################
    
    # prepositional connecting phrase
    PREP_CON: {<IN.*><NP.*|DP.*|TP.*>(<CC|,><NP.*|DP.*|TP.*>)+}
    
    # prepositional FROM/TO phrase
    PREP_FTO: {<FROM|TO><NP.*|DP.*|TP.*>}
    
    # prepositional noun phrase
    PRENP: {<IN.*><NP.*>}
    
    # prepositional time phrase
    PRETP: {<IN.*><TP.*>}
    
    # prepositional date phrase
    PREDP: {<IN.*><DP.*|LOT>}
    
    # prepositional date-time phrase
    PREDTP: {(<PRETP><PREDP>)|(<PREDP><PRETP>)}
    """
    cp = nltk.RegexpParser(grammar)
    result = cp.parse(sent)
    if draw:
        result.draw()
    return result

def _time_without_a_preposition(sent):
    """
    Build date in expressions of time without a preposition.
    
    :param phrase: sequence of tagged tokens
    :type phrase: nltk.tree.Tree
    :return: the quantity of words and the date
    :type: tuple(int,datetime)
    
    >>> tree=nltk.Tree('IMP_A', [('stop','VB'), ('tomorrow','NN')])
    >>> _time_without_a_preposition(tree)
    (1, datetime.datetime(2015, 3, 28, 0, 0))
    """
    grammar = r"""
    TWP_2: {<NN><DT|JJ|NN>}
    TWP_4: {<NN><IN><NN><DT>}
    TWP_1: {<NN>}
    """
    sent.reverse()
    cp = nltk.RegexpParser(grammar)
    sent = cp.parse(sent)
    sent=sent[0]
    today=datetime.today()
    day=None
    lenght=0
    try:
        if sent.label()=='TWP_4' and sent[2][0]=='day':
            lenght=4
            if sent[0][0].lower() in ['tomorrow','yesterday']:
                if sent[1][0].lower()=='after':
                    day=today+timedelta(days=1)
                elif sent[1][0].lower()=='before':
                    day=today+timedelta(days=-1)
                day=datetime(day.year,
                             day.month,
                             day.day)
        elif sent.label()=='TWP_2':
            lenght=2
            if sent[1][1] in ['DT','NN']:
                #---- part of day ----
                try:
                    data1=int(utils.keyword(sent[0],'part_of_day'))
                    #---- make date ----
                    if data1!=None:
                        if sent[1][0]=='this': 
                            day=datetime(today.year,
                                         today.month,
                                         today.day,
                                         data1)
                        elif sent[1][0]=='yesterday': 
                            day=datetime(today.year,
                                         today.month,
                                         today.day,
                                         data1)+timedelta(days=-1)
                        elif sent[1][0]=='tomorrow': 
                            day=datetime(today.year,
                                         today.month,
                                         today.day,
                                         data1)+timedelta(days=1)
                except: pass
                if not day:
                    sent.set_label('TWP_1')
            elif sent[1][1]=='JJ':
                mod=None
                if sent[1][0]=='next':
                    mod=1
                elif sent[1][0]=='last':
                    mod=-1
                if mod:
                    #---- part of day ----
                    try:
                        data1=int(utils.keyword(sent[0],'part_of_day'))
                        #---- make date ----
                        if data1!=None:
                            day=datetime(today.year,
                                         today.month,
                                         today.day,
                                         data1)+timedelta(days=mod)
                    except: pass
                    try:
                        w=d=h=m=s=0
                        if sent[0][0]=='week':
                            w=mod
                        elif sent[0][0]=='day':
                            d=mod
                        elif sent[0][0]=='hour':
                            h=mod
                        elif sent[0][0]=='minute':
                            m=mod
                        elif sent[0][0]=='second':
                            s=mod
                        if w or (d or (h or (m or s))):
                            day=today+timedelta(days=d,
                                                seconds=s,
                                                minutes=m,
                                                hours=h,
                                                weeks=w)
                    except: pass
                if not day:
                    sent.set_label('TWP_1')
        if sent.label()=='TWP_1':
            lenght=1
            if sent[0][0]=='yesterday':
                today=today+timedelta(days=-1)
                day=datetime(today.year,
                             today.month,
                             today.day)
            elif sent[0][0]=='today':
                day=datetime(today.year,
                             today.month,
                             today.day)
            elif sent[0][0]=='tonight':
                day=datetime(today.year,
                             today.month,
                             today.day,19)
            elif sent[0][0]=='tomorrow':
                today=today+timedelta(days=1)
                day=datetime(today.year,
                             today.month,
                             today.day)
    except: return None
    if day:
        return (lenght,day)
    return None

def _rebuild_place(chunk_phrase):
    """
    Build place.
    
    :param phrase: sequence of tagged tokens
    :type phrase: nltk.tree.Tree
    :return: place
    :type: str
    
    >>> tree=nltk.Tree('NP_S', [('the','DT'), ('house','NN')])
    >>> _rebuild_place(tree)
    'house'
    """
    #DESIGN hacer para LOT y agregar otros
    words=[]
    #---- join all except the first item (DT) ----
    if chunk_phrase.label() in ['DP_POD','DP_OD','NP_SG','NP_NPP','NP_S','TP_PS','TP_TO']:
        if chunk_phrase[0][1]=='DT':
            for chunk in chunk_phrase[1:]:
                words.append(chunk[0])
        elif chunk_phrase[0][1]=='PRP$':
            for chunk in chunk_phrase[1:]:
                words.append(chunk[0])
            if chunk_phrase[0][0]=='my':
                words.append('of')
                words.append(base.USER)
            elif PRAGMATIC_SUBJECT:
                words.append('of')
                words.append(PRAGMATIC_SUBJECT)
        else:
            for chunk in chunk_phrase:
                words.append(chunk[0])
    #---- split all ---- {<CD><NN(S)?>(<CC|,><CD><NN(S)?>)*}
    elif chunk_phrase.label()=='LOT':
        pass
    #---- TO complement ----
    elif chunk_phrase.label()=='CTO':
        #---- with 'the' ----
        if chunk_phrase[1][1]=='DT':
            for chunk in chunk_phrase[2:]:
                words.append(chunk[0])
        #---- with possesive pronoun ----
        elif chunk_phrase[1][1]=='PRP$':
            for chunk in chunk_phrase[2:]:
                words.append(chunk[0])
            if chunk_phrase[1][0]=='my':
                words.append('of')
                words.append(base.USER)
            elif PRAGMATIC_SUBJECT:
                words.append('of')
                words.append(PRAGMATIC_SUBJECT)
        #---- without 'the' ----
        else:
            for chunk in chunk_phrase[1:]:
                words.append(chunk[0])
    #---- join all (DP_DP, DP_CD) ----
    else:
        for chunk in chunk_phrase:
            words.append(chunk[0])
    if words==[]:
        return None
    else:
        return ' '.join(words)

def _rebuild_time(phrase):
    """
    Build time.
    
    :param phrase: sequence of tagged tokens
    :type phrase: nltk.tree.Tree
    :return: time
    :type: datetime
    
    >>> tree=nltk.Tree('TPCLK', [('4:00','CDT'), ('pm','NN')])
    >>> _rebuild_time(tree)
    datetime.datetime(2015, 2, 27, 16, 0)
    """
    today=datetime.today()
    data1=None
    data2=None
    #==== time phrases ====
    if phrase.label()[:3]=='TP_':
        #---- get numbers ----
        for chunk in phrase:
            if chunk[1]=='CD':
                if data1:
                    data2=chunk[0]
                    break
                else:
                    data1=chunk[0]
        #---- convert numbers ----
        if data1 and data2:
            try:
                data1=int(data1)
                data2=int(data2)
                #---- am/pm ----
                pm=0
                if phrase[-1][0]=='pm':
                   pm=12 
                #---- make time ----
                if phrase.label()=='TP_PS':
                    return datetime(today.year,
                                    today.month,
                                    today.day,
                                    data2+pm,data1)
                elif phrase.label()=='TP_HM':
                    return datetime(today.year,
                                    today.month,
                                    today.day,
                                    data1+pm,data2)
                elif phrase.label()=='TP_TO':
                    return datetime(today.year,
                                    today.month,
                                    today.day,
                                    data2-1+pm,60-data2)
            except: return None
    #==== hh:mm (am/pm)? or hh o'clock  ====
    elif phrase.label()=='TPCLK':    
        if phrase[0][1]=='CDT':
            #---- hour and minutes ----
            try:
                data1=int(phrase[0][0][:-3])
                data2=int(phrase[0][0][-2:])
            except: return None
            #---- am/pm ----
            try:
                if phrase[1][1]=='NN':
                    if phrase[1][0]=='pm':
                        data1=data1+12
            except: pass
        elif phrase[0][1]=='CDTM':
            #---- hour and minutes ----
            try:
                data1=int(phrase[0][0][:-5])
                data2=int(phrase[0][0][-4:-2])
                #---- am/pm ----
                if phrase[0][0][-2:]=='pm':
                    data1=data1+12
            except: return None
        elif phrase[0][1]=='CDTO':
            #---- hour ----
            try:
                data1=int(phrase[0][0])
                data2=0
            except: return None
        #---- make time ----
        try:
            day=datetime(today.year,
                         today.month,
                         today.day,
                         data1,data2)
            delta=day-today
            if delta.days<0:
                return day+timedelta(days=1)
            return day
        except: return None
    return None
    
def _rebuild_date(phrase,parameter=''):
    """
    Build date.
    
    :param phrase: sequence of tagged tokens
    :type phrase: nltk.tree.Tree
    :param parameter: preposition
    :type: str
    :return: date
    :type: datetime
    
    >>> tree=nltk.Tree('DP_OD', [('22nd','OD'), ('June','NNP')])
    >>> _rebuild_date(tree,'on')
    datetime.datetime(2015, 6, 22, 0, 0)
    """
    today=datetime.today()
    data1=None
    data2=None
    #### LENGTH OF TIME ####
    if phrase.label()=='LOT':
        try:
            value=0
            w=d=h=m=s=0
            for chunk in phrase:
                if chunk[1]=='CD':
                    value=int(chunk[0])
                elif chunk[1][:2]=='NN':
                    if chunk[0] in ['week','weeks']:
                        w=value
                    elif chunk[0] in ['day','days']:
                        d=value
                    elif chunk[0] in ['hour','hours']:
                        h=value
                    elif chunk[0] in ['minute','minutes']:
                        m=value
                    elif chunk[0] in ['second','seconds']:
                        s=value
            return today+timedelta(days=d,
                                   seconds=s,
                                   minutes=m,
                                   hours=h,
                                   weeks=w)
        except: return None
    #### AT PREPOSITION ####
    if parameter=='at':
        #==== OTHERS ====
        if phrase.label()=='NP_S' and len(phrase)==1:
            try:
                #---- at BREAKFAST ----
                if phrase[0][0]=='breakfast':
                    day=datetime(today.year,
                                 today.month,
                                 today.day,7)
                #---- at NIGTH ----
                elif phrase[0][0]=='nigth':
                    day=datetime(today.year,
                                 today.month,
                                 today.day,19)
                #---- make date ----
                delta=day-today
                if delta.days<0:
                    today=today+timedelta(days=1)
                return datetime(today.year,
                                today.month,
                                today.day,
                                day.hour)
            except: return None
    #### IN PREPOSITION ####
    elif parameter=='in':
        if phrase.label()=='NP_S':
            #==== LONGER PERIODS (month, season) ====
            if len(phrase)==1:
                #---- MONTH ---- 
                try:
                    data1=int(utils.keyword(phrase[0],'month'))
                    delta=data1-today.month
                    if delta==0:
                        return today+timedelta(minutes=1)
                    elif delta<0:
                        return datetime(today.year+1,data1,1)
                    else:
                        return datetime(today.year,data1,1)
                except: pass
                #---- SEASON (meteorological method: North) ----
                #DESIGN revisar si la fecha actual esta en la estacion
                try:
                    #---- season ----
                    if phrase[0][0]=='spring':
                        day=datetime(today.year,3,1)
                    elif phrase[0][0]=='summer':
                        day=datetime(today.year,6,1)
                    elif phrase[0][0]=='autumn':
                        day=datetime(today.year,9,1)
                    elif phrase[0][0]=='winter':
                        day=datetime(today.year,12,1)
                    #---- make date ----
                    delta=day-today
                    if delta.days<0:
                        return datetime(day.year+1,day.month,day.day)
                    return day
                except: pass
            #==== PART OF DAY ====
            if len(phrase)==2:
                try:
                    #---- part of day ----
                    data1=int(utils.keyword(phrase[1],'part_of_day'))
                    #---- make date ----
                    if data1!=None:
                        if data1-today.hour<0:
                            today=today+timedelta(days=1)
                        return datetime(today.year,
                                        today.month,
                                        today.day,
                                        data1)
                except: return None
    #### ON PREPOSITION ####
    elif parameter=='on':
        #==== DAY ====
        if phrase.label() in ['DP_CD','DP_OD']:
            try:
                #---- day and month ----
                for chunk in phrase:
                    #---- day ----
                    if chunk[1]=='CD':
                        data1=int(chunk[0])
                    elif chunk[1]=='OD':
                        data1=int(chunk[0][:-2])
                    #---- month ----
                    elif chunk[1]=='NNP':
                        data2=int(utils.keyword(chunk,'month'))
                #---- make date ---
                if data1 and data2:
                    delta=datetime(today.year,data2,data1)-today
                    if delta.days<0:
                        return datetime(today.year+1,data2,data1)
                    else:
                        return datetime(today.year,data2,data1)
            except: return None
        elif phrase.label()=='NP_S' and len(phrase)==1:
            #---- DAY ---- 
            if phrase[0][1]=='NNP':
                data1=int(utils.keyword(phrase[0],'day'))
            try:
                if data1:
                    delta=data1-today.isoweekday()
                    if delta<=0:
                        delta=delta+7
                    day=today+timedelta(days=delta)
                    return datetime(day.year,
                                    day.month,
                                    day.day)
            except: return None
        #==== DAY and PART OF DAY ====
        elif phrase.label()=='DP_DP':
            try:
                #---- day and part of day ----
                for chunk in phrase:
                    #---- day ----
                    if chunk[1]=='NNP':
                        data1=int(utils.keyword(chunk,'day'))
                    #---- part of day ----
                    elif chunk[1]=='NN':
                        data2=int(utils.keyword(chunk,'part_of_day'))
                #---- make date ---
                if data1 and data2!=None:
                    delta=data1-today.isoweekday()
                    if delta<=0:
                        delta=delta+7
                    day=today+timedelta(days=delta)
                    return datetime(day.year,
                                    day.month,
                                    day.day,
                                    data2)
            except: return None
        elif phrase.label()=='DP_POD':
            #DESIGN revisar y ajustar defase
            try:
                #---- day and part of day ----
                for chunk in phrase:
                    #---- day ----
                    if chunk[1]=='OD':
                        data1=int(chunk[0][:-2])
                    #---- part of day ----
                    elif chunk[1]=='NN':
                        data2=int(utils.keyword(chunk,'part_of_day'))
                #---- make date ----
                if data1 and data2!=None:
                    delta=data1-today.day
                    if delta<=0:
                        if today.month<12:
                            month=today.month+1
                            year=today.year
                        else:
                            month=1
                            year=today.year+1
                        return datetime(year,month,
                                        data1,data2)
                    else:
                        return datetime(today.year,
                                        today.month,
                                        data1,data2)                
            except: return None
    #### OTHERS PREPOSITIONS ####
    else:
        #==== PART OF DAY, DAY, MONTH, SEASON & OTHERS ====
        #DESIGN terminar        
        if phrase.label()=='NP_S':
            det=adj=noun=None
            for chunk in phrase:          
                if chunk[1]=='DT' and chunk[0] in ['a','that','this']:
                    det=chunk[0]
                elif chunk[1]==('next','JJ'):
                    adj=1
                elif chunk[1]==('last','JJ'):
                    adj=-1
                elif chunk[1]==('few','JJ'):
                    try: adj=adj*2
                    except: adj=2
                elif chunk[1][:2]=='NN':
                    noun=chunk
            #---- length of time ----
            try:            
                if noun[0] in ['week','weeks']:
                    if det=='a':
                        return today+timedelta(weeks=1)
                elif noun[0] in ['day','days']:
                    if det=='a':                    
                        return today+timedelta(days=1)
                elif noun[0] in ['hour','hours']:
                    if det=='a':
                        return today+timedelta(hours=1)
                elif noun[0] in ['minute','minutes']:
                    if det=='a':
                        return today+timedelta(minutes=1)
                elif noun[0] in ['second','seconds']:
                    if det=='a':
                        return today+timedelta(seconds=1)
            except: return None
            #---- part of day ----
            try:
                data1=int(utils.keyword(noun,'part_of_day'))
                if data1!=None:
                    if data1-today.hour<0:
                        today=today+timedelta(days=1)
                    return datetime(today.year,
                                    today.month,
                                    today.day,
                                    data1)
            except: pass
            #---- day ---
            try:
                data1=int(utils.keyword(noun,'day'))
                if data1:
                    delta=data1-today.isoweekday()
                    if delta<=0:
                        delta=delta+7
                    day=today+timedelta(days=delta)
                    return datetime(day.year,
                                    day.month,
                                    day.day)
            except: pass
            #---- month ----
            try:
                data1=int(utils.keyword(noun,'month'))
                delta=data1-today.month
                if delta==0:
                    return today+timedelta(minutes=1)
                elif delta<0:
                    return datetime(today.year+1,data1,1)
                else:
                    return datetime(today.year,data1,1)
            except: pass
            #---- season ----
            try:
                #---- season ----
                if phrase[0][0]=='spring':
                    day=datetime(today.year,3,1)
                elif phrase[0][0]=='summer':
                    day=datetime(today.year,6,1)
                elif phrase[0][0]=='autumn':
                    day=datetime(today.year,9,1)
                elif phrase[0][0]=='winter':
                    day=datetime(today.year,12,1)
                #---- make date ----
                delta=day-today
                if delta.days<0:
                    return datetime(day.year+1,day.month,day.day)
                return day
            except: pass
            #---- others ----
            try:
                #---- BREAKFAST ----
                if phrase[0][0]=='breakfast':
                    day=datetime(today.year,
                                 today.month,
                                 today.day,7)
                #---- NIGTH ----
                elif phrase[0][0]=='nigth':
                    day=datetime(today.year,
                                 today.month,
                                 today.day,19)
                #---- make date ----
                delta=day-today
                if delta.days<0:
                    today=today+timedelta(days=1)
                return datetime(today.year,
                                today.month,
                                today.day,
                                day.hour)
            except: pass
        
        
        #==== DAY ====
        elif phrase.label() in ['DP_CD','DP_OD']:
            try:
                #---- day and month ----
                for chunk in phrase:
                    #---- day ----
                    if chunk[1]=='CD':
                        data1=int(chunk[0])
                    elif chunk[1]=='OD':
                        data1=int(chunk[0][:-2])
                    #---- month ----
                    elif chunk[1]=='NNP':
                        data2=int(utils.keyword(chunk,'month'))
                #---- make date ---
                if data1 and data2:
                    delta=datetime(today.year,data2,data1)-today
                    if delta.days<0:
                        return datetime(today.year+1,data2,data1)
                    else:
                        return datetime(today.year,data2,data1)
            except: pass
        #==== DAY and PART OF DAY ====
        elif phrase.label()=='DP_DP':
            try:
                #---- day and part of day ----
                for chunk in phrase:
                    #---- day ----
                    if chunk[1]=='NNP':
                        data1=int(utils.keyword(chunk,'day'))
                    #---- part of day ----
                    elif chunk[1]=='NN':
                        data2=int(utils.keyword(chunk,'part_of_day'))
                #---- make date ---
                if data1 and data2!=None:
                    delta=data1-today.isoweekday()
                    if delta<=0:
                        delta=delta+7
                    day=today+timedelta(days=delta)
                    return datetime(day.year,
                                    day.month,
                                    day.day,
                                    data2)
            except: pass
        elif phrase.label()=='DP_POD':
            #DESIGN revisar y ajustar defase
            try:
                #---- day and part of day ----
                for chunk in phrase:
                    #---- day ----
                    if chunk[1]=='OD':
                        data1=int(chunk[0][:-2])
                    #---- part of day ----
                    elif chunk[1]=='NN':
                        data2=int(utils.keyword(chunk,'part_of_day'))
                #---- make date ----
                if data1 and data2!=None:
                    delta=data1-today.day
                    if delta<=0:
                        if today.month<12:
                            month=today.month+1
                            year=today.year
                        else:
                            month=1
                            year=today.year+1
                        return datetime(year,month,
                                        data1,data2)
                    else:
                        return datetime(today.year,
                                        today.month,
                                        data1,data2)                
            except: return None
        pass
    return None
    
def _place_or_time(chunk_phrase):
    for chunk in chunk_phrase:
        if utils.keyword(chunk,'time'):
            return 'time'
    return 'place'

def _chunk_process(chunk_phrase):
    #==== numeric complement ====
    if chunk_phrase.label()=='CNR':
        param={}
        #chunk_phrase=chunk_phrase.leaves()
        for chunk in chunk_phrase:
            #---- numeric value ----
            if chunk[1]=='CD':
                if chunk[0].endswith('º'):
                    try:
                        param['value']=float(chunk[0][:len(chunk[0])-1])
                        param['unit']='º'
                    except: pass
                elif chunk[0].endswith('m'):
                    try:
                        param['value']=float(chunk[0][:len(chunk[0])-1])
                        param['unit']='m'
                    except: pass
                elif chunk[0].endswith('s'):
                    try:
                        param['value']=float(chunk[0][:len(chunk[0])-1])
                        param['unit']='s'
                    except: pass
                else:
                    try:
                        param['value']=float(chunk[0][:len(chunk[0])])
                    except: pass
            #---- unit ----
            elif chunk[1] in ['NN','NNS','NNP','NNPS']:
                unit=utils.keyword(chunk,'unit')
                if unit:
                    if len(param.keys()) is 1:
                            param['unit']=unit
        if len(param.keys()) is 2:
            return param
    #==== to- complement ====
    if chunk_phrase.label()=='CTO':
        param={}
        for chunk in chunk_phrase:
            if chunk[1] in ['NN','NNS','NNP','NNPS']:
                c=utils.keyword(chunk,'mwv')
                if c:
                    param['mod']=c
                else:
                    param['pos']='to'
                    param['place']=_rebuild_place(chunk_phrase)
                    return ('PLACE',param)
        if param!={}:
            return param
    return {}

############ PROCESS ############

def _extractor_of_commands(sent, robot=True):
    """
    Extractor of commands based in the grammar (VERB + COMPLEMENT)
    """
    _COMMANDS={}
    p_action=None
    #---- main action ---- 
    if robot:
        action=utils.keyword(sent[0])
        if not action:
            return []
    else:
        action=utils.keyword(sent[0],'action_place')
        if action=='N-S-A':
            return []
    #---- VERB ----
    if len(sent) is 1:
        pass
    #---- VERB + COMPLEMENT ----
    else:
        #copy_sent=sent.copy()
        copy_sent=sent[:]
        d=_time_without_a_preposition(copy_sent)
        if type(d) is tuple:        
            sent=sent[:len(sent)-d[0]]
            _COMMANDS['TIME']={'pos':'on','time':d[1]}
        complement=_chunk_extractor(sent,base.DRAW)

        fmto=False
        FMTO={}
        FMTO_LABEL=False
        for comp in complement:
            if type(comp) is tuple:
                pass
            elif type(comp) is nltk.tree.Tree:
                #==== complement ====
                if comp.label()=='COMP' and robot:
                    parameters={}
                    verb_comp=_chunk_imperative_complement(comp,base.DRAW)
                    for c in verb_comp:
                        if type(c) is nltk.tree.Tree:
                            #---- phrasal verb ----
                            if c.label()=='MWV':
                                modifier=utils.keyword(c[1],'mwv')
                                if modifier:
                                    parameters['mod']=modifier
                            #---- numeric complement ----
                            elif c.label()=='CNR':
                                parameters.update(_chunk_process(c))
                            #---- to- complement ----
                            elif c.label()=='CTO':
                                cto=_chunk_process(c)
                                if type(cto) is tuple:
                                    _COMMANDS['PLACE']=cto[1]
                                else:
                                    parameters.update(cto)
                        elif type(c) is tuple:
                            if c[1] in ['NN','NNS','NNP','NNPS']:
                                if utils.keyword(c):
                                    p_action=utils.keyword(c)
                    if parameters!={}:
                        _COMMANDS['ACTION']=parameters
                
                #==== PREPOSITIONAL NOUN/DATE PHRASE ====
                elif comp.label() in ['PRENP','PREDP']:
                    #---- preposition ----
                    if type(comp[0]) is tuple:
                        prep=utils.keyword(comp[0],'preposition')
                    elif type(comp[0]) is nltk.tree.Tree:
                        if comp[0].label()=='INF':
                            comp[0][0]='in front of'
                            prep='place'
                        elif comp[0].label()=='INT':
                            comp[0][0]=comp[0][0][0]+' to'
                            prep='place'
                    if prep in ['at','in','on','place-time']:
                        prep=_place_or_time(comp[1])
                    #---- from/to (finishes) ----
                    if fmto: 
                        if prep==FMTO['pos'] and comp[0][0] in ['till','until','through']:
                            FMTO_LABEL=True
                            prep=None
                        else:
                            fmto=False
                    #---- local variables ----
                    parameters={'pos':comp[0][0].lower()}
                    #---- PLACE ----
                    if prep=='place':
                        parameters['place']=_rebuild_place(comp[1])
                        _COMMANDS['PLACE']=parameters
                    #---- DATE ----
                    elif prep=='time':
                        t=_rebuild_date(comp[1],prep)
                        if t:
                            parameters['time']=t
                            _COMMANDS['TIME']=parameters
                #==== PREPOSITIONAL TIME PHRASE ====
                elif comp.label()=='PRETP':
                    #---- preposition ----
                    if type(comp[0]) is tuple:
                        prep=utils.keyword(comp[0],'preposition')
                    else: 
                        prep=None
                    #---- from/to (finishes) ----
                    if fmto: 
                        if prep==FMTO['pos'] and comp[0][0] in ['till','until','through']:
                            FMTO_LABEL=True
                            prep=None
                        else:
                            fmto=False
                    #---- TIME ----
                    if prep in ['time','at','place-time']:
                        t=_rebuild_time(comp[1])
                        if t:
                            parameters={'pos':comp[0][0].lower()}
                            parameters['time']=t
                            _COMMANDS['TIME']=parameters
                #==== PREPOSITIONAL DATE-TIME PHRASE ====
                elif comp.label()=='PREDTP':
                    t=d=p=prep_t=prep_dp=None
                    prep_init=None
                    parameters={}
                    for c in comp:
                        #---- TIME ----
                        if c.label()=='PRETP':
                            #---- preposition ----
                            if type(c[0]) is tuple:
                                prep=utils.keyword(c[0],'preposition')
                            elif type(c[0]) is nltk.tree.Tree:
                                prep=None
                            if prep in ['time','at']:
                                prep_t=c[0][0]
                                if not prep_init:
                                    prep_init=prep_t
                                t=_rebuild_time(c[1])
                        #---- DATE/PLACE ----
                        elif c.label()=='PREDP':
                            #---- preposition ----
                            if type(c[0]) is tuple:
                                prep=utils.keyword(c[0],'preposition')
                            elif type(c[0]) is nltk.tree.Tree:
                                if c[0].label()=='INF':
                                    c[0][0]='in front of'
                                    prep='place'
                                elif c[0].label()=='INT':
                                    c[0][0]=c[0][0][0]+' to'
                                    prep='place'
                            if prep in ['at','in','on','place-time']:
                                prep=_place_or_time(c[1])
                            prep_dp=c[0][0].lower()
                            if not prep_init:
                                prep_init=prep_dp
                            #---- place ----
                            if prep=='place':
                                p=_rebuild_place(c[1])
                            #---- date ----
                            elif prep=='time':
                                d=_rebuild_date(c[1],prep)
                    #---- bind date and time ----
                    if d and t:
                        parameters['pos']=prep_init
                        parameters['time']=datetime(d.year,
                                                    d.month,
                                                    d.day,
                                                    t.hour,
                                                    t.minute)
                        _COMMANDS['TIME']=parameters
                    elif d:
                        parameters['pos']=prep_dp
                        parameters['time']=d
                        _COMMANDS['TIME']=parameters
                    elif t:
                        parameters['pos']=prep_t
                        parameters['time']=t
                        _COMMANDS['TIME']=parameters
                    #---- place ----
                    if p:
                        parameters={}
                        parameters['pos']=prep_dp
                        parameters['place']=p
                        _COMMANDS['PLACE']=parameters
                #==== PREPOSITIONAL CONNECTING PHRASE ====
                elif comp.label()=='PREP_CON':
                    #---- preposition ----
                    if type(comp[0]) is tuple:
                        prep=utils.keyword(comp[0],'preposition')
                    elif type(comp[0]) is nltk.tree.Tree:
                        if comp[0].label()=='INF':
                            comp[0][0]='in front of'
                            prep='place'
                        elif comp[0].label()=='INT':
                            comp[0][0]=comp[0][0][0]+' to'
                            prep='place'
                    if prep in ['at','in','on','place-time']:
                        prep=_place_or_time(comp[1])
                        for c in comp[2:]:
                            if type(c) is nltk.tree.Tree:
                                if c.label()[:2]=='TP':
                                    if prep!='time':
                                        prep='place'
                                        break
                                elif _place_or_time(c)!=prep:
                                    prep='place'
                                    break
                    #---- local variables ----
                    item_list=[]
                    connecting=True
                    #---- PLACE ----
                    if prep=='place':
                        for c in comp[1:]:
                            if type(c) is tuple and c[0]=='or':
                                connecting=False
                                break
                            elif type(c) is nltk.tree.Tree:
                                item_list.append(_rebuild_place(c))
                    #---- DATE ----
                    elif prep=='time':
                        for c in comp:
                            if type(c) is tuple and c[0]=='or':
                                connecting=False
                                break
                            elif type(c) is nltk.tree.Tree:
                                #---- time ----
                                if c.label()[:2]=='TP':
                                    time=_rebuild_time(c)
                                #---- date ----
                                else:
                                    time=_rebuild_date(c)
                                #---- check ----
                                if time:
                                    item_list.append(time)
                                else:
                                    item_list=[]
                                    break
                    if item_list:
                        parameters={'pos':comp[0][0].lower()}
                        if connecting:
                            parameters[prep]=item_list
                        else:
                            parameters[prep]=item_list[0]
                        _COMMANDS[prep.upper()]=parameters
                        
                #==== PREPOSITIONAL FROM/TO PHRASE ====
                if comp.label()=='PREP_FTO' or FMTO_LABEL:
                    #---- preposition FROM ----
                    if comp[0][1]=='FROM':
                        #---- time ----
                        if comp[1].label()[:2]=='TP':
                            fmto=_rebuild_time(comp[1])
                            FMTO['pos']='time'
                        #---- place ----
                        elif _place_or_time(comp[1])=='place':
                            fmto=_rebuild_place(comp[1])
                            FMTO['pos']='place'
                        #---- date ----
                        else:
                            fmto=_rebuild_date(comp[1])
                            FMTO['pos']='time'
                        #---- make dict ----
                        if fmto:
                            FMTO['value']=[fmto]
                            fmto=True
                        else:
                            FMTO={}
                            fmto=False                        
                    #---- preposition TO ----
                    elif comp[0][1]=='TO' or FMTO_LABEL:
                        if fmto:
                            #---- time ----
                            if comp[1].label()[:2]=='TP':
                                if FMTO['pos']=='time':
                                    fmto=_rebuild_time(comp[1])
                                    if fmto:
                                        FMTO['value'].append(fmto)
                            #---- place ----
                            elif _place_or_time(comp[1])=='place':
                                if FMTO['pos']=='place':
                                    fmto=_rebuild_place(comp[1])
                                    if fmto:
                                        FMTO['value'].append(fmto)
                            #---- date ----
                            else:
                                if FMTO['pos']=='time':
                                    fmto=_rebuild_date(comp[1])
                                    if fmto:
                                        FMTO['value'].append(fmto)
                            if len(FMTO['value'])==2:
                                param={'pos':'from'}
                                param[FMTO['pos']]=FMTO['value']
                                _COMMANDS[FMTO['pos'].upper()]=param
                        else:
                            parameters={'pos':comp[0][0].lower()}
                            parameters['place']=_rebuild_place(comp[1])
                            _COMMANDS['PLACE']=parameters
                        FMTO_LABEL=False
                        fmto=False
                        FMTO={}
    #==== MAKE A LIST OF COMMANDS ====
    CMD=[]
    #==== TEMPORAL RESTRICTION ====
    try:
        param={'start':None, 'end':None}
        #---- type of preposition (START) ----
        if _COMMANDS['TIME']['pos'] in ['at','in','on','since']:
            param['start']=_COMMANDS['TIME']['time']
        #---- type of preposition (END) ----
        elif _COMMANDS['TIME']['pos'] in ['till','until','for','by']:
            param['end']=_COMMANDS['TIME']['time']
        #---- type of preposition (BETWEEN) ----
        elif _COMMANDS['TIME']['pos'] in ['from','between']:
            if type(_COMMANDS['TIME']['time']) is list:
                param['start']=_COMMANDS['TIME']['time'][0]
                param['end']=_COMMANDS['TIME']['time'][-1]
            else:
                param['start']=_COMMANDS['TIME']['time']
        CMD.append(param)
    except:
        CMD.append({'start':None, 'end':None})
    #==== NOT ROBOTIC ACTIONS ====    
    if not robot:
        try:
            CMD.append(_COMMANDS['PLACE'])
        except: 
            if action:
                CMD.append(('action_place',action))
        return CMD
    #==== MOBILE ROBOTS COMMANDS ====
    #---- go to the place ----
    try:
        CMD.append(_COMMANDS['PLACE'])
    except:
        CMD.append({})
    param={}
    #---- MOVE ----
    if action=='move':
        try:
            keys=list(_COMMANDS['ACTION'].keys())
            if 'value' in keys:
                if 'unit' in keys:
                    if _COMMANDS['ACTION']['unit']=='m':
                        param['value']=_COMMANDS['ACTION']['value']
                        param['unit']=_COMMANDS['ACTION']['unit']
                else:
                    param['value']=_COMMANDS['ACTION']['value']
            if 'mod' in keys:
                #---- move forward or back ----
                if _COMMANDS['ACTION']['mod'] in ['y','-y']:
                    param['mod']=_COMMANDS['ACTION']['mod']
                #---- move to the left or right ----
                elif _COMMANDS['ACTION']['mod']=='x':
                    CMD.append({'action':'turn', 'value':90})
                elif _COMMANDS['ACTION']['mod']=='-x':
                    CMD.append({'action':'turn', 'value':-90})
        except: pass
        if param:
            param['action']='move'
            CMD.append(param)
        elif not CMD[1]:
            CMD.append({'action':'move'})
        else:
            CMD.append({'action':'stop'})
    #---- STOP ----
    elif action=='stop':
        CMD.append({'action':'stop'})
    #---- FOLLOW ----
    elif action=='follow':
        CMD.append({'action':'follow'})
    #---- SPEED ----
    elif action=='speed':
        try:
            keys=list(_COMMANDS['ACTION'].keys())
            if 'mod' in keys:
                #---- speed up or speed down ----
                if _COMMANDS['ACTION']['mod'] in ['+','-']:
                    param['mod']=_COMMANDS['ACTION']['mod']
        except: pass
        param['action']='speed'
        CMD.append(param)
    #---- TURN ----
    elif action=='turn':
        try:
            keys=list(_COMMANDS['ACTION'].keys())
            if 'value' in keys:
                if 'unit' in keys:
                    if _COMMANDS['ACTION']['unit']=='º':
                        param['value']=_COMMANDS['ACTION']['value']
                        param['unit']=_COMMANDS['ACTION']['unit']
                else:
                    param['value']=_COMMANDS['ACTION']['value']
            if 'mod' in keys:
                if not param:
                    #---- turn to the left, right or back ----
                    if _COMMANDS['ACTION']['mod']=='x':
                        param['value']=90
                    elif _COMMANDS['ACTION']['mod']=='-x':
                        param['value']=-90
                    elif _COMMANDS['ACTION']['mod']=='-y':
                        param['value']=180
                elif _COMMANDS['ACTION']['mod']=='-x':
                        param['value']=-param['value']
        except: pass
        if param:
            param['action']='turn'
            CMD.append(param)
        elif CMD[1] and CMD[1]['pos']=='in front of':
            CMD.append({'action':'turn','pos':CMD[1]['place']})
            CMD[1]=({})
        else:
            CMD.append({'action':'turn'})
    #---- MAKE ----
    elif action=='make':
        try:
            keys=list(_COMMANDS['ACTION'].keys())
            #---- MOVE ----
            if p_action=='move':
                if 'value' in keys:
                    if 'unit' in keys:
                        if _COMMANDS['ACTION']['unit']=='m':
                            param['value']=_COMMANDS['ACTION']['value']
                            param['unit']=_COMMANDS['ACTION']['unit']
                    else:
                        param['value']=_COMMANDS['ACTION']['value']
                if 'mod' in keys:
                    #---- move forward or back ----
                    if _COMMANDS['ACTION']['mod'] in ['y','-y']:
                        param['mod']=_COMMANDS['ACTION']['mod']
                    #---- move to the left or right ----
                    elif _COMMANDS['ACTION']['mod']=='x':
                        CMD.append({'action':'turn','value':90})
                    elif _COMMANDS['ACTION']['mod']=='-x':
                        CMD.append({'action':'turn','value':-90})
                param['action']='move'
                CMD.append(param)
            #---- TURN ----
            elif p_action=='turn':
                if 'value' in keys:
                    if 'unit' in keys:
                        if _COMMANDS['ACTION']['unit']=='º':
                            param['value']=_COMMANDS['ACTION']['value']
                            param['unit']=_COMMANDS['ACTION']['unit']
                    else:
                        param['value']=_COMMANDS['ACTION']['value']
                if 'mod' in keys:
                    if param=={}:
                        #---- turn to the left, right or back ----
                        if _COMMANDS['ACTION']['mod']=='x':
                            param['value']=90
                        elif _COMMANDS['ACTION']['mod']=='-x':
                            param['value']=-90
                        elif _COMMANDS['ACTION']['mod']=='-y':
                            param['value']=180
                    else:
                        if _COMMANDS['ACTION']['mod']=='-x':
                            param['value']=-param['value']
                param['action']='turn'
                CMD.append(param)
        except:
            if p_action:
                CMD.append({'action':p_action})
    return CMD
    
def _extractor_of_commands1(sent):
    """
    Extractor of commands based in the grammar (SUBJECT + VERB + COMPLEMENT)
    """
    global PRAGMATIC_SUBJECT
    #---- extract the SUBJECT ----
    for item in range(len(sent)):
        if sent[item][1][:2]=='VB':
            break
    subject=None
    if sent[0][1]=='PRP':
        subject=sent[0][0]
        if subject=='I' or subject=='i':
            subject=base.USER
        elif PRAGMATIC_SUBJECT:
            subject=PRAGMATIC_SUBJECT
    else:
        subject=_rebuild_place(nltk.Tree('NP_S',sent[:item]))
        if subject:
            PRAGMATIC_SUBJECT=subject
        else:
            PRAGMATIC_SUBJECT=''
    #---- fix the beginning of the predicate ----
    try:
        #---- future: going to ----
        if sent[item][1]=='VBG' and sent[item+1][1]=='TO':
            if sent[item+2][1][:2]=='VB':
                item=item+2
        #---- future continuous/perfect----
        elif sent[item+1][1][:2]=='VB':
                item=item+1
    except: pass
    #---- extract the place and the date ----
    CMD=_extractor_of_commands(sent[item:],False)
    #---- build the commands ----
    if len(CMD)==1 and subject:
        CMD.append({'pos':'to','place':subject})
        CMD.append({'action':'capture'})
    elif len(CMD)==2:
        if CMD[1][0]=='action_place':
            CMD.append({'pos':'to','place':CMD.pop()[1]})
        CMD.append({'action':'capture'})
    else:
        return []
    return CMD

############ GRAMMATICAL STRUCTURE #############

def imperative_affirmative(sent):
    """
    Imperative Affirmative
    
    - grammatical structure: VERB + COMPLEMENT
    - tag structure: {<VB.*> (<CD|DT|EX|IN|JJ.*|LS|NN.*|OF|P.*|R.*|TO|VB.*>(<CC><DT>?<JJ.*>*<NN.*>+)?)*}
    """
    COMMANDS=_extractor_of_commands(sent)
    if COMMANDS:
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
    print(COMMANDS)

def imperative_negative(sent):
    """
    Imperative Negative
    
    - grammatical structure: Don't + VERB + COMPLEMENT
    - tag structure: {<VBP><RB><VB.*> (<CD|DT|EX|IN|JJ.*|LS|NN.*|OF|P.*|R.*|TO|VB.*>(<CC><DT>?<JJ.*>*<NN.*>+)?)*}
    """
    COMMANDS=_extractor_of_commands(sent[2:])
    if COMMANDS:
        COMMANDS_FORBIDDEN.append(COMMANDS)
    print(COMMANDS)

def present_simple(sent):
    """
    Present Simple
    
    - grammatical structure: Do/Does + SUBJECT + VERB + COMPLEMENT?
    - tag structure: {<VB(P|Z)><PRP><VB(P)?><.*>*<\.>}
    """
    #---- 2nd person ----
    if sent[1][0]=='you':
        COMMANDS=_extractor_of_commands(sent[2:len(sent)-1])
        #---- ask for the current state ----
        try:
            answer=base.list_in_list(COMMANDS,COMMANDS_CURRENT[0])
            print('ANSWER: '+str(answer))
        except: pass
    else:
        COMMANDS=_extractor_of_commands1(sent[1:len(sent)-1])
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
    print(COMMANDS)
            
def present_continuous(sent):
    """
    Present Continuous
    
    - grammatical structure: TO BE + SUBJECT + VERB-ing + COMPLEMENT?
    - tag structure: {<VB(P|Z)><PRP><VBG><.*>*<\.>}
    """
    #---- 2nd person ----
    if sent[1][0]=='you':
        sent[2]=(lemmatizer.lemmatize(sent[2][0],'v'),'VB')
        COMMANDS=_extractor_of_commands(sent[2:len(sent)-1])
        #---- ask for the current state ----
        try:
            answer=base.list_in_list(COMMANDS,COMMANDS_CURRENT[0])
            print('ANSWER: '+str(answer))
        except: pass
    else:
        for i in range(len(sent)):
            if sent[i][1][:2]=='VB' and i:
                break
        sent[i]=(lemmatizer.lemmatize(sent[i][0],'v'),'VB')
        COMMANDS=_extractor_of_commands1(sent[1:len(sent)-1])
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
    print(COMMANDS)
    
def present_perfect(sent):
    """
    Present Perfect
    
    - grammatical structure: Have/Has + SUBJECT + VERB(past participle) + COMPLEMENT?
    - tag structure: {<VB(P|Z)><PRP><RB>?<VBD><.*>*<\.>}
    """
    #---- 2nd person ----
    if sent[1][0]=='you':
        answer=False
        if sent[2][0]=='ever':
            sent[3]=(lemmatizer.lemmatize(sent[3][0],'v'),'VB')
            COMMANDS=_extractor_of_commands(sent[3:len(sent)-1])
            print(COMMANDS)
            #---- ask for the previous states ----
            for ecmd in COMMANDS_ENDED:
                answer=answer or base.list_in_list(COMMANDS,ecmd)
                if answer:
                    break
        else:
            sent[2]=(lemmatizer.lemmatize(sent[2][0],'v'),'VB')
            COMMANDS=_extractor_of_commands(sent[2:len(sent)-1])
            print(COMMANDS)
            #---- ask for the first previous states ----
            try:
                answer=base.list_in_list(COMMANDS,COMMANDS_ENDED[-1])
            except: pass
        print('ANSWER: '+str(answer))
    
def present_perfect_continuous(sent):
    """
    Present Perfect Continuous
    
    - grammatical structure: Have/Has + SUBJECT + been + VERB-ing + COMPLEMENT?
    - tag structure: {<VB(P|Z)><PRP><VBN><VBG><.*>*<\.>}
    """
    #---- 2nd person ----
    if sent[1][0]=='you':
        sent[2]=(lemmatizer.lemmatize(sent[3][0],'v'),'VB')
        COMMANDS=_extractor_of_commands(sent[3:len(sent)-1])
        print(COMMANDS)
        #---- ask for the first previous states ----
        try:
            answer=base.list_in_list(COMMANDS,COMMANDS_ENDED[-1])
            print('ANSWER: '+str(answer))
        except: pass
    
def past_simple(sent):
    """
    Past Simple
    
    - grammatical structure: Did + SUBJECT + VERB + COMPLEMENT?
    - tag structure: {<VBD><PRP><VB(P)?><.*>*<\.>}
    """
    #---- 2nd person ----
    if sent[1][0]=='you':
        COMMANDS=_extractor_of_commands(sent[2:len(sent)-1])
        print(COMMANDS)
        #---- ask for the previous states ----
        answer=False
        for ecmd in COMMANDS_ENDED:
            answer=answer or base.list_in_list(COMMANDS,ecmd)
            if answer:
                break
        print('ANSWER: '+str(answer))

def past_continuous(sent):
    """
    Past Continuous
    
    - grammatical structure: Was/Were + SUBJECT + VERB-ing + COMPLEMENT?
    - tag structure: {<VBD><PRP><VBG><.*>*<\.>}
    """
    #---- 2nd person ----
    if sent[1][0]=='you':
        sent[2]=(lemmatizer.lemmatize(sent[2][0],'v'),'VB')
        COMMANDS=_extractor_of_commands(sent[2:len(sent)-1])
        print(COMMANDS)
        #---- ask for the previous states ----
        answer=False
        for ecmd in COMMANDS_ENDED:
            answer=answer or base.list_in_list(COMMANDS,ecmd)
            if answer:
                break
        print('ANSWER: '+str(answer))

def past_perfect(sent):
    """
    Past Perfect
    
    - grammatical structure: Had + SUBJECT + VERB(past participle) + COMPLEMENT?
    - tag structure: {<VBD><PRP><VBD><.*>*<\.>}
    """
    for i in range(len(sent)):
        if sent[i]==('when','WRB'):
            break
    answer=False
    #==== without past simple ====
    if i==len(sent)-1:
        #---- 2nd person ----
        if sent[1][0]=='you':
            sent[2]=(lemmatizer.lemmatize(sent[2][0],'v'),'VB')
            COMMANDS=_extractor_of_commands(sent[2:len(sent)-1])
            print(COMMANDS)
            #---- ask for the previous states ----
            for ecmd in COMMANDS_ENDED:
                answer=answer or base.list_in_list(COMMANDS,ecmd)
                if answer:
                    break
    #==== combine with past simple ====
    else:
        #---- 2nd person ----
        if sent[1][0]=='you' and sent[i+1][0]=='you':
            sent[2]=(lemmatizer.lemmatize(sent[2][0],'v'),'VB')
            sent[i+2]=(lemmatizer.lemmatize(sent[i+2][0],'v'),'VB')
            #---- past simple ----
            COMMANDS0=_extractor_of_commands(sent[i+2:len(sent)-1])
            #---- past perfect ----         
            COMMANDS1=_extractor_of_commands(sent[2:i])
            print(COMMANDS0)
            print(COMMANDS1)
            #---- ask for the previous states ----
            status=False
            for ecmd in COMMANDS_ENDED:
                if status:
                    status=False
                    if base.list_in_list(COMMANDS1,ecmd):
                        answer=True
                        break
                else:
                    if base.list_in_list(COMMANDS0,ecmd):
                        status=True
    print('ANSWER: '+str(answer))

def past_perfect_continuous(sent):
    """
    Past Perfect Continuous
    
    - grammatical structure: Had + SUBJECT + been + VERB-ing + COMPLEMENT?
    - tag structure: {<VBD><PRP><VBN><VBG><.*>*<\.>}
    """
    #---- 2nd person ----
    if sent[1][0]=='you':
        sent[2]=(lemmatizer.lemmatize(sent[2][0],'v'),'VB')
        COMMANDS=_extractor_of_commands(sent[2:len(sent)-1])
        print(COMMANDS)
        #---- ask for the previous states (without the last) ----
        answer=False
        try:
            for ecmd in COMMANDS_ENDED[:-1]:
                answer=answer or base.list_in_list(COMMANDS,ecmd)
                if answer:
                    break
        except: pass
        print('ANSWER: '+str(answer))

def future_going_to(sent):
    """
    Future: going to
    
    - grammatical structure: TO BE + SUBJECT + going to + VERB + COMPLEMENT?
    - tag structure: {<VB(P|Z)><PRP><VBG><TO><VB(P)?><.*>*<\.>}
    """
    if sent[1][0]=='you':
        COMMANDS=_extractor_of_commands(sent[4:len(sent)-1])
        #---- ask for the later states ----
        answer=False
        try:
            for ccmd in COMMANDS_CURRENT[1:]:
                answer=answer or base.list_in_list(COMMANDS,ccmd)
                if answer:
                    break
        except: pass
        print('ANSWER: '+str(answer))
    else:
        COMMANDS=_extractor_of_commands1(sent[1:len(sent)-1])
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
    print(COMMANDS)

def future_will(sent):
    """
    Future: will
    
    - grammatical structure: Will + SUBJECT + VERB + COMPLEMENT?
    - tag structure: {<MD><PRP><VB><.*>*<\.>}
    """
    if sent[1][0]=='you':
        COMMANDS=_extractor_of_commands(sent[2:len(sent)-1])
        #---- ask for the later states ----
        answer=False
        try:
            for ccmd in COMMANDS_CURRENT[1:]:
                answer=answer or base.list_in_list(COMMANDS,ccmd)
                if answer:
                    break
        except: pass
        print('ANSWER: '+str(answer))
    else:
        COMMANDS=_extractor_of_commands1(sent[1:len(sent)-1])
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
    print(COMMANDS)

def future_continuous(sent):
    """
    Future Continuous
    
    - grammatical structure: Will + SUBJECT + be + VERB-ing + COMPLEMENT?
    - tag structure: {<MD>(<PRP>|(<DT>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<VB><VBG><.*>*<\.>}
    """
    if sent[1][0]=='you':
        sent[3]=(lemmatizer.lemmatize(sent[3][0],'v'),'VB')
        COMMANDS=_extractor_of_commands(sent[3:len(sent)-1])
        #---- ask for the later states ----
        answer=False
        try:
            for ccmd in COMMANDS_CURRENT[1:]:
                answer=answer or base.list_in_list(COMMANDS,ccmd)
                if answer:
                    break
        except: pass
        print('ANSWER: '+str(answer))
    else:
        for i in range(len(sent)):
            if sent[i][1]=='VBG' and i:
                break
        sent[i]=(lemmatizer.lemmatize(sent[i][0],'v'),'VB')
        COMMANDS=_extractor_of_commands1(sent[1:len(sent)-1])
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
    print(COMMANDS)
    
def future_perfect(sent):
    """
    Future Perfect
    
    - grammatical structure: Will + SUBJECT + have + VERB(past participle) + COMPLEMENT?
    - tag structure: {<MD>(<PRP>|(<DT>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<VB><VBN><.*>*<\.>}
    """
    if sent[1][0]=='you':
        sent[3]=(lemmatizer.lemmatize(sent[3][0],'v'),'VB')
        COMMANDS=_extractor_of_commands(sent[3:len(sent)-1])
        #---- ask for the later states ----
        answer=False
        try:
            for ccmd in COMMANDS_CURRENT[1:]:
                answer=answer or base.list_in_list(COMMANDS,ccmd)
                if answer:
                    break
        except: pass
        print('ANSWER: '+str(answer))
    else:
        for i in range(len(sent)):
            if sent[i][1]=='VBN' and i:
                break
        sent[i]=(lemmatizer.lemmatize(sent[i][0],'v'),'VB')
        COMMANDS=_extractor_of_commands1(sent[1:len(sent)-1])
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
    print(COMMANDS)

def interrogative_Wh_questions(sent):
    """
    Interrogative: Wh-questions
    
    - grammatical structure:
    - tag structure:
    """
    #DESIGN hacer

def interrogative_to_have(sent):
    """
    Interrogative: To have
    
    - grammatical structure: Have/Has + SUBJECT + got + COMPLEMENT?
    - tag structure: {<VB(P|Z)><PRP><RB>?<VBD><.*>*<\.>}
    """
    #---- 2nd person ----
    if sent[1][0]=='you':
        pass
    else:
        COMMANDS=_extractor_of_commands1(sent[1:len(sent)-1])
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
        print(COMMANDS)

def interrogative_there(sent):
    """
    Interrogative: There is, There are
    
    - grammatical structure: Is/Are there + COMPLEMENT?
    - tag structure: {<VB(P|Z)><EX|RB><.*>*<\.>}
    """
    COMMANDS=_extractor_of_commands(sent[:len(sent)-1],False)
    try:
        if COMMANDS[-1][0]=='go':
            #---- check the forbidden command list ----
            status=False
            for fcmd in COMMANDS_FORBIDDEN:
                status=status or base.list_in_list(fcmd,COMMANDS)
                if status:
                    break
            if not status:
                COMMANDS.append(('capture',{}))
                COMMANDS_CURRENT.append(COMMANDS)
                COMMAND_CMD.append(COMMANDS)
    except: pass
    print(COMMANDS)
    
def interrogative_to_be(sent):
    """
    Interrogative: To be
    
    - grammatical structure: TO BE + SUBJECT + COMPLEMENT?
    - tag structure: {<VB(P|Z)>(<PRP>|(<DT>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))<.*>*<\.>}
    """
    #DESIGN hacer
    grammar = r"""
    SUB: {<VB(P|Z)>(<PRP>|(<DT>?<JJ.*>*<NN.*>+(<CC|POS|OF><DT>?<JJ.*>*<NN.*>+)?))}
    """
    cp = nltk.RegexpParser(grammar)
    sent = cp.parse(sent)
    sentence=[]
    if type(sent[0]) is nltk.tree.Tree:
        for item in sent[0][1:]:
            sentence.append(item)
        sentence.append(('do','VB'))
        for item in sent[1:-1]:
            sentence.append(item)
        COMMANDS=_extractor_of_commands1(sentence)
        #---- check the forbidden command list ----
        status=False
        for fcmd in COMMANDS_FORBIDDEN:
            status=status or base.list_in_list(fcmd,COMMANDS)
            if status:
                break
        if not status:
            COMMANDS_CURRENT.append(COMMANDS)
            COMMAND_CMD.append(COMMANDS)
        print(COMMANDS)
                  
def modal_auxiliary_verb(sent):
    """
    Modal Auxiliary Verb
    
    - grammatical structure: SUBJECT + MODAL VERB + VERB + COMPLEMENT
    - tag structure: {<PRP><MD><RB>?<VB><.*>*}
    """
    if sent[0][0]=='you':
        if sent[2][1]=='RB':
            COMMANDS=_extractor_of_commands(sent[3:])
            COMMANDS_FORBIDDEN.append(COMMANDS)
        else:
            COMMANDS=_extractor_of_commands(sent[2:])
            #---- check the forbidden command list ----
            status=False
            for fcmd in COMMANDS_FORBIDDEN:
                status=status or base.list_in_list(fcmd,COMMANDS)
                if status:
                    break
            if not status:
                COMMANDS_CURRENT.append(COMMANDS)
                COMMAND_CMD.append(COMMANDS)
        print(COMMANDS)
        
def conditional_minus1(sent):
    """
    Conditional -1
    
    - grammatical structure: If PRESENT SIMPLE AFFIRMATIVE, IMPERATIVE
    - tag structure: {<IN><AFF_PRS><,><IMP_.*>}
    """
    if sent[0][0].lower()=='if':
        if sent[1][0][0]=='you':
            #---- present simple affirmative ----
            COMMANDS=_extractor_of_commands(sent[1][1:])
            if COMMANDS:
                #---- check the forbidden command list ----
                status=False
                for fcmd in COMMANDS_FORBIDDEN:
                    status=status or base.list_in_list(fcmd,COMMANDS)
                    if status:
                        break
                if not status:
                    print(COMMANDS)
                #---- imperative ----
                if sent[3].label()=='IMP_A':
                    imperative_affirmative(sent[3])
                elif sent[3].label()=='IMP_A$':
                    imperative_affirmative(sent[3][2:])
                elif sent[3].label()=='IMP_N':
                    imperative_negative(sent[3])
                elif sent[3].label()=='IMP_N$':
                    imperative_negative(sent[3][1:])

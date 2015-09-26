# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 14:01:40 2015

@author: Toni
"""

__all__=['_KEYWORDS']

_KEYWORDS={}

############# ACTIONS #############
_dict_actions ={'bend'   : 'turn',
                'turn'   : 'turn',
               
                'end '   : 'stop',
                'finish' : 'stop',
                'park'   : 'stop',
                'quit'   : 'stop',
                'rest'   : 'stop',
                'stop'   : 'stop',
                'wait'   : 'stop',  
                
                'address': 'move',
                'arrive' : 'move',
                'come'   : 'move',
                'drive'  : 'move',
                'go'     : 'move',
                'lead'   : 'move',
                'move'   : 'move',
                'run'    : 'move',
                'walk'   : 'move',
                  
                'hurry'  : 'speed',
                'speed'  : 'speed',
                
                'pursue' : 'follow',               
                'follow' : 'follow',
                
                'make'   : 'make'
                }

############# PREPOSITIONS #############
_dict_prepositions ={'at':'at',
                     'in':'in',
                     'on':'on',
                     
                     'above'  : 'place',
                     'across' : 'place',
                     'against': 'place',
                     'along'  : 'place',
                     'among'  : 'place',
                     'around' : 'place',
                     'behind' : 'place',
                     'below'  : 'place',
                     'beyond' : 'place',
                     'inside' : 'place',
                     'into'   : 'place',
                     'near'   : 'place',
                     'onto'   : 'place',
                     'outside': 'place',
                     'through': 'place',
                     'toward' : 'place',
                     'under'  : 'place',
                     
                     'after'  : 'time',
                     'before' : 'time',
                     'during' : 'time',
                     'for'    : 'time',
                     'since'  : 'time',
                     'till'   : 'time',
                     'until'  : 'time',
                     'within' : 'time',
                     
                     'between': 'place-time',
                     'by'     : 'place-time',
                     'over'   : 'place-time'
                    }
                    
############# PHRASAL VERBS #############
#       y
#    -x + x   position
#      -y
_dict_phrasal_verb ={'advance' : 'y',
                     'forward' : 'y',  
                     'straight': 'y',
                     'back'    : '-y',
                     'right'   : 'x',
                     'left'    : '-x',
                     
                     'up'      : '+',
                     'down'    : '-'
                    }

############# UNITS #############
_dict_unit ={'m'      : 'm',
             'meter'  : 'm',
             'meters' : 'm',
             
             'degree' : 'º',
             
             's'      : 's',
             'second' : 's',
             'seconds': 's',
             }



############# TIME #############
_dict_word_time ={
                'second'    : 'time',
                'seconds'   : 'time',
                'minute'    : 'time',                
                'minutes'   : 'time',                
                'hour'      : 'time',
                'hours'     : 'time',
                'day'       : 'time',
                'days'      : 'time',
                'week'      : 'time',
                'weeks'     : 'time',
                'month'     : 'time',
                'months'    : 'time',
                'year'      : 'time',
                'years'     : 'time',
                'century'   : 'time',
                'centuries' : 'time',

                'monday'    : 'time',
                'tuesday'   : 'time',
                'wednesday' : 'time',                
                'thursday'  : 'time',                
                'friday'    : 'time',
                'saturdy'   : 'time',
                'sunday'    : 'time',
                
                'january'   : 'time',
                'february'  : 'time',
                'march'     : 'time',
                'april'     : 'time',                
                'may'       : 'time',
                'june'      : 'time',
                'july'      : 'time',
                'august'    : 'time',
                'september' : 'time',
                'october'   : 'time',
                'november'  : 'time',                
                'december'  : 'time',
                
                'midnight'  : 'time',
                'morning'   : 'time',
                'midday'    : 'time',
                'noon'      : 'time',              
                'noonday'   : 'time',
                'afternoon' : 'time',
                'evening'   : 'time',
                'night'     : 'time',
                
                'spring'    : 'time',
                'summer'    : 'time',
                'autumn'    : 'time',              
                'winter'    : 'time',
                
                'yesterday' : 'time',
                'today'     : 'time',
                'tonight'   : 'time',
                'tomorrow'  : 'time'
                }
                
############# MONTH #############
_dict_word_month ={
                'january'   : '1',
                'february'  : '2',
                'march'     : '3',
                'april'     : '4',                
                'may'       : '5',
                'june'      : '6',
                'july'      : '7',
                'august'    : '8',
                'september' : '9',
                'october'   : '10',
                'november'  : '11',                
                'december'  : '12'
                }

############# DAY #############
_dict_word_day ={
                'monday'    : '1',
                'tuesday'   : '2',
                'wednesday' : '3',                
                'thursday'  : '4',                
                'friday'    : '5',
                'saturdy'   : '6',
                'sunday'    : '7'
                }
                
############# PART OF DAY #############
_dict_word_part_of_day ={
                'midnight'  : '0',
                'morning'   : '3',
                'midday'    : '12',
                'noon'      : '12',              
                'noonday'   : '12',
                'afternoon' : '16',
                'evening'   : '18',
                'night'     : '19'
                }
        
############# CARDINAL NUMBERS #############
_dict_cardinal={
                'one'          : '1',
                'two'          : '2',
                'three'        : '3',                
                'four'         : '4',                
                'five'         : '5',
                'six'          : '6',
                'seven'        : '7',
                'eight'        : '8',
                'nine'         : '9',
                'ten'          : '10',                
                'eleven'       : '11',
                'twelve'       : '12',
                'thirteen'     : '13',                
                'fourteen'     : '14',                
                'fifteen'      : '15',
                'sixteen'      : '16',
                'seventeen'    : '17',
                'eighteen'     : '18',
                'nineteen'     : '19',
                'twenty'       : '20',                               
                'twenty-one'   : '21',
                'twenty-two'   : '22',
                'twenty-three' : '23',                
                'twenty-four'  : '24',                
                'twenty-five'  : '25',
                'twenty-six'   : '26',
                'twenty-seven' : '27',
                'twenty-eight' : '28',
                'twenty-nine'  : '29',
                'thirty'       : '30',                
                'thirty-one'   : '31',
                'thirty-two'   : '32',
                'thirty-three' : '33',                
                'thirty-four'  : '34',                
                'thirty-five'  : '35',
                'thirty-six'   : '36',
                'thirty-seven' : '37',
                'thirty-eight' : '38',
                'thirty-nine'  : '39',
                'forty'        : '40',                
                'forty-one'    : '41',
                'forty-two'    : '42',
                'forty-three'  : '43',                
                'forty-four'   : '44',                
                'forty-five'   : '45',
                'forty-six'    : '46',
                'forty-seven'  : '47',
                'forty-eight'  : '48',
                'forty-nine'   : '49',
                'fifty'        : '50',                
                'fifty-one'    : '51',
                'fifty-two'    : '52',
                'fifty-three'  : '53',                
                'fifty-four'   : '54',                
                'fifty-five'   : '55',
                'fifty-six'    : '56',
                'fifty-seven'  : '57',
                'fifty-eight'  : '58',
                'fifty-nine'   : '59'
                }
                
############# ORDINAL NUMBERS #############
_dict_ordinal={
                'first'          : '1st',
                'second'         : '2nd',
                'third'          : '3rd',                
                'fourth'         : '4th',                
                'fifth'          : '5th',
                'sixth'          : '6th',
                'seventh'        : '7th',
                'eighth'         : '8th',
                'ninth'          : '9th',
                'tenth'          : '10th',                
                'eleventh'       : '11th',
                'twelfth'        : '12th',
                'thirteenth'     : '13th',                
                'fourteenth'     : '14th',                
                'fifteenth'      : '15th',
                'sixteenth'      : '16th',
                'seventeenth'    : '17th',
                'eighteenth'     : '18th',
                'nineteenth'     : '19th',
                'twentieth'      : '20th',                               
                'twenty-first'   : '21st',
                'twenty-second'  : '22nd',
                'twenty-third'   : '23rd',                
                'twenty-fourth'  : '24th',                
                'twenty-fifth'   : '25th',
                'twenty-sixth'   : '26th',
                'twenty-seventh' : '27th',
                'twenty-eighth'  : '28th',
                'twenty-ninth'   : '29th',
                'thirtieth'      : '30th',                
                'thirty-first'   : '31st'
                }
                

############# OTHERS PERSONAL ACTIONS #############
_dict_actions_place={
                    'rain'       : 'open place',
                    'snow'       : 'open place',
                    'dawn'       : 'open place',
                    
                    'fry'        : 'kitchen',
                    'cook'       : 'kitchen',
                    'swap'       : 'sink',
                    'dine'       : 'dining room',
                    'iron'       : 'bureau',
                    'phone'      : 'telephone',
                    'watch'      : 'tv',
                    'park'       : 'parking',
                    'sleep'      : 'bed',
                    'bath'       : 'bath',
                    'swim'       : 'fish pool',
                    
                    'know'       : 'N-S-A',
                    'understand' : 'N-S-A',
                    'believe'    : 'N-S-A',
                    'think'      : 'N-S-A',
                    'mean'       : 'N-S-A',
                    
                    'love'       : 'N-S-A',
                    'hate'       : 'N-S-A',
                    'like'       : 'N-S-A',
                    'prefer'     : 'N-S-A'
                    }
                
#make a dictionary
_KEYWORDS['action']=_dict_actions
_KEYWORDS['preposition']=_dict_prepositions
_KEYWORDS['mwv']=_dict_phrasal_verb
_KEYWORDS['unit']=_dict_unit

_KEYWORDS['time']=_dict_word_time
_KEYWORDS['month']=_dict_word_month
_KEYWORDS['day']=_dict_word_day
_KEYWORDS['part_of_day']=_dict_word_part_of_day

_KEYWORDS['cardinal']=_dict_cardinal
_KEYWORDS['ordinal']=_dict_ordinal

_KEYWORDS['action_place']=_dict_actions_place
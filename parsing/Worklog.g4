grammar Worklog;

wl : week+ ;

week : weekHeader NL+ weekBody ;
weekHeader : '# Week ' NUM  ;
weekBody : day+ ;

day : dayHeader NL dayInfo NL dayBody* NL* ;
dayHeader : '## ' NUM ' ' STR ' ' NUM ;
dayInfo : start NL lunch NL stop extra? NL?;

start : '- Start @ ' STR ;
extra : NL '- Extra ' STR ;

lunch
    : '- Lunch ' STR
    | '- Lunch ' STR ' (biz)'
    ;
stop : '- Stop @ ' STR ;

dayBody
    : ' '* '- ' wordWithMaybeSpace+ NL 
    | ' '* '- ' wordWithMaybeSpace+ NL additionalLine+
    ;

additionalLine
    : ' '+ wordWithMaybeSpace+ NL
    ;

wordWithMaybeSpace
    : STR ' '* 
    | NUM ' '*
    ;

NL : [\r\n]+ ;
NUM : [0-9]+ ;
STR : ~[ \t\r\n]+ ;

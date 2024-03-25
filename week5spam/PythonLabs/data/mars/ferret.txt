;redcode
;name Ferret
;author Robert R. Reed III
;strategy 1st place in ICWST'87
;assert 1
START   MOV     #4908  ,B
F       CMP     <A     ,<B
        MOV     S      ,@B
        CMP     <A     ,<B
A       MOV     S      ,-5
        DJN     F      ,B
K       MOV     W      ,<W
        DJN     K      ,<W
        ADD     #3     ,W
B       JMP     K
W       DAT     #-10
S       SPL     0
        END     START

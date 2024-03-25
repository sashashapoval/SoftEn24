;redcode
;name Chang1
;author Morrison J. Chang
;strategy 2nd place in ICWST'86
;strategy dwarf, imp-stomper, imp-gun
;assert 1
        MOV     #0     ,-1
        JMP     -1
        DAT     #9
START   SPL     -2
        SPL     4
        ADD     #-16   ,-3
        MOV     #0     ,@-4
        JMP     -4
        SPL     2
        JMP     -1
        MOV     0      ,1
        END     START

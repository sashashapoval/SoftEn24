;redcode
;name Plague
;author Ron Paludan
;strategy 2nd place in ICWST'87
;assert 1
       SPL     WIPE
       SPL     WIPE
LOOP   ADD     #24    ,PTR
       JMZ     LOOP   ,@PTR
       MOV     JBOMB  ,@PTR
       MOV     SBOMB  ,<PTR
       ADD     #1     ,PTR
       JMP     LOOP
       DAT             #1
       DAT             #2
       DAT             #3
       DAT             #4
PTR    DAT             #5
WIPE   MOV     2      ,<2
       JMP     WIPE
       DAT             #-16
JBOMB  JMP     -1
SBOMB  SPL     0
       END

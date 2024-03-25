;redcode
;name Mice
;author Chip Wendell
;strategy 1st place in ICWST'86
;strategy replicator
;assert 1
PTR     DAT             #0
START   MOV     #12    ,PTR
LOOP    MOV     @PTR   ,<COPY
        DJN     LOOP   ,PTR
        SPL     @COPY  ,0
        ADD     #653   ,COPY
        JMZ     START  ,PTR
COPY    DAT             #833
        END     START

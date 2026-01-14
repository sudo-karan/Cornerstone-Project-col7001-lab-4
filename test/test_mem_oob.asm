; Test Memory Out of Bounds
; Expected Error: Memory Access Out of Bounds

PUSH 10
STORE 6000    ; Valid indices are 0-1023 (Mem) and 1024-5119 (Heap)
HALT

# CA-lab3

- Пронина Анастасия Ильинична, P3233
- `asm | risc | harv | hw | instr | binary -> struct | trap -> stream | port | pstr | prob1 | -`
- Базовый вариант.

## Содержание

1. [Язык программирования](#язык-программирования)
2. [Организация памяти](#организация-памяти)
3. [Система команд](#система-команд)
4. [Транслятор](#транслятор)
5. [Модель процессора](#модель-процессора)
6. [Тестирование](#тестирование)

<h2 id="язык-программирования">Язык программирования ASM</h2>

``` bnf
<program> ::= <data_section> | <text_section>

<data_section> ::= "section .data" | <data_definition> | <label>

<text_section> ::= "section .text" | <command> | <label>

<data_definition> ::= "db" {<number> | <string_literal>}+

<command> ::= "ld" <reg>, <data_address>
        |    "st" <reg>, <data_address>
        |    "mov" <reg>, <reg> | <number>
        |    "add" <reg>, <reg> | <number>, <reg> | <number>
        |    "inc" <reg>
        |    "dec" <reg>
        |    "beq" <code_address>
        |    "bne" <code_address>
        |    "jmp" <code_address>
        |    "out" <reg>, <port>
        |    "in" <reg>, <port>
        |    "hlt"
        |    "cmp" <reg> | <number>, <reg> | <number>
        |    "push" <reg>
        |    "pop" <reg>
        |    "iret"
        |    "mod" <reg>, <reg> | <number>, <reg> | <number>
        |    "div" <reg>, <reg> | <number>, <reg> | <number>
        |    "printi" <reg>

<data_address> ::= <direct_address> | <indirect_address>

<direct_address> ::= <reg> | <number> | <label>

<indirect_address> ::= [<reg>] | [<number>] | [<label>]

<code_address> ::= <number> | <label>

<label> ::= <char> {<char> | <digit>}* ":"

<string_literal> ::= "'" {<char> | <digit> | <special>}+ "'"

<number> ::= {-}* {<digit>}+

<char> ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" |  "i" | "j" | "k" | "l" | "m"
           | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
           | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M"
           | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"

<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<special> ::= "\n"
```
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

### Описание семантики ASM

- Метки определяются на отдельных строчках как для памяти команд, так и для памяти данных. Далее на эти метки можно ссылаться.
- Программа выполняется последовательно начиная с адреса, обозначенного меткой _start. Заканчивается на инструкции HLT.

#### Область видимости

Все переменные, расположенные в секции .data, являются глобальными, к ним можно получить доступ из любого места программы.

<h2 id="организация-памяти">Организация памяти</h2>

### Модель памяти процессора

#### Машинное слово
- **Память данных**: 32 бита.
- **Память инструкций**: 32 бита.

#### Варианты адресации для данных
- **Абсолютная адресация**: адрес ячейки может быть указан напрямую с помощью метки или числа, а также может быть загружен из указанного регистра.
- **Относительная адресация**: адрес ячейки расположен в памяти по некоторому адресу, являющемуся непосредственным аргументом команды (число, метка, регистр). 

#### Варианты адресации для команд, не работающих с памятью
- **Регистры**: в выполнении операции принимает участие значение из указанного регистра.
- **Константы**: при выполнении операции операнд загружается напрямую из регистра команд.

### Механика отображения программы и данных на процессор
```
+----------------------+
|      Registers       |
+----------------------+
| R0                   |
| R1                   |
| R2                   |
| R3                   |
+----------------------+

+-----------------------+
|   Instruction memory  |
+-----------------------+
| 00 : instruction 1    |
| ...                   |
| n  : instruction n+1  |
| ...                   |
+-----------------------+

+-----------------------+
|      Data memory      |
+-----------------------+
| 00 : num literal      |
| ...                   |
| l  : char literal     |
| l+1: char literal     |
| ...                   |
| c  : data             |
| ...                   |
+-----------------------+
```

Память данных и память инструкций разделены. 

#### Виды памяти и регистров, доступные программисту
- **Регистры общего назначения**: R1, R2, R3, R4.
- **Память данных**: в памяти данных хранятся литералы, непосредственно определенные в `section .data`

- Операции с данными выполняются так, как будто все они являются 32-разрядными целыми числами.
- Символьные литералы хранятся в одном машинном слове, занимают младшие 8 бит.
- Все переменные, определенные в `section .data`, не являются константными и могут быть изменены в процессе работы программы.
- Относительная адресация может использоваться при работе со строками или массивами, во всех остальных случаях будет использоваться абсолютная.
- Строки в памяти хранятся в следующем виде: сначала указывается длина строки, затем идет последовательность 32-разрядных слов, каждое из которых хранит один символ (pstr).

<h2 id="система-команд">Система команд</h2>
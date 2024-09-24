# Лабораторная работа 3 по Архитектуре Компьютера

- Состанов Тимур Айратович P3314
- `lisp -> asm | acc | neum | hw | tick -> instr | struct | stream | port | pstr | prob1 | cache`
- Упрощенный вариант

## Язык программирования

### Синтаксис

```ebnf
program ::= { line }

line ::= label [ comment ] "\n"
       | instr [ comment ] "\n"
       | [ comment ] "\n"

label ::= label_name ":"

instr ::= op0 
        | op1 arg
        | "WORD" word_data

op0 ::= "CLA"
      | "INC"
      | "DEC"
      | "HLT"
      | "NOT"
      | "NEG"
      

op1 ::= "ST"
      | "LD"
      | "CMP"
      | "JZ"
      | "JMP"
      | "IN"
      | "OUT"
      | "DIV"
      | "MUL"
      | "ADD"
      | "SUB"
      | "AND"
      | "OR"
      | "XOR"
      

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

comment ::= ";" <any symbols except "\n">

word_data ::= number | string

arg ::= label_name | ( label_name ) | number | #number

variable ::= number | label_name

string ::= "\"" <any symbols except "\n"> "\""

number ::= 0x <any of "0-9 ABCDEF">
```

Поддерживаются однострочные комментарии, начинающиеся с ;

- `CLA` - очистить аккумулятор
- `INC` - увеличить значение аккумулятора на 1
- `DEC` - уменьшить значение аккумулятора на 1
- `HLT` - останов
- `NOT` - логическое НЕ аккумулятора
- `NEG` - сделать число в аккумуляторе отрицательным
- `ST`  - сохранить значение аккумулятора в ячейку памяти
- `LD`  - загрузить значение аккумулятора из ячейки памяти
- `CMP` - выставить значение флага Z по результату операции AC - arg
- `JZ`  - переход если флаг Z установлен
- `JMP` - безусловный переход
- `IN`  - загрузить число из ВУ в аккумулятор
- `OUT` - записать число из аккумулятора в ВУ
- `DIV` - операция деления
- `MUL` - операция умножения
- `ADD` - операция сложения
- `SUB` - операция вычитания
- `AND` - операция логического И
- `OR`  - операция логического ИЛИ
- `XOR` - операция сложения по модулю 2

### Семантика

- Язык предполагает последовательное исполнение
- Глобальная область видимости меток
- В программе не может быть дублирующихся меток, определенных в разных местах с одним именем.
- 3 вида адресации: абсолютная, относительная, непосредственная загрузка аргумента
  
| Тип адресации                      | Синтаксис | Описание                                            |
|------------------------------------|-----------|-----------------------------------------------------|
| Абсолютная                         | BUF       | Аргумент - содержимое ячейки по метке BUF           |
| Относительная                      | (BUF)     | Аргумент - содержимое ячейки по адресу из метки BUF |
| Непосредственная загрузка операнда | #BUF      | Аргумент - значение BUF                             |
- В программе должна быть определена метка `START` указывающая на адрес первой исполняемой команды
- Метки для переходов могут определяться на одной строке с инструкцией:

``` asm
label: inc
```

И в другом месте (неважно, до или после определения) сослаться на эту метку:

```asm
jmp label   ; --> `jmp 123`, где 123 - номер инструкции после объявления метки
```

## Организация памяти

### Модель памяти процессора:

- Машинное слово – не определено. Реализуется высокоуровневой структурой данных. Операнд – 32-битный. Интерпретируется
  как беззнаковое целое число. При попытке чтения данных из ячейки с данными исполнение программы аварийно завершится
- Программа и данные хранятся в общей памяти согласно архитектуре Фон-Неймановского процессора. Программа состоит из
  набора инструкций, последняя инструкция – `HLT`
- Операция записи в память перезапишет ячейку памяти как ячейку с данными. Программист имеет доступ на чтение/запись в
  любую ячейку памяти.

```
       Registers
+------------------------------+
| acc                          |
+------------------------------+
           memory
+----------------------------+
| 00 :       ...             |
| 01 :     variables         |
| 02 :       ...             |
| 03 :                       |
|           ...              |
| n  : program start         |
|           ...              |
| k :        ...             |
| k+1 :    variables         |
| k+2 :      ...             |
+----------------------------+
```
- Адрес начала программы задается меткой START:
- Программисту доступен аккумулятор и память
- Константы отсутствуют, память динамическая

## Система команд

### Особенности процессора:

- Машинное слово - не определено
- Доступ к памяти осуществляется по адресу из специального регистра AR. Значение в нем может быть защелкнуто
из операнда или из PC
- Обращение с устройствами ввода-вывода через порты. Порт ВУ на чтение - 2, ВУ на запись - 1
- Обработка данных осуществляется в аккумуляторе. Данные попадают в аккумулятор из памяти
- Поток управления:
  - Значение PC инкриминируется после исполнения каждой инструкции,
  - Условные (JZ) и безусловные (JUMP) переходы.

### Набор инструкций:

| Инструкция | Описание                                                   |
|------------|------------------------------------------------------------|
| CLA        | очистить аккумулятор                                       |
| INC        | увеличить значение аккумулятора на 1                       |
| DEC        | уменьшить значение аккумулятора на 1                       |
| HLT        | останов                                                    |
| NOT        | логическое НЕ аккумулятора                                 |
| NEG        | сделать число в аккумуляторе отрицательным                 |
| ST         | сохранить значение аккумулятора в ячейку памяти            |
| LD         | загрузить значение аккумулятора из ячейки памяти           |
| CMP        | выставить значение флага Z по результату операции AC - arg |
| JZ         | переход если флаг Z установлен                             |
| JMP        | безусловный переход                                        |
| IN         | загрузить число из ВУ в аккумулятор                        |
| OUT        | записать число из аккумулятора в ВУ                        |
| DIV        | операция деления                                           |
| MUL        | операция умножения                                         |
| ADD        | операция сложения                                          |
| SUB        | операция вычитания                                         |
| AND        | операция логического И                                     |
| OR         | операция логического ИЛИ                                   |
| XOR        | операция сложения по модулю 2                              |


### Типы адресации

| Тип адресации                      | Синтаксис | Описание                                            |
|------------------------------------|-----------|-----------------------------------------------------|
| Абсолютная                         | BUF       | Аргумент - содержимое ячейки по метке BUF           |
| Относительная                      | (BUF)     | Аргумент - содержимое ячейки по адресу из метки BUF |
| Непосредственная загрузка операнда | #BUF      | Аргумент - значение BUF                             |

### Директивы

- `word number` - кладет данные в ячейку памяти в соответствии с линейным порядком
- `$label` - кладет адрес метки в аргументы

### Способ кодирования инструкций:
Машинный код преобразуется в список JSON, где один элемент списка — это одна инструкция. 
Индекс инструкции в списке – адрес этой инструкции в памяти. 

Пример машинного слова:
```json
{
  "opcode": "jmp",
  "arg": 3,
  "arg_type": "direct_address"
}
```

## Транслятор

Интерфейс командной строки: `translator.py [-h] input_file output_file`

Реализовано в модуле [translator](ak_lab3%2Ftranslator.py)

### Этапы трансляции:

1. Препроцессинг: Удаление комментариев, превращение каждой строки в список команд и данных разделенных пробелом
2. Трансляция кода в инструкции, метки остаются неразмеченными
3. Подстановка меток в инструкции

Правила трансляции:
1. Одна инструкция - одна строка
2. Метки находятся на одной строке с инструкцией
3. Ссылаться можно только на существующие метки

## Модель процессора

Интерфейс командной строки: `machine.py [-h] [--iotype [IOTYPE]] input_file output_file`

Реализован в модуле [machine](ak_lab3%2Fmachine.py)

### DataPath
```
          +-------------+                                                        
          |             | write_io                                               
          |           +-+---------------------+                                  
          |           |                       |                                  
          |    read_io|  Control Unit         |address                           
          |      +----+                       +------------------------------+   
          |      |  +-+                       |                              |   
          |      |  | +-------+---------------+                              |   
          |      |  |port     |direct     ^  ^instr                          |   
          |      |  |         | load      |  |                               |   
          |      |  |         |           |  |                               |   
          |      |  |         |           |  |                               |   
          v      v  v         |           |  |                               |   
      +----------------+      |           |  |                               |   
      |                |      |           |  |     +------------+            |   
      |  IO Controller |      |           |  |     |            |            |   
      |                |      |  +--------+--+-+---+   Memory   |            |   
      +------------+---+      |  |        |    |   |            |            |   
          ^data_in |data_out  |  |        |    |   |            |            |   
          |        |          |  |        | +--+-->|            |<----read   |   
          |        | +--------+--+        | |  |   |            |            |   
          +----+(0)| |        |  |        | |  |   |            |<----write  |   
          |    | | | |        |  |        | |  |   |            |            |   
          |    v v v v        |  |        | |  |   |            |            |   
          |   +-------+       |  |        | |  |   +------------+            |   
          |   |  MUX  |       |  |        | |  |          ^ addr             |   
          |   +---+---+       |  |(0)     | |  |          |                  |   
          |       |           |  | |      | |  |          |                  |   
          |       v           v  v v      | |  |   +------+-----+            |   
          |  +---------+    +--------+    | |  |   |     AR     |<---latch_ar|   
latch_ac -+->|   AC    |    | MUX    |    | |  |   +------------+            |   
          |  +-------+-+    +---+----+    | |  |          ^                  |   
          |          |          |         | |  |          |                  |   
          |          |          |         | |  |    +-----+----+             |   
          |          |          |         | |  |    |    MUX   |             |   
          |          v          v         | |  |    +----------+             |   
          |       -------    ------       | |  |     ^   ^    ^   +----+     |   
          |       \      \  /      /      | |  +-----+   |    |   |    |     |   
          |        \      \/      /z_flag | |            |  +-+---++   |     |   
          | ~-+/*^->\    ALU     /--------+ |            |  |  PC  |<--+-latch_pc
          |  +1 -1   \          /           |            |  +------+   |     |   
          |           ----+-----            |            |      ^      |     |   
          |               |                 |            |      |      +1    |   
          +---------------+-----------------+            |   +--+---+  |     |   
                                                         |   |  MUX |  |     |   
                                                         |   +------+  |     |   
                                                         |      ^  ^   |     |   
                                                         |      |  +---+     |   
                                                         |      |            |   
                                                         +------+------------+   
```

Реализован в классе `DataPath`

memory - однопортовая память, поэтому либо читаем, либо пишем.

Сигналы (обрабатываются за один такт, реализованы в виде методов класса):

- `latch_pc` - защелкнуть значение в program counter
- `latch_ar` - защелкнуть выбранное значение в address register
- `latch_ac` - защелкнуть выбранное значение в аккумулятор
- `z_flag` - отражает нулевой результат операции в АЛУ
- `read` - прочитать значение из памяти по адресу ar
- `write` - записать выбранное значение в память по адресу ar

## Control Unit

```
+-------------+   read_io +---------------+                    
|             |<----------+               |       +-----------+
|  DataPath   |           |  Instruction  |<------+  Step     |
|             |  write_io |   decoder     |       |  Counter  |
|             |<----------+               +------>|           |
|             |           |               |       +-----------+
|             |   port    |               |                    
|             |<----------+               |                    
|             |           |               |                    
|             |direct_load|               |                    
|             |<----------+               |                    
|             |           |               |                    
|             |  address  |               |                    
|             |<----------+               |                    
|             |           |               |                    
|             |  instr    |               |                    
|             +---------->|               |                    
|             |           |               |                    
|             | z_flag    |               |                    
|             +---------->|               |                    
+-------------+           +---------------+                    
```

Реализовано в классе `ControlUnit`

- Hardwired (реализовано полностью на Python).
- Выполняет предварительную инициализацию машины -- выполняет список инструкций, 
чтобы защелкнуть адрес первой инструкции в pc(метод initialize_datapath)
- Выполнение и декодирование инструкций происходит в методе decode_and_execute_instruction.
- tick нужен для подсчета тактов

Особенности работы модели:
* Цикл симуляции осуществляется в функции simulation.
* Шаг моделирования соответствует одной инструкции с выводом состояния в журнал.
* Для журнала состояний процессора используется стандартный модуль logging.
* Количество инструкций для моделирования лимитировано (1000).
* Остановка моделирования осуществляется при:
  * превышении лимита количества выполняемых инструкций;
  * исключении StopIteration -- если выполнена инструкция halt.

## Тестирование
- Тестирование выполняется при помощи golden test-ов.
- Настройка golden тестирования находится в файле [test_golden.py](tests%2Ftest_golden.py)
- Конфигурация golden test-ов лежит в директории [golden](tests%2Fgolden)

Запустить тесты: `poetry run pytest .`

Обновить конфигурацию golden tests: `poetry run pytest . --update-goldens`

CI при помощи Github Actions:

CI-linter:
```yaml
name: CI - linter

on: [ push ]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ "3.12" ]
    steps:
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install poetry
        run: |
          python -m pip install --upgrade pip
          curl -sSL https://install.python-poetry.org | python3 -
          export PATH="$HOME/.local/bin:$PATH"
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: |
          poetry install
          poetry self add 'poethepoet[poetry_plugin]'
      - name: Run linters
        run: |
          poetry poe lint
```

CI-tester:
```yaml

name: CI - tester

on: [ push ]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ "3.12" ]
    steps:
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install poetry
        run: |
          python -m pip install --upgrade pip
          curl -sSL https://install.python-poetry.org | python3 -
          export PATH="$HOME/.local/bin:$PATH"
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: |
          poetry install
          poetry self add 'poethepoet[poetry_plugin]'
      - name: Test
        run: |
          poetry poe test
```

где:
- `poetry` - управления зависимостями для языка программирования Python.
- `pytest` - утилита для запуска тестов.
- `mypy` - утилита для статического анализа типов в коде
- `pylint` - утилита для статического анализа кода
- `black` - утилита для форматирования кода

Пример использования и журнал работы процессора на примере hello:
```
>> python -m ak_lab3.translator .\examples\asm\hello_world.asm .\examples\json\empty.json
>> python -m ak_lab3.machine .\examples\json\hello_world.json .\examples\input\empty.txt
DEBUG:root:TICK:    0 PC:   16 AR:    0 AC:    0 Z_FLAG: 0      {'opcode': 'cla'}                
DEBUG:root:TICK:    4 PC:   17 AR:   16 AC:    0 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:    9 PC:   18 AR:   14 AC:    0 Z_FLAG: 1      {'opcode': 'ld', 'arg': 1, 'arg_type': 'direct_load'}
DEBUG:root:TICK:   14 PC:   19 AR:   18 AC:    1 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   19 PC:   20 AR:   15 AC:    1 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   25 PC:   21 AR:   14 AC:    0 Z_FLAG: 1      {'opcode': 'inc'}
DEBUG:root:TICK:   29 PC:   22 AR:   21 AC:    1 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   34 PC:   23 AR:    0 AC:    1 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   38 PC:   24 AR:   23 AC:    1 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   43 PC:   25 AR:   14 AC:    1 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:   50 PC:   26 AR:    1 AC:   72 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:   54 PC:   27 AR:   26 AC:   72 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   60 PC:   28 AR:   15 AC:    1 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:   64 PC:   29 AR:   28 AC:    2 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   69 PC:   30 AR:   15 AC:    2 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   73 PC:   20 AR:   30 AC:    2 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   79 PC:   21 AR:   14 AC:    1 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:   83 PC:   22 AR:   21 AC:    2 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   88 PC:   23 AR:    0 AC:    2 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   92 PC:   24 AR:   23 AC:    2 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:   97 PC:   25 AR:   14 AC:    2 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  104 PC:   26 AR:    2 AC:  101 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  108 PC:   27 AR:   26 AC:  101 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  114 PC:   28 AR:   15 AC:    2 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  118 PC:   29 AR:   28 AC:    3 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  123 PC:   30 AR:   15 AC:    3 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  127 PC:   20 AR:   30 AC:    3 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  133 PC:   21 AR:   14 AC:    2 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  137 PC:   22 AR:   21 AC:    3 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  142 PC:   23 AR:    0 AC:    3 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  146 PC:   24 AR:   23 AC:    3 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  151 PC:   25 AR:   14 AC:    3 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  158 PC:   26 AR:    3 AC:  108 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  162 PC:   27 AR:   26 AC:  108 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  168 PC:   28 AR:   15 AC:    3 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  172 PC:   29 AR:   28 AC:    4 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  177 PC:   30 AR:   15 AC:    4 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  181 PC:   20 AR:   30 AC:    4 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  187 PC:   21 AR:   14 AC:    3 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  191 PC:   22 AR:   21 AC:    4 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  196 PC:   23 AR:    0 AC:    4 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  200 PC:   24 AR:   23 AC:    4 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  205 PC:   25 AR:   14 AC:    4 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  212 PC:   26 AR:    4 AC:  108 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  216 PC:   27 AR:   26 AC:  108 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  222 PC:   28 AR:   15 AC:    4 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  226 PC:   29 AR:   28 AC:    5 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  231 PC:   30 AR:   15 AC:    5 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  235 PC:   20 AR:   30 AC:    5 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  241 PC:   21 AR:   14 AC:    4 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  245 PC:   22 AR:   21 AC:    5 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  250 PC:   23 AR:    0 AC:    5 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  254 PC:   24 AR:   23 AC:    5 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  259 PC:   25 AR:   14 AC:    5 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  266 PC:   26 AR:    5 AC:  111 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}      
DEBUG:root:TICK:  270 PC:   27 AR:   26 AC:  111 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  276 PC:   28 AR:   15 AC:    5 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  280 PC:   29 AR:   28 AC:    6 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  285 PC:   30 AR:   15 AC:    6 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  289 PC:   20 AR:   30 AC:    6 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  295 PC:   21 AR:   14 AC:    5 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  299 PC:   22 AR:   21 AC:    6 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  304 PC:   23 AR:    0 AC:    6 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  308 PC:   24 AR:   23 AC:    6 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  313 PC:   25 AR:   14 AC:    6 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  320 PC:   26 AR:    6 AC:   44 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  324 PC:   27 AR:   26 AC:   44 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  330 PC:   28 AR:   15 AC:    6 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  334 PC:   29 AR:   28 AC:    7 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  339 PC:   30 AR:   15 AC:    7 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  343 PC:   20 AR:   30 AC:    7 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  349 PC:   21 AR:   14 AC:    6 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  353 PC:   22 AR:   21 AC:    7 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  358 PC:   23 AR:    0 AC:    7 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  362 PC:   24 AR:   23 AC:    7 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  367 PC:   25 AR:   14 AC:    7 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  374 PC:   26 AR:    7 AC:   32 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  378 PC:   27 AR:   26 AC:   32 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  384 PC:   28 AR:   15 AC:    7 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  388 PC:   29 AR:   28 AC:    8 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  393 PC:   30 AR:   15 AC:    8 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  397 PC:   20 AR:   30 AC:    8 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  403 PC:   21 AR:   14 AC:    7 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  407 PC:   22 AR:   21 AC:    8 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  412 PC:   23 AR:    0 AC:    8 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  416 PC:   24 AR:   23 AC:    8 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  421 PC:   25 AR:   14 AC:    8 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  428 PC:   26 AR:    8 AC:   87 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  432 PC:   27 AR:   26 AC:   87 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  438 PC:   28 AR:   15 AC:    8 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  442 PC:   29 AR:   28 AC:    9 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  447 PC:   30 AR:   15 AC:    9 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  451 PC:   20 AR:   30 AC:    9 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  457 PC:   21 AR:   14 AC:    8 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  461 PC:   22 AR:   21 AC:    9 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  466 PC:   23 AR:    0 AC:    9 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  470 PC:   24 AR:   23 AC:    9 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  475 PC:   25 AR:   14 AC:    9 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  482 PC:   26 AR:    9 AC:  111 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  486 PC:   27 AR:   26 AC:  111 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  492 PC:   28 AR:   15 AC:    9 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  496 PC:   29 AR:   28 AC:   10 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  501 PC:   30 AR:   15 AC:   10 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  505 PC:   20 AR:   30 AC:   10 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  511 PC:   21 AR:   14 AC:    9 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  515 PC:   22 AR:   21 AC:   10 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  520 PC:   23 AR:    0 AC:   10 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  524 PC:   24 AR:   23 AC:   10 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  529 PC:   25 AR:   14 AC:   10 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  536 PC:   26 AR:   10 AC:  114 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  540 PC:   27 AR:   26 AC:  114 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  546 PC:   28 AR:   15 AC:   10 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  550 PC:   29 AR:   28 AC:   11 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  555 PC:   30 AR:   15 AC:   11 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  559 PC:   20 AR:   30 AC:   11 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  565 PC:   21 AR:   14 AC:   10 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  569 PC:   22 AR:   21 AC:   11 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  574 PC:   23 AR:    0 AC:   11 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  578 PC:   24 AR:   23 AC:   11 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  583 PC:   25 AR:   14 AC:   11 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  590 PC:   26 AR:   11 AC:  108 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  594 PC:   27 AR:   26 AC:  108 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  600 PC:   28 AR:   15 AC:   11 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  604 PC:   29 AR:   28 AC:   12 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  609 PC:   30 AR:   15 AC:   12 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  613 PC:   20 AR:   30 AC:   12 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  619 PC:   21 AR:   14 AC:   11 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  623 PC:   22 AR:   21 AC:   12 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  628 PC:   23 AR:    0 AC:   12 Z_FLAG: 0      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  632 PC:   24 AR:   23 AC:   12 Z_FLAG: 0      {'opcode': 'st', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  637 PC:   25 AR:   14 AC:   12 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'relative_address'}
DEBUG:root:TICK:  644 PC:   26 AR:   12 AC:  100 Z_FLAG: 0      {'opcode': 'out', 'arg': 1}
DEBUG:root:TICK:  648 PC:   27 AR:   26 AC:  100 Z_FLAG: 0      {'opcode': 'ld', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  654 PC:   28 AR:   15 AC:   12 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  658 PC:   29 AR:   28 AC:   13 Z_FLAG: 0      {'opcode': 'st', 'arg': 15, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  663 PC:   30 AR:   15 AC:   13 Z_FLAG: 0      {'opcode': 'jmp', 'arg': 20, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  667 PC:   20 AR:   30 AC:   13 Z_FLAG: 0      {'opcode': 'ld', 'arg': 14, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  673 PC:   21 AR:   14 AC:   12 Z_FLAG: 0      {'opcode': 'inc'}
DEBUG:root:TICK:  677 PC:   22 AR:   21 AC:   13 Z_FLAG: 0      {'opcode': 'cmp', 'arg': 0, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  682 PC:   23 AR:    0 AC:   13 Z_FLAG: 1      {'opcode': 'jz', 'arg': 31, 'arg_type': 'direct_address'}
DEBUG:root:TICK:  686 PC:   31 AR:   23 AC:   13 Z_FLAG: 1      {'opcode': 'hlt'}
INFO:root:output buffer: Hello, World
INFO:root:instr_counter: 140
INFO:root:ticks: 689
```

| ФИО                      | <алг>       | <LoC> | <code байт> | <code инстр> | <инстр> | <такт> | <вариант>                                                                                               |
|--------------------------|-------------|-------|-------------|--------------|---------|--------|---------------------------------------------------------------------------------------------------------|
| Состанов Тимур Айратович | hello_world | 20    | -           | 20           | 140     | 689    | lisp -> asm \| acc \| neum \| hw \| tick -> instr \| struct \| stream \| port \| pstr \| prob1 \| cache |
| Состанов Тимур Айратович | cat         | 11    | -           | 11           | 46      | 208    | lisp -> asm \| acc \| neum \| hw \| tick -> instr \| struct \| stream \| port \| pstr \| prob1 \| cache |
| Состанов Тимур Айратович | hello       | 72    | -           | 72           | 403     | 1975   | lisp -> asm \| acc \| neum \| hw \| tick -> instr \| struct \| stream \| port \| pstr \| prob1 \| cache |
| Состанов Тимур Айратович | prob1       | 36    | -           | 36           | 28      | 132    | lisp -> asm \| acc \| neum \| hw \| tick -> instr \| struct \| stream \| port \| pstr \| prob1 \| cache |

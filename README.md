  TUTAC - TUTorial Automatic Computer, described in the book "Basic Computer Programming" by Theodore G. Scott.
  has 
  - Decimal interface
  - 2000 word, 11 digit memory, addressed as 0000-1999
    - memory could expand to 10,000 words
  - card reader
  - zero memory button
  - load card button, reads until blank card
    order of cards doesn't matter since explicit addressing and
    instruction pointer always starts at 0000.
  - instruction pointer
  - op codes
  <pre>
    | code | command                | abbr  |
    |------+------------------------+-------|
    |   00 | Stop                   | Stop  |
    |   08 | Shift Right            | SR    |
    |   09 | Shift Left             | SL    |
    |   15 | Store                  | Store |
    |   25 | Write                  | Write |
    |   30 | Unconditional Transfer | UT    |
    |   31 | Transfer on Zero       | TOZ   |
    |   32 | Transfer on Plus       | TOP   |
    |   50 | Copy                   | Copy  |
    |   60 | Add                    | Add   |
    |   61 | Subtract               | Sub   |
    |   62 | Multiply               | Mult  |
    |   63 | Divide                 | Div   |
  </pre>
  Instructions are coded as 
  - cards take 15 digits
    - 4 digit address, 1 digit sign (0 pos, 1 neg), 10 digit integer
    - 4 digit address, 1 ignored digit, 2 digit opcode, 4 digit addresses, 4 ignored
  - There's a single word accumulator with an unsigned 10 digit right register.
   - typewriter output
  - stop light
  - overflow light, when an 11 digit number is generated in the accumulator the overflow light comes on, automatic STOP, stop light comes on
  
  Program running procedure as described in the text is:
  - cards are punched
  - cards placed in card reader, unpunched card indicates end of deck
  - load card button pressed
  - until unpunched card:
    - card read
    - contents loaded into memory
  - execution starts with instruction pointer at 0000
  - execution continues until STOP condition
  
  Example programs in carddecks/ - altered syntax to allow comments.
  Run as:
  python tutac.py path_to_program.deck
  Output to stdout.
  
  

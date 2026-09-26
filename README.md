# Number Squares

An addition game made with pygame. Two cartoon number characters, built from
the right number of colored squares, show up under a question like
"What is 4 + 5?". Type your answer and press Enter. The two characters jump
together and combine into their sum. If you got it right you get confetti and
a big smile.

## Running

```sh
pip install -r requirements.txt
python -m number_squares
```

## Controls

| Screen   | Keys |
|----------|------|
| Menu     | `1` `2` `3` or ←/→ pick difficulty, Enter to play, Esc to quit |
| Question | type digits, Backspace, Enter to answer, Esc back to the menu |
| Result   | Enter/N for another round, M for the menu, Esc/Q to quit |

You can also click all the buttons with the mouse.

Difficulty: **Easy** uses 1–9, **Medium** uses numbers up to 99, **Hard** uses numbers up to 999.

## Colors

| Digit | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|-------|---|---|---|---|---|---|---|---|---|---|
| Color | white | red | orange | yellow | green | blue | dark purple | rainbow | magenta | grey |

- A single-digit character is solid blocks of its color. The blocks of a 7
  run through the rainbow from red at the top to light purple at the bottom.
- From 10 up, each block's **border** is the first digit and the **interior**
  has one vertical stripe per remaining digit, from left to right.
  10 is a red border with a white inside. 215 is an orange border with a red
  left half and a blue right half.
  A 7 inside a pattern shows up as horizontal rainbow bands.
- Black is only used for features: faces, arms and legs.

### Big numbers

To keep characters a sensible size, big numbers are compressed:

- **100–999:** each *stacked* block (one extra layer peeking out behind it)
  is worth 10. The leftover ones are plain blocks.
- **1000+:** blocks with two extra layers are worth 100, and they're mixed
  with ten-blocks and ones.

A legend under or above the character (for example "▣ = 10") explains the
stacked blocks. The block count is still exact: 215 is 21 ten-blocks and
5 ones.

## Tests

```sh
pip install pytest
python -m pytest
```

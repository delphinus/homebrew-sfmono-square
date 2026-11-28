# Powerline separators out of the row by a pixel

The Powerline separators (U+E0B0 and the others) of SF Mono Square are as tall as a cell: their
top is at the ascent and their bottom at the descent.  A terminal that draws them from the font
can still show a pixel of a separator above or below its row.  This cannot be fixed in the font.

## Why

The ascent of SF Mono Square is 1638/2048 of the em, which is not a whole number of pixels at most
sizes.  At 18pt on a Retina display the em is 36px and the ascent is 28.79px.  A terminal puts the
baseline on a whole pixel: on the 28th pixel the top of a separator is 0.79px above the row, and on
the 29th its bottom is 0.21px below the row.  Either way a separator as tall as the row is out of it
at one of the ends, and the antialiased edge shows as a pixel at the corners of the separator.

Making the separators shorter only moves the problem.  To stay in the row at every size, they would
have to lose almost a pixel (about 3% of the em at each end at 13pt), and then they would be shorter
than the row, with a step against the background at the top or the bottom.

The patcher used to make the separators 1% taller than the em, so that they bled 10.5 units out of
the cell at each end.  That is 0.18px at 18pt on Retina.  Taking it away changed the brightness of
the pixels out of the row by about 20%, and nothing that could be seen.

## Terminals

Most terminals draw the separators by themselves, filling the cell exactly, and do not show it.

| Terminal | Draws the separators | Out of the row |
|---|---|---|
| kitty | by itself, always | no |
| Ghostty | by itself | no |
| WezTerm | by itself with `custom_block_glyphs = true` (the default) | no |
| WezTerm | from the font with `custom_block_glyphs = false` | yes, above the row at 13pt, 16pt and 18pt |
| iTerm2 | by itself with "Use built-in Powerline glyphs" on | no |
| iTerm2 | from the font with it off | yes, above the row at 13pt and 18pt, below at 16pt |
| Terminal.app | from the font, always | faint, below the row at 16pt only |

Terminal.app makes a row about 2px taller than the em at these sizes, so the separators stay in the
row at 13pt and 18pt.

These were measured on macOS with SF Mono Square v3.7.0 Regular at 13pt, 16pt and 18pt on a Retina
display (WezTerm 20250730, Ghostty 1.4.0, iTerm2 3.7.9, Terminal.app 2.15).  A line of Powerline
segments was printed with blank rows above and below it, and the pixels next to the top and the
bottom of the segments that differed from the background were counted.

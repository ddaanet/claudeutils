# Backtick Space Quoting

Testing inline code with leading and trailing spaces.

## Cases with Leading Spaces

- Leading space: ` code`
- Multiple leading: `   code`
- Only space: `   `

## Cases with Trailing Spaces

- Trailing space: `code `
- Multiple trailing: `code   `
- Only space: `   `

## Cases with Both Spaces

- Both ends: ` code `
- Both multiple: `   code   `
- Both with symbols: ` $VAR `

## Cases without Spaces (unchanged)

- Normal: `code`
- No spaces: `const x = 'y'`
- Path: `~/.bashrc`

## Mixed in Sentence

The empty span ` ` (space only) should be quoted.
Variable ` name ` needs visible spaces.
The path `./file` should be unchanged.

## Multiple on Same Line

First ` one ` and second `two` and ` three `.

## With Markdown

Bold: **`bold`** (no spaces)
Code in bold: **` spaced `** (has spaces)
Italic: *` slanted `* (has spaces)

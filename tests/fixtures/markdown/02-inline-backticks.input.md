# Inline Code Spans with Backticks

## Basic Cases

- Single backticks: `code`
- Multiple words: `const foo = 'bar'`
- With symbols: `$PATH` and `~/.bashrc`
- Empty code span: ` ` (space between delimiters is ignored)
- Whitespace trimmed: ` code ` becomes `code` (non-significant)

## Double Backtick Quoting

**Without spaces around content:**
- Quote one backtick (no spaces): ``using ` backtick``
- Multiple backticks in content: ``use ` and ` backticks``

**With spaces for consistency (when content starts/ends with backtick):**
- Single backtick: `` ` `` (spaces at both ends for consistency)
- Backtick at start: `` `start`` (spaces at both ends)
- Backtick at end: ``end` `` (spaces at both ends)
- Multiple with spaces: `` ` and ` `` (spaces at both ends)

## Triple Backtick Quoting

**Without spaces around content:**
- Quote double backticks: ``` using `` double ```
- Multiple in content: ``` use `` and `` backticks ```

**With spaces for consistency (when content starts/ends with backticks):**
- Double backtick: ``` `` ``` (spaces at both ends)
- At start: ``` ``start ``` (spaces at both ends)
- At end: ``` end`` ``` (spaces at both ends)
- Single in triple: ``` ` ``` (spaces at both ends)

## Mixed Quoting

**Using triple backticks to quote both single and double:**
- Mixed: ``` using ` single and `` double ```
- Complex: ``` quote ` or `` or both ```
- At boundaries: ``` ` and `` mixed ```

## Quadruple Backtick Quoting

**Quoting triple backticks (code fence markers):**
- Quote triple (no spaces needed): ```` using ``` triple ````
- Fence example: ```` code fence: ```python ````
- Triple with spaces (if at boundaries): ```` ``` ```` (spaces at both ends)

## Edge Cases

**Content is just backticks (spaces added for consistency):**
- Just one backtick: `` ` `` (spaces at both ends)
- Just two backticks: ``` `` ``` (spaces at both ends)
- Just three backticks: ```` ``` ```` (spaces at both ends)

**Delimiter normalization (shortest delimiter when no inner backticks):**
- May normalize: ``no backticks`` → `no backticks`
- May normalize: ```also no backticks``` → `also no backticks`
- Normalization is a feature, not a bug

**Adjacent code spans:**
- Back to back: `code1``code2`
- With text: `code1` and ``code2``
- Multiple styles: `single` and `` `double` `` and ``` `triple` ```

**Backticks with other markdown:**
- Bold code: **`code`**
- Italic code: *`code`*
- Link with code: [`link`](url)
- Code with emphasis: `*not italic*`
- Code with underscore: `my_variable`

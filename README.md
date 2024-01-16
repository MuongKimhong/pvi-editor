### You like Vim? You love NeoVim? You like PVI.

#### A vim like editor, built on top of [Textual](https://github.com/textualize/textual/) with all nescessary features and key bindings.

![Screenshot](screenshot.png)

## Installation

#### There are some new key bindings to make things easier while coding, for example:
- to go to top of the file, instead of using `<gg>`, use `<gt>` (Go Top)
- to go to bottom of the file, instead of using `<G>`, use `<gb>` (Go bottom)
- to select all, instead of `<gg><VG>`, use `<sa>` (Select all)
- to selec current line, instead of `<V>`, use `<sl>` (Select line)

See key bindings for more details.

## Key Binding
- `<ctrl+b>` show or hide sidebar
- `<ctrl+q>` switch focus between sidebar and editor
- `<j>` move down in sidebar if sidebar is focused
- `<k>` move up in sidebar if sidebar is focused
- `<dd>` delete file or directory in sidebar if sidebar is focused
- `<af>` create new file in sidebar if sidebar is focused
- `<ad>` create new directory in sidebar if sidebar is focused
#### Editor
- `<j>` move down
- `<k>` move up
- `<h>` move left
- `<l>` move right
- `<i>` enter insert mode
- `<gt>` go to the top of the file
- `<gb>` go to the bottom of the file
- `<sa>` enter selection mode and select all
- `<sl>` enter selection mode and select current line
- `<v>` enter selection mode
- `<d>` delete the selected text (only work in selection mode)
- `<y>` copy the selected text (only work in selection mode)
- `<yy>` copy the current line
- `<dd>` copy the current line and delete
- `<p>` paste the copied text at cursor location
- `<ss>` open search file dialog

- `<:w>` save file content (Normal mode)
- `<:wq>` save file content and quit PVI (Normal mode)
- `<:q>` quit PVI (Normal mode)

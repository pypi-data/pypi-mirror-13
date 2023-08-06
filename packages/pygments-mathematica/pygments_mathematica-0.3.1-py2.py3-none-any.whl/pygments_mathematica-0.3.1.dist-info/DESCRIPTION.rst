pygments-mathematica

This is the most up-to-date lexer and highlighter for Mathematica/Wolfram Language source code using
the pygments engine.

It currently supports:

 - All builtin functions in the System` context including unicode symbols like π except those that
 use characters from the private unicode space (e.g. \[FormalA]).
 - User defined symbols, including those in a context.
 - All operators including unicode operators like ∈ and ⊕.
 - Comments, including multi line and nested.
 - Strings, including multi line and escaped quotes.
 - Patterns, slots (including named slots #name introduced in version 10) and slot sequences.
 - Message names (e.g. the ivar in General::ivar)
 - Numbers including base notation (e.g. 8 ^^ 23 == 19) and scientific notation (e.g. 1 *^ 3 == 1000).
 - Local variables in Block, With and Module.

A Sass file containing the styles can be obtained from the package repository for use in static
website generators such as Jekyll, Octopress, Pelican, etc.

© 2016 rsmenon



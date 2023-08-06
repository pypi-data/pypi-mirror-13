`ayrton` uses several tricks to get the job done. This file attempts to explain them.

Expansion
=========

CraztASTTransformer
===================

`ayrton` analyzes the script before executing it. The class `ayrton.castt.CraztASTTransformer`
implements several visitors for implementing several of these tricks:

Command execution
-----------------

An `ayrton` script executes commands by calling function with the same name. Thus, `echo()`
calls `/bin/echo`. For this, the `visit_Call()` method checks if there's any name in the
current scope and in `ayrton`'s environment (which includes builtins, imported functions
and other stuff) defined; if not, it converts the function call `foo()` to the instantiation
of `Command` and subsequent call of the resulting object, `Command ('foo')()`. Any parameters
of the original call are passed mostly as-is to the modified version.

Command nesting
---------------

Command nesting  is when the first argument to a command is also a command. In this case the
`_out` and `_bg` keywords for the inner one are set to `Pipe` and `True`, and the `_in`
keyword of the nesting one is set up to the inner command. See Pipes below.

Pipes
-----

The `visit_BinOp()` method takes care of building pipes for constructions like `foo () | bar ()`.
This first applies the command execution transform (by calling `generic-visit()`) and then
rewrites in the same way as Command nesting.

Redirection
-----------

The same method also takes care of stdout redirection in append mode via Python's binary
right shift operator. The `_out` keyword is rewritten to a call to `open()` in binary append
mode with the right operand as filename.

Also the `visit_Compare()` method implements stdin redirection (`<`), stdout redirection in
rewrite mode (`>`) and stdout+stderr (`>=`).

Transparent remote execution
----------------------------


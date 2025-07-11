# Jam Programming Language - Backend Implementation

## Overview
This repository contains the backend implementation of the Jam programming language, which includes:
1. A Jam-to-JavaScript transpiler (`jam_to_js()` function)
2. A Jam interpreter (`run_jam_code()` function)

Jam is a simple, expressive language designed for educational purposes, with features inspired by JavaScript and Python.

## Table of Contents
1. [Language Features](#language-features)
2. [Transpiler Details](#transpiler-details)
3. [Interpreter Details](#interpreter-details)
4. [Usage Examples](#usage-examples)
5. [Supported Commands](#supported-commands)
6. [Implementation Code](#implementation-code)
7. [Limitations](#limitations)
8. [Development Notes](#development-notes)

## Language Features

### Core Features
- **Simple syntax** with minimal punctuation
- **Dynamic typing** with automatic type inference
- **First-class functions** including anonymous functions
- **Control structures** (if/else, loops)
- **Basic I/O operations** (print, say)
- **Math operations** (arithmetic, square roots)
- **List operations** (mapping, random selection)

### Unique Features
- **Natural language-inspired syntax** (e.g., "add 5 and 3 into result")
- **Voice output support** via `say` command
- **Timing operations** with `timer start`/`timer stop`
- **Immediate feedback** in interpreter mode

## Transpiler Details

### Function: `jam_to_js(jam_code: str) -> str`
Converts Jam code to equivalent JavaScript code.

#### Implementation Notes:
- Processes input line by line
- Maintains indentation structure
- Handles nested blocks (if/else, functions, loops)
- Preserves comments from original code
- Generates human-readable JavaScript output

#### Supported Transpilation:
| Jam Syntax          | JavaScript Equivalent               |
|---------------------|-------------------------------------|
| `print expr`        | `console.log(expr)`                 |
| `set var = value`   | `let var = value`                   |
| `if condition { }`  | `if (condition) { }`                |
| `otherwise { }`     | `else if (condition) { }`           |
| `function name(){}` | `function name() {}`                |
| `map func over arr` | `arr.map(func)`                     |
| `repeat N { }`      | `for (let i=0; i<N; i++) { }`       |

## Interpreter Details

### Function: `run_jam_code(code: str) -> str`
Executes Jam code directly and returns the output.

#### Implementation Notes:
- Uses Python's `eval()` for expression evaluation
- Maintains state in `variables`, `lists`, and `functions` dictionaries
- Redirects stdout to capture all output
- Implements safety measures for web use (disables certain commands)

#### Key Components:
1. **Expression Evaluator** (`eval_expr()`):
   - Handles strings, numbers, booleans, lists, and variables
   - Performs automatic type conversion

2. **Condition Evaluator** (`eval_condition()`):
   - Substitutes variable values into conditions
   - Converts Jam-style booleans to Python

3. **Program Runner** (`run_program()`):
   - Processes commands sequentially
   - Handles block structures (functions, conditionals, loops)
   - Maintains call stack for nested execution

## Usage Examples

### Example 1: Basic Program
```jam
let x = 5
print x
if x > 3 {
    print "Big"
}

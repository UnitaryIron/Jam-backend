# Jam Programming Language - Backend Implementation

Jam is a beginner-friendly programming language that reads almost like English.  
This repository contains the **backend implementation** of Jam, including:

1. A **Jam-to-JavaScript transpiler** (`jam_to_js()` function)
2. A **Jam interpreter** (`run_jam_code()` function)

Jam is designed for **educational use**, with features inspired by JavaScript, Python, and natural language itself.

---

## Table of Contents

1. [Language Features](#language-features)
2. [Transpiler Details](#transpiler-details)
3. [Interpreter Details](#interpreter-details)
4. [Usage Examples](#usage-examples)
5. [Supported Commands](#supported-commands)
6. [Limitations](#limitations)
7. [Development Notes](#development-notes)
8. [Contributing](#contributing)
9. [License](#license)

---

## Language Features

### Core Features

- Simple syntax with minimal punctuation
- Dynamic typing with automatic inference
- Control flow: `if`, `else`, `repeat`, `while`, etc.
- Basic I/O: `print`, `say`, `ask`
- Math operations including square roots, exponents
- List support with operations like `map`, `random`

### Unique Features

- **Natural-language inspired syntax**  
  e.g., `add 5 and 3 into result`
- **Voice output support** using `say`
- **Timer commands**: `timer start`, `timer stop`
- **Immediate feedback** in interpreter mode

---

## Transpiler Details

### Function: `jam_to_js(jam_code: str) -> str`

This function converts Jam code into equivalent, readable JavaScript.

#### Features

- Processes input line by line
- Maintains indentation and structure
- Handles nested `if`, `repeat`, and functions
- Preserves comments
- Outputs clean JavaScript

#### Example Transpilation

| Jam Code               | JavaScript Output           |
|------------------------|-----------------------------|
| `print x`              | `console.log(x)`            |
| `let a = 5`            | `let a = 5`                 |
| `if a > 3 { ... }`     | `if (a > 3) { ... }`        |
| `repeat 5 { ... }`     | `for (let i = 0; i < 5; i++) { ... }` |
| `map f over list`      | `list.map(f)`               |
| `function greet() {}`  | `function greet() {}`       |

---

## Interpreter Details

### Function: `run_jam_code(code: str) -> str`

Executes Jam code in real-time using Python as the host environment.

#### Internal Components

1. **Expression Evaluator** - `eval_expr()`
   - Evaluates numbers, strings, variables, booleans
   - Automatically converts types

2. **Condition Evaluator** - `eval_condition()`
   - Parses and evaluates logical conditions
   - Handles natural booleans (`true`, `false`)

3. **Program Runner** - `run_program()`
   - Executes code line by line
   - Tracks variable state and function calls
   - Supports nested blocks and scopes

#### Safety
- Blocks unsafe Python built-ins for web deployment
- Uses `stdout` redirection to capture printed output

---

## Usage Examples

### Example 1: Basic Program

```jam
let x = 5
print x
if x > 3 {
    print "Big"
}
```
## Usage Examples

### Example 2: Using Functions

```jam
function greet(name) {
    say "Hello, " + name
}

greet("Emmanuel")
```
### Example 3: Mapping Over Lists
```jam
let nums = [1, 2, 3, 4]
let doubled = map n => n * 2 over nums
print doubled
```
## Supported Commands
- let - declare variables
- print, say, ask - I/O operations
- if, else, repeat, while, until - control flow
- function, return - function support
- map, filter, reduce - list processing
- timer start, timer stop - measure time intervals
- random, length, sqrt, pow - built-in functions

## Limitations
- No file system access
- No real concurrency or threading
- Limited scope control (functions do not yet support closures)
- Limited error messages (to be improved)
- Transpiler currently covers a subset of all Jam features

## Development Notes
- Written in Python 3.10+
- Uses ast, eval, and custom parser logic
- Designed to integrate with the Jam IDE
- Modular structure for easy extension (parser, stdlib, core)

## Contributing
We welcome contributions from developers, educators, and students alike!

### Local Setup
```bash
git clone https://github.com/UnitaryIron/Jam-backend.git
cd Jam-backend
pip install -r requirements.txt
python main.py
```

## Contribution Areas

- Core Interpreter to improve logic, add new commands
- Transpiler to extend JavaScript support
- Testing	Add test coverage, edge cases
- Docs & Tutorials	Create guides for educators and students
- IDE Integration	(Frontend repo) Help improve the web IDE

## Guidelines

- Fork the repo
- Create a feature branch: git checkout -b feature/my-feature
- Commit with a clear message
- Push and open a pull request
- Be kind and respectful in reviews

### Good First Issues

- Check issues tagged with good first issue.

## License

This project is licensed under the MIT License.
See LICENSE for details.

## Contact
For questions, ideas, or collaboration:
Discord: unitaryiron_99094
Email: emmanuellijo670@gmail.com

![GitHub issues](https://img.shields.io/github/issues/UnitaryIron/Jam-backend)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

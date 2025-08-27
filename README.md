# 🎵 Jam: A Friendly, Expressive Language for All Developers

> **Jam** is a beginner-friendly programming language with a readable, English-like syntax that compiles to JavaScript. Designed to be simple enough for newcomers and powerful enough for professionals.

![License](https://img.shields.io/github/license/UnitaryIron/Jam-Backend)
![Issues](https://img.shields.io/github/issues/UnitaryIron/Jam-Backend)
![Last Commit](https://img.shields.io/github/last-commit/UnitaryIron/Jam-Backend)

---

## 📚 Table of Contents

- [Why Jam?](#why-jam)
- [Quick Start](#quick-start)
- [Your First Jam Program](#your-first-jam-program)
- [Language Guide](#language-guide)
  - [Variables](#variables)
  - [Control Flow](#control-flow)
  - [Loops](#loops)
  - [Functions](#functions)
  - [Operations](#operations)
  - [Utilities](#utilities)
- [Architecture](#architecture)
- [Vision](#vision)
- [Contributing](#contributing)
- [Development Setup](#development-setup)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Support](#support)

---

## Why Jam?

### For Beginners

- **Intuitive Syntax** — English-like commands that make sense right away  
- **Beginner-Friendly Learning Curve** — No complex symbols or obscure syntax  
- **Interactive Feedback** — Built-in interpreter for immediate results  
- **Helpful Guidance** — Get warnings and tips as you learn  

### For Professionals

- **JavaScript Compilation** — Convert Jam into clean, production-ready JavaScript  
- **Type Inference** — Smart type detection and warning system  
- **Modern Features** — Functions, lambdas, maps, timers, and more  
- **Extensible Architecture** — Easily add new features or tools  

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/UnitaryIron/Jam-Backend.git
cd Jam-Backend

# Install dependencies
pip install -r requirements.txt
```

## Your First Jam Program

### Create a file called hello.jam:

```jam
# Welcome to Jam!
say "Hello, World!"
set name = ask "What's your name?" into name
print "Welcome " + name + "!"
```
Run with the Jam interpreter:
```python
python jam.py hello.jam
```
Or compile to JavaScript:
```
python jam.py --compile hello.jam > hello.js
node hello.js
```

## Language Guide

### Variables
```jam
set message = "Hello Jam!"
set count = 42
set pi = 3.14159
set is_active = true
set numbers = [1, 2, 3, 4, 5]
```

### Control Flow
```jam
if temperature > 30 {
    say "It's hot outside!"
} else if temperature > 20 {
    say "It's warm outside!"
} else {
    say "It's cool outside!"
}
```

### Loops
```jam
repeat 5 {
    print "This will print 5 times"
}
```

### Functions

Named function:
```jam
function greet (name) {
    return "Hello " + name + "!"
}
```

Anonymous function (lambda):
```jam
set double = function anonymous (x) {
    return x * 2
}
```

Calling functions:
```jam
call greet "Jam Developer"
print double(21)
```

### Operations

Math operations:
```jam
add 5 and 3 into result
multiply result and 2 into final
```

String operations:
```jam
uppercase "hello" into shout
reverse "Jam" into backwards
```

List operations:
```jam
set numbers = [1, 2, 3, 4, 5]
length of numbers into count
```

Map (transform array):
```jam
set doubled = map (n) => n * 2 over numbers
```

### Utilities

Timing execution:
```jam
timer start
# ... your code ...
timer stop
```

Random values:
```jam
random between 1 and 100 into lucky_number
choose from "apple", "banana", "cherry" into fruit
```

User input:
```jam
ask "What's your name?" into username
print "Hello " + username
```

## Architecture
Jam is built with a dual-path architecture:

- Interpreter: Runs Jam directly in Python for quick testing
- Compiler: Transpiles Jam into readable, performant JavaScript

Core Components:

- Parser — Converts Jam syntax into an abstract syntax tree
- Type System — Provides inference and developer-friendly warnings
- JavaScript Transpiler — Outputs clean, idiomatic JavaScript
- Standard Library — Built-in support for common operations

🔮 Vision

Jam aims to be the most approachable language without sacrificing power or extensibility.

Roadmap

🌐 Web-based playground

📦 Package manager for Jam modules

🧾 Optional static type annotations

🐞 Debugger and developer tools

📚 Expanded standard library

🚀 Performance improvements

🤝 Contributing

We welcome developers of all skill levels! Start contributing in just a few steps:

Fork the repository

Create a feature branch

git checkout -b feature/my-feature


Commit your changes

git commit -m "Add my feature"


Push to GitHub

git push origin feature/my-feature


Open a Pull Request

📄 Please see the CONTRIBUTING.md
 and CODE_OF_CONDUCT.md

Areas We Need Help

🧪 Language design and syntax ideas

📖 Documentation and tutorials

📦 Standard library development

🛠️ Editor tooling and plugins

🧹 Test coverage and edge cases

💻 Development Setup
# Clone your fork
git clone https://github.com/your-username/jam-language.git
cd jam-language

# Run tests
python test_jam.py


📘 Documentation build instructions coming soon.

📜 License

This project is licensed under the MIT License
.

🙏 Acknowledgments

Inspired by educational languages like Scratch, Python, and BASIC

Created to make programming more accessible and expressive

Thanks to all contributors

📞 Support

📖 Documentation: Coming soon

🐛 Issues: GitHub Issues

💬 Discussions: GitHub Discussions

📧 Email: jam-language@example.com

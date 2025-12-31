"""Compiler and interpreter for the Jam programming language.

This module provides two primary functionalities:
1.  jam_to_js: A compiler that translates Jam source code into JavaScript.
2.  run_jam_code: An interpreter that executes Jam source code directly in Python.

It also includes helper functions for parsing, type inference, and execution logic.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any, Tuple

JamType = Union[str, int, float, bool, list]


class TypeErrorJam(Exception):
    """Custom exception for type-related errors in Jam."""
    pass


# Tracks variables and their types (by name -> Python type)
symbol_table: Dict[str, type] = {}
type_warnings: List[str] = []


def infer_type(value: str) -> Optional[type]:
    """Infer type from a Jam literal/expression (quick & conservative)."""
    v = value.strip()
    if v.isdigit() or (v.startswith('-') and v[1:].isdigit()):
        return int
    if v.count('.') == 1:
        left, right = v.split('.', 1)
        if (left.isdigit() or (left.startswith('-') and left[1:].isdigit())) and right.isdigit():
            return float
    if v in ("true", "false"):
        return bool
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return str
    if v.startswith("[") and v.endswith("]"):
        return list
    if v in symbol_table:
        return symbol_table[v]
    return None


def check_assignment(var: str, value: str) -> None:
    """Record type and warn if the value type flips. Never raise."""
    val_t = infer_type(value)
    if var in symbol_table:
        if val_t and symbol_table[var] != val_t:
            type_warnings.append(
                f"Type mismatch for '{var}': previously {symbol_table[var].__name__}, now {val_t.__name__}"
            )

    else:
        symbol_table[var] = val_t or str

    # ---------- Compiler: Jam -> JavaScript ----------


def _collect_block(lines: List[str], start_idx: int) -> Tuple[List[str], int]:
    """Collect lines inside a {...} starting with the current line that already consumed the '{'."""
    block: List[str] = []
    depth = 0
    i = start_idx
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        if line.endswith("{"):
            depth += 1
            block.append(raw)
        elif line == "}":
            if depth == 0:
                return block, i
            depth -= 1
            block.append(raw)
        else:
            block.append(raw)
        i += 1
    return block, i


_anon_counter = 0


def _anon_name() -> str:
    """Generates a unique name for an anonymous function.

    Returns:
        A string representing a unique function name.
    """
    global _anon_counter
    _anon_counter += 1
    return f"_anon_{_anon_counter}"


def _trim_quotes(s: str) -> str:
    """Removes leading and trailing quotes from a string.

    Args:
        s: The string to trim.

    Returns:
        The string without surrounding single or double quotes.
    """
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def jam_to_js(jam_code: str) -> str:
    """Compiles a string of Jam code into JavaScript.

    This function iterates through each line of the Jam code, translating
    constructs like variable assignments, control flow, function definitions,
    and I/O commands into their JavaScript equivalents.

    Args:
        jam_code: A string containing the Jam source code.

    Returns:
        A string of compiled JavaScript code. Type warnings are appended
        as comments at the end of the script.
    """
    type_warnings.clear()
    lines = [ln.rstrip("\n") for ln in jam_code.splitlines()]
    js: List[str] = []

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        # Skip empties/comments
        if not line or line.startswith("#"):
            i += 1
            continue

        # ---- CONTROL FLOW: if / else if / else ----
        if line.startswith("if ") and line.endswith("{"):
            cond = line[3:-1].strip()
            js.append(f"if ({cond}) {{")
            i += 1
            inner, i = _collect_until_brace(lines, i)
            js.extend(_indent_block(jam_to_js("\n".join(inner))))
            js.append("}")
            i = _skip_blank_comments(lines, i + 1)
            while i < len(lines):
                nxt = lines[i].strip()
                if nxt.startswith("else if ") and nxt.endswith("{"):
                    cond2 = nxt[8:-1].strip()
                    js.append(f"else if ({cond2}) {{")
                    i += 1
                    inner2, i = _collect_until_brace(lines, i)
                    js.extend(_indent_block(jam_to_js("\n".join(inner2))))
                    js.append("}")
                    i = _skip_blank_comments(lines, i + 1)
                elif nxt == "else {":
                    js.append("else {")
                    i += 1
                    inner3, i = _collect_until_brace(lines, i)
                    js.extend(_indent_block(jam_to_js("\n".join(inner3))))
                    js.append("}")
                    i = _skip_blank_comments(lines, i + 1)
                else:
                    break
            continue

        if line.startswith("else if ") and line.endswith("{"):
            cond = line[8:-1].strip()
            js.append(f"else if ({cond}) {{")
            i += 1
            inner, i = _collect_until_brace(lines, i)
            js.extend(_indent_block(jam_to_js("\n".join(inner))))
            js.append("}")
            i += 1
            continue

        if line == "else {":
            js.append("else {")
            i += 1
            inner, i = _collect_until_brace(lines, i)
            js.extend(_indent_block(jam_to_js("\n".join(inner))))
            js.append("}")
            i += 1
            continue

        # ---- DECL / ASSIGN ----
        if line.startswith("set "):
            after = line[4:]
            if " = " in after:
                var_name, value = after.split(" = ", 1)
                var_name = var_name.strip()
                value = value.strip()
                check_assignment(var_name, value)

                if value.startswith("map "):
                    tmp = value[4:].strip()
                    if "over" in tmp:
                        func, _, data = tmp.partition("over")
                        js.append(f"let {var_name} = {data.strip()}.map({func.strip()});")
                    else:
                        js.append(f"let {var_name} = {tmp};")
                else:
                    js.append(f"let {var_name} = {value};")
            else:
                js.append(f"/* malformed set: {line} */")
            i += 1
            continue

        # ---- FUNCTIONS ----
        if line.startswith("function ") and line.endswith("{"):
            head = line[9:-1].strip()
            name, params = _split_name_params(head)
            js.append(f"function {name}({params}) {{")
            i += 1
            inner, i = _collect_until_brace(lines, i)
            js.extend(_indent_block(jam_to_js("\n".join(inner))))
            js.append("}")
            i += 1
            continue

        if line.startswith("function anonymous ") and line.endswith("{"):
            head = line[len("function anonymous "):-1].strip()
            anon = _anon_name()
            _, params = _split_name_params(anon + " " + head)
            js.append(f"const {anon} = ({params}) => {{")
            i += 1
            inner, i = _collect_until_brace(lines, i)
            js.extend(_indent_block(jam_to_js("\n".join(inner))))
            js.append("};")
            i += 1
            continue

        # return
        if line.startswith("return "):
            js.append(f"return {line[7:].strip()};")
            i += 1
            continue

        # ---- LOOPS ----
        if line.startswith("repeat ") and line.endswith("{"):
            count = line[len("repeat "):-1].strip()
            js.append(f"for (let i = 0; i < {count}; i++) {{")
            i += 1
            inner, i = _collect_until_brace(lines, i)
            js.extend(_indent_block(jam_to_js("\n".join(inner))))
            js.append("}")
            i += 1
            continue

        # ---- I/O + STRING/Numeric Ops ----
        if line.startswith("print "):
            content = line[6:].strip()
            if not (content.startswith('"') or content.startswith("'")):
                content = f'"{_trim_quotes(content)}"'
            js.append(f"console.log({content});")
            i += 1
            continue

        if line.startswith("say "):
            content = line[4:].strip()
            if not (content.startswith('"') or content.startswith("'")):
                content = f'"{_trim_quotes(content)}"'
            js.append(f"console.log({content});")
            i += 1
            continue

        if line.startswith("ask "):
            part = line[4:].strip()
            target_var = None
            if " and store in " in part:
                q, _, v = part.partition(" and store in ")
                target_var = v.strip()
            elif " into " in part:
                q, _, v = part.partition(" into ")
                target_var = v.strip()
            else:
                q = part
            q = q.strip()
            if target_var:
                js.append(f"let {target_var} = prompt({q});")
            else:
                js.append(f"prompt({q});")
            i += 1
            continue

        if line.startswith("add "):
            a, _, rest = line[4:].partition(" and ")
            b, _, var = rest.partition(" into ")
            js.append(f"let {var.strip()} = {a.strip()} + {b.strip()};")
            i += 1
            continue

        if line.startswith("multiply "):
            a, _, rest = line[9:].partition(" and ")
            b, _, var = rest.partition(" into ")
            js.append(f"let {var.strip()} = {a.strip()} * {b.strip()};")
            i += 1
            continue

        if line.startswith("length of "):
            arg = line[len("length of "):].strip()
            if " into " in arg:
                expr, _, var = arg.partition(" into ")
                js.append(f"let {var.strip()} = ({expr.strip()}).length;")
            else:
                js.append(f"console.log(({arg}).length);")
            i += 1
            continue

        if line.startswith("uppercase "):
            arg = line[len("uppercase "):].strip()
            if " into " in arg:
                expr, _, var = arg.partition(" into ")
                js.append(f"let {var.strip()} = ({expr.strip()}).toUpperCase();")
            else:
                js.append(f"console.log(String({arg}).toUpperCase());")
            i += 1
            continue

        if line.startswith("lowercase "):
            arg = line[len("lowercase "):].strip()
            if " into " in arg:
                expr, _, var = arg.partition(" into ")
                js.append(f"let {var.strip()} = ({expr.strip()}).toLowerCase();")
            else:
                js.append(f"console.log(String({arg}).toLowerCase());")
            i += 1
            continue

        if line.startswith("reverse "):
            arg = line[len("reverse "):].strip()
            if " into " in arg:
                expr, _, var = arg.partition(" into ")
                js.append(f"let {var.strip()} = String({expr.strip()}).split('').reverse().join('');")
            else:
                js.append(f"console.log(String({arg}).split('').reverse().join(''));")
            i += 1
            continue

        if line.startswith("square of "):
            arg = line[len("square of "):].strip()
            if " into " in arg:
                expr, _, var = arg.partition(" into ")
                e = expr.strip()
                js.append(f"let {var.strip()} = ({e}) * ({e});")
            else:
                e = arg
                js.append(f"console.log(({e}) * ({e}));")
            i += 1
            continue

        if line.startswith("sqrt of "):
            arg = line[len("sqrt of "):].strip()
            if " into " in arg:
                expr, _, var = arg.partition(" into ")
                js.append(f"let {var.strip()} = Math.sqrt({expr.strip()});")
            else:
                js.append(f"console.log(Math.sqrt({arg}));")
            i += 1
            continue

        if line.startswith("random between "):
            rest = line[len("random between "):]
            a, _, rest2 = rest.partition(" and ")
            b, _, var = rest2.partition(" into ")
            a = a.strip();
            b = b.strip();
            v = var.strip()
            js.append(f"let {v} = Math.floor(Math.random() * (({b}) - ({a}) + 1)) + ({a});")
            i += 1
            continue

        if line == "timer start":
            js.append('console.time("jamTimer");')
            i += 1
            continue

        if line == "timer stop":
            js.append('console.timeEnd("jamTimer");')
            i += 1
            continue

        if line.startswith("wait "):
            ms = line[5:].strip()
            js.append(f"/* wait {ms} ms (no-op in compiled JS) */")
            i += 1
            continue

        if line.startswith("choose from "):
            rest = line[len("choose from "):]
            items_part, _, var = rest.partition(" into ")
            items = [it.strip() for it in items_part.split(",")]
            arr = ", ".join(items)
            js.append(f"let {var.strip()} = [{arr}][Math.floor(Math.random()*[{arr}].length)];")
            i += 1
            continue

        if line.startswith("call "):
            call_part = line[5:].strip()
            if "(" in call_part and call_part.endswith(")"):
                js.append(f"{call_part};")
            else:
                js.append(f"{call_part}();")
            i += 1
            continue

        if line == "}":
            js.append("}")
            i += 1
            continue

        js.append(line if line.endswith("{") or line.endswith("}") else f"{line};")
        i += 1

    if type_warnings:
        js.append("\n/* Type Warnings:")
        for w in type_warnings:
            js.append(f"   - {w}")
        js.append("*/")
        type_warnings.clear()

    return "\n".join(js)


def _split_name_params(head: str) -> Tuple[str, str]:
    """
    head like:  myFunc (a, b)    or   anonymous (x)
    returns (name, 'a, b')
    """
    if "(" in head and head.endswith(")"):
        name = head[: head.index("(")].strip()
        params = head[head.index("(") + 1: -1].strip()
        return name or _anon_name(), params
    return (head.strip() or _anon_name()), ""


def _collect_until_brace(lines: List[str], start: int) -> Tuple[List[str], int]:
    """Collect a flat block until a single closing '}' encountered."""
    block: List[str] = []
    i = start
    depth = 0
    while i < len(lines):
        line = lines[i].strip()
        raw = lines[i]
        if not line or line.startswith("#"):
            i += 1
            continue
        if line.endswith("{"):
            depth += 1
            block.append(raw)
        elif line == "}":
            if depth == 0:
                return block, i
            depth -= 1
            block.append(raw)
        else:
            block.append(raw)
        i += 1
    return block, i


def _indent_block(js_str: str, spaces: int = 2) -> List[str]:
    """Indents a block of JavaScript code.

    Args:
        js_str: The JavaScript code as a string.
        spaces: The number of spaces to indent each line.

    Returns:
        A list of strings, where each string is an indented line of code.
    """
    pad = " " * spaces
    return [pad + ln if ln else "" for ln in js_str.splitlines()]


def _skip_blank_comments(lines: List[str], i: int) -> int:
    """Skips over blank lines and comments.

    Args:
        lines: A list of code lines.
        i: The starting index.

    Returns:
        The index of the next non-blank, non-comment line.
    """
    while i < len(lines):
        s = lines[i].strip()
        if not s or s.startswith("#"):
            i += 1
        else:
            break
    return i


def _parse_arrow(fn: str):
    """
    Parse a string like '(n) => n * 2' into a Python lambda.
    Only supports single-parameter, single-expression arrows.
    """
    fn = fn.strip()
    if fn.startswith("(") and "=>" in fn:
        params, _, expr = fn.partition("=>")
        params = params.strip("() ").strip()
        expr = expr.strip()
        return lambda x: eval(expr, {"__builtins__": {}}, {params: x})
    return None


# ---------- Interpreter (Python) ----------
def run_jam_code(code: str) -> str:
    """
    Executes JAM code from a string and returns the captured output as a string.
    """
    import io, sys, random, math, time

    output = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = output

    variables: Dict[str, Any] = {}
    functions: Dict[str, Tuple[List[str], List[str]]] = {}  # name -> (params, body)
    timer_start: Optional[float] = None

    def say(x):
        print(x)

    def eval_expr(expr: str) -> Any:
        """
        Evaluates a string expression into a Python value (bool, str, int, float, list, or variable).
        """
        e = expr.strip()

        if e == "true": return True
        if e == "false": return False

        if (e.startswith('"') and e.endswith('"')) or (e.startswith("'") and e.endswith("'")):
            return e[1:-1]

        if e.startswith("[") and e.endswith("]"):
            inner = e[1:-1].strip()
            if not inner:
                return []
            parts = [p.strip() for p in inner.split(",")]
            return [eval_expr(p) for p in parts]

        if e.isdigit() or (e.startswith('-') and e[1:].isdigit()):
            try:
                return int(e)
            except:
                pass

        try:
            if "." in e:
                return float(e)
        except:
            pass

        if e in variables:
            return variables[e]

        try:
            return eval(e, {"__builtins__": {}}, dict(variables))
        except:
            return e

    def eval_condition(cond: str) -> bool:
        """Evaluates a condition string to a boolean.

        Args:
            cond: The condition string to evaluate.

        Returns:
            True if the condition is met, False otherwise.
        """
        try:
            val = eval(cond.replace("true", "True").replace("false", "False"),
                       {"__builtins__": {}}, dict(variables))
            return bool(val)
        except:
            return False

    def parse_block(lines: List[str], start: int) -> Tuple[List[str], int]:
        """
        Parses a block of code from a list of lines, starting at the given index, and returns the block with the ending index.
        """
        block: List[str] = []
        i = start
        depth = 0
        while i < len(lines):
            s = lines[i].strip()
            if not s or s.startswith("#"):
                i += 1
                continue
            if s.endswith("{"):
                depth += 1
                block.append(lines[i])
            elif s == "}":
                if depth == 0:
                    return block, i
                depth -= 1
                block.append(lines[i])
            else:
                block.append(lines[i])
            i += 1
        return block, i

    def run_lines(lines: List[str], start: int = 0, local_vars: Optional[Dict[str, Any]] = None) -> int:
        """
        Interprets and executes JAM code line by line.

        Handles control flow (if/else, repeat), variable assignment, expressions,
        function definitions/calls/returns, input/output (print, say, ask),
        string and math operations, randomness, timers, and simple utilities.

        Args:
            lines: List of JAM code lines.
            start: Index to begin execution from (default 0).
            local_vars: Optional dictionary of variables for local scope.

        Returns:
            The index position where execution stopped.
        """
        nonlocal timer_start
        env = variables if local_vars is None else local_vars
        i = start
        while i < len(lines):
            raw = lines[i]
            line = raw.strip()
            if not line or line.startswith("#"):
                i += 1
                continue

            if line.startswith("if ") and line.endswith("{"):
                cond = line[3:-1].strip()
                i += 1
                block, j = parse_block(lines, i)
                taken = False
                if eval_condition(cond):
                    run_lines(block, 0, env)
                    taken = True
                i = j + 1
                i = _skip_blank(lines, i)
                while i < len(lines):
                    nxt = lines[i].strip()
                    if nxt.startswith("else if ") and nxt.endswith("{"):
                        cond2 = nxt[8:-1].strip()
                        i += 1
                        blk2, j2 = parse_block(lines, i)
                        if not taken and eval_condition(cond2):
                            run_lines(blk2, 0, env)
                            taken = True
                        i = j2 + 1
                        i = _skip_blank(lines, i)
                    elif nxt == "else {":
                        i += 1
                        blk3, j3 = parse_block(lines, i)
                        if not taken:
                            run_lines(blk3, 0, env)
                        i = j3 + 1
                        break
                    else:
                        break
                continue

            if line.startswith("repeat ") and line.endswith("{"):
                cnt = int(eval_expr(line[len("repeat "):-1].strip()))
                i += 1
                block, j = parse_block(lines, i)
                for _ in range(cnt):
                    run_lines(block, 0, env)
                i = j + 1
                continue
            if line.startswith("set "):
                after = line[4:]
                if " = " in after:
                    var, expr = after.split(" = ", 1)
                    var = var.strip();
                    expr = expr.strip()

                    if expr.startswith("map "):
                        tmp = expr[4:].strip()
                        func_str, _, data_str = tmp.partition("over")
                        data = eval_expr(data_str.strip())

                        fn = func_str.strip()
                        lam = _parse_arrow(fn)

                        if isinstance(data, list) and lam is not None:
                            env[var] = [lam(el) for el in data]
                        else:
                            env[var] = data  # fallback
                    else:
                        env[var] = eval_expr(expr)
                i += 1
                continue

            if line.startswith("print "):
                print(eval_expr(line[6:].strip()))
                i += 1
                continue
            if line.startswith("say "):
                print(eval_expr(line[4:].strip()))
                i += 1
                continue

            if line.startswith("ask "):
                part = line[4:].strip()
                if " and store in " in part:
                    q, _, var = part.partition(" and store in ")
                elif " into " in part:
                    q, _, var = part.partition(" into ")
                else:
                    q, var = part, None
                ans = f"(input requested: {eval_expr(q)})"
                if var:
                    env[var.strip()] = ans
                else:
                    print(ans)
                i += 1
                continue

            if line.startswith("add "):
                a, _, rest = line[4:].partition(" and ")
                b, _, var = rest.partition(" into ")
                env[var.strip()] = eval_expr(a) + eval_expr(b)
                i += 1
                continue
            if line.startswith("multiply "):
                a, _, rest = line[9:].partition(" and ")
                b, _, var = rest.partition(" into ")
                env[var.strip()] = eval_expr(a) * eval_expr(b)
                i += 1
                continue
            if line.startswith("length of "):
                arg = line[len("length of "):].strip()
                if " into " in arg:
                    expr, _, var = arg.partition(" into ")
                    env[var.strip()] = len(str(eval_expr(expr)))
                else:
                    print(len(str(eval_expr(arg))))
                i += 1
                continue

            if line.startswith("uppercase "):
                arg = line[len("uppercase "):].strip()
                if " into " in arg:
                    expr, _, var = arg.partition(" into ")
                    env[var.strip()] = str(eval_expr(expr)).upper()
                else:
                    print(str(eval_expr(arg)).upper())
                i += 1
                continue

            if line.startswith("lowercase "):
                arg = line[len("lowercase "):].strip()
                if " into " in arg:
                    expr, _, var = arg.partition(" into ")
                    env[var.strip()] = str(eval_expr(expr)).lower()
                else:
                    print(str(eval_expr(arg)).lower())
                i += 1
                continue

            if line.startswith("reverse "):
                arg = line[len("reverse "):].strip()
                if " into " in arg:
                    expr, _, var = arg.partition(" into ")
                    env[var.strip()] = str(eval_expr(expr))[::-1]
                else:
                    print(str(eval_expr(arg))[::-1])
                i += 1
                continue

            if line.startswith("square of "):
                arg = line[len("square of "):].strip()
                if " into " in arg:
                    expr, _, var = arg.partition(" into ")
                    val = eval_expr(expr)
                    env[var.strip()] = val * val
                else:
                    val = eval_expr(arg)
                    print(val * val)
                i += 1
                continue

            if line.startswith("sqrt of "):
                arg = line[len("sqrt of "):].strip()
                if " into " in arg:
                    expr, _, var = arg.partition(" into ")
                    env[var.strip()] = math.sqrt(eval_expr(expr))
                else:
                    print(math.sqrt(eval_expr(arg)))
                i += 1
                continue

            if line.startswith("random between "):
                rest = line[len("random between "):]
                a, _, rest2 = rest.partition(" and ")
                b, _, var = rest2.partition(" into ")
                lo = int(eval_expr(a));
                hi = int(eval_expr(b))
                env[var.strip()] = random.randint(lo, hi)
                i += 1
                continue

            if line == "timer start":
                timer_start = time.time()
                i += 1
                continue

            if line == "timer stop":
                if timer_start is not None:
                    elapsed = time.time() - timer_start
                    print(f"Time elapsed: {elapsed:.2f} seconds")
                    timer_start = None
                i += 1
                continue

            if line.startswith("wait "):
                i += 1
                continue

            if line.startswith("choose from "):
                rest = line[len("choose from "):]
                items_part, _, var = rest.partition(" into ")
                items = [p.strip() for p in items_part.split(",")]
                pool = [eval_expr(p) for p in items]
                import random as _r
                env[var.strip()] = _r.choice(pool) if pool else None
                i += 1
                continue

            if line.startswith("function ") and line.endswith("{"):
                head = line[9:-1].strip()
                name, params = _split_name_params(head)
                i += 1
                body, j = parse_block(lines, i)
                functions[name] = ([p.strip() for p in params.split(",")] if params else [], body)
                i = j + 1
                continue

            if line.startswith("return "):
                val = eval_expr(line[7:].strip())
                raise _JamReturn(val)
            if line.startswith("call "):
                callp = line[5:].strip()
                if "(" in callp and callp.endswith(")"):
                    fname = callp[:callp.index("(")].strip()
                    args_s = callp[callp.index("(") + 1:-1].strip()
                    args = [a.strip() for a in args_s.split(",")] if args_s else []
                else:
                    fname = callp
                    args = []
                if fname in functions:
                    params, body = functions[fname]
                    local = dict(variables)
                    for pi, ai in zip(params, args):
                        local[pi] = eval_expr(ai)
                    try:
                        run_lines(body, 0, local)
                        variables["last_return"] = None
                    except _JamReturn as r:
                        variables["last_return"] = r.value
                else:
                    fn = variables.get(fname)
                    if callable(fn):
                        variables["last_return"] = fn(*[eval_expr(a) for a in args])
                i += 1
                continue

            if line == "}":
                i += 1
                continue

            i += 1

        return i

    class _JamReturn(Exception):
        """Exception used to handle 'return' statements in Jam functions."""

        def __init__(self, value: Any):
            self.value = value

    def _skip_blank(lines: List[str], idx: int) -> int:
        """
        Skips blank lines and comments, returning the next valid index.
        """
        while idx < len(lines):
            s = lines[idx].strip()
            if not s or s.startswith("#"):
                idx += 1
            else:
                break
        return idx

    all_lines = code.splitlines()
    run_lines(all_lines, 0, None)

    sys.stdout = sys_stdout
    return output.getvalue()


# ---------- Demo ----------
if __name__ == "__main__":
    jam_code = """
# Sample Jam code
set x = 5
if x > 3 {
    print "Hello"
} else if x < 2 {
    print "Small"
} else {
    print "Medium"
}

function anonymous (n) {
    return n * 2
}

set numbers = [1, 2, 3]
set doubled = map (n) => n * 2 over numbers
print doubled

add 3 and 9 into total
print total

uppercase "jam" into U
print U
random between 10 and 12 into r
print r
"""
    js_code = jam_to_js(jam_code)
    print("Generated JavaScript:\n")
    print(js_code)
    print("\n--- Interpreter Output ---")
    print(run_jam_code(jam_code))


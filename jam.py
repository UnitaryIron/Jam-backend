from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
import re
from random import choice
from enum import Enum

JamType = Union[str, int, float, bool, list]


class TypeErrorJam(Exception):
    pass


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


# ---------- Interpreter (Python) ----------

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

_anon_counter = 0

def _anon_name() -> str:
    """Generates a unique name for an anonymous function.

    Returns:
        A string representing a unique function name.
    """
    global _anon_counter
    _anon_counter += 1
    return f"_anon_{_anon_counter}"


def _split_name_params(head: str) -> Tuple[str, str]:
    """
    head like:  myFunc (a, b)    or   anonymous (x)
    returns (name, 'a, b')
    """
    if "(" in head and head.endswith(")"):
        name = head[: head.index("(")].strip()
        params = head[head.index("(") + 1 : -1].strip()
        return name or _anon_name(), params
    return (head.strip() or _anon_name()), ""

def run_jam_code(code: str) -> str:
    import io, sys, random, math, time

    output = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = output

   # Error Detection System

    class ErrorSeverity(Enum):
        HINT = "Hint"
        WARNING = "Warning"
        ERROR = "Error"
        CONCEPT = "Concept"

    class SyntaxErrorJam(Exception):
        def __init__(self, message: str, line_num: int, line: str,
                     suggestion: str = "", example: str = "",
                     severity: ErrorSeverity = ErrorSeverity.ERROR):
            self.message = message
            self.line_num = line_num
            self.line = line
            self.suggestion = suggestion
            self.example = example
            self.severity = severity
            super().__init__(message)

    suggestion_rule = Callable[[str, int, str], List[tuple[str, ErrorSeverity]]]
    suggestion_rules: List[suggestion_rule] = []

    def format_n_show_error(e: SyntaxErrorJam) -> None:
        """Format and print a SyntaxErrorJam to the output."""
        print(f"{e.severity.value}: {e.message} (line {e.line_num})")
        if e.line is not None:
            print(f"  >> {e.line.strip()}")
        if e.suggestion:
            print(f"Suggestion: {e.suggestion}")
        if e.example:
            print(f"Example: {e.example}")

    def register_suggestion(rule: suggestion_rule):
        suggestion_rules.append(rule)

    def suggest_correction(name: str, line_num: int, line: str) -> List[tuple[str, ErrorSeverity]]:
        results = []
        for rule in suggestion_rules:
            results.extend(rule(name, line_num, line))
        return results

    def rule_compare_operator(name, line_num, line):
        out = []
        if name in line:
            pos = line.find(name)
        else:
            pos = 0

        if "==" in line and "=" not in line[:pos]:
            out.append(("Did you mean '=' instead of '=='?", ErrorSeverity.HINT))
        return out

    def rule_colon_after_keywords(name, line_num, line):
        if "while" in line and line.endswith(":"):
            return [("Jam uses {} for blocks, not :", ErrorSeverity.ERROR)]
        return []

    register_suggestion(rule_compare_operator)
    register_suggestion(rule_colon_after_keywords)


    @dataclass
    class KeywordPattern:
        keyword: str
        patterns: List[str]
        messages: List[str]

    keyword_patterns = [
        KeywordPattern(
            "if",
            ["i", "f", "fi", "iff", "ig"],
            [
                "Did you mean 'if'?",
                "Looks like you're aiming for 'if'.",
                "Try 'if' instead of that.",
            ]
        ),
        KeywordPattern(
            "else",
            ["els", "ese", "esle", "elsee", "eles", "ells"],
            [
                "Did you mean 'else'?",
                "Looks like a typo of 'else'.",
                "Use 'else' instead.",
            ]
        ),
        KeywordPattern(
            "function",
            ["functon", "functin", "funtion", "funciton", "fucntion", "funcshun"],
            [
                "Did you mean 'function'?",
                "That looks close to 'function'.",
            ]
        ),
        KeywordPattern(
            "return",
            ["retun", "retrn", "etur", "reutrn", "output"],
            [
                "Did you mean 'return'?",
                "That resembles 'return'.",
            ]
        ),
        KeywordPattern(
            "repeat",
            ["repea", "repate", "repeet", "loop", "again"],
            [
                "Did you mean 'repeat'?",
                "Looks like a typo of 'repeat'.",
            ]
        ),
        KeywordPattern(
            "set",
            ["se", "st", "est", "sett", "assign", "let", "var"],
            [
                "Try using 'set'.",
                "You probably meant 'set'."
            ]
        ),
    ]

    validator = Callable[[str, int, str], None]
    validators: List[validator] = []

    def register_validator(v: validator):
        validators.append(v)

    def validate_variable_name(name: str, line_num: int, line: str):
        for validator in validators:
            validator(name, line_num, line)

    # ===== Validator implementations =====

    def validate_empty_name(name, line_num, line):
        if not name:
            raise SyntaxErrorJam(
                "Variable name missing.",
                line_num, line,
                "Variable names start with letters and can contain letters, numbers, and underscores.",
                "set myVariable = 10"
            )

    def validate_password(name, line_num, line):
        if "password" in name.lower():
            raise SyntaxErrorJam(
                f"Variable name '{name}' contains sensitive information.",
                line_num, line,
                "Avoid using 'password' in variable names.",
                severity=ErrorSeverity.CONCEPT
            )

    def validate_braces(name, line_num, line):
        if name.startswith("{") and not name.endswith("}"):
            raise SyntaxErrorJam(
                f"Variable name '{name}' doesn't have closing braces!",
                line_num, line,
                "Close any opening braces."
            )

    def validate_keyword_typos(name, line_num, line):
        for kp in keyword_patterns:
            if any(name.startswith(p) for p in kp.patterns):
                raise SyntaxErrorJam(
                    f"'{name}' looks like a misspelling of '{kp.keyword}'.",
                    line_num, line,
                    choice(kp.messages),
                    severity=ErrorSeverity.CONCEPT
                )

    def validate_allowed_chars(name, line_num, line):
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            raise SyntaxErrorJam(
                f"Invalid characters in '{name}'.",
                line_num, line,
                "Use only letters, digits, and underscores.",
                "set my_variable = 10"
            )

    def validate_reserved(name, line_num, line):
        reserved = {'if', 'else', 'function', 'return', 'repeat', 'set', 'print', 'say', 'ask'}
        if name in reserved:
            raise SyntaxErrorJam(
                f"'{name}' is a reserved keyword.",
                line_num, line,
                "Choose a different variable name.",
                f"set {name}_value = 10"
            )

    # Register validators
    for v in [
        validate_empty_name,
        validate_password,
        validate_braces,
        validate_keyword_typos,
        validate_allowed_chars,
        validate_reserved
    ]:
        register_validator(v)

    def check_number_bounds(value: str, context: str) -> Optional[tuple[str, ErrorSeverity]]:
        try:
            num = float(value)
            if context == "repeat" and num > 1000:
                return f"Repeating {int(num)} times might be too many!", ErrorSeverity.WARNING
            if abs(num) > 1e10:
                return "That number is extremely large.", ErrorSeverity.WARNING
            if 0 < abs(num) < 1e-10:
                return "Number is extremely close to zero.", ErrorSeverity.WARNING
        except:
            pass
        return None

    variables: Dict[str, Any] = {}
    functions: Dict[str, Tuple[List[str], List[str]]] = {}  # name -> (params, body)
    timer_start: Optional[float] = None

    def say(x):
        print(x)

    def eval_expr(expr: str) -> Any:
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
        try:
            val = eval(cond.replace("true", "True").replace("false", "False"),
                       {"__builtins__": {}}, dict(variables))
            return bool(val)
        except:
            return False

    def parse_block(lines: List[str], start: int) -> Tuple[List[str], int]:
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
                    var = var.strip()
                    expr = expr.strip()

                    try:
                        validate_variable_name(var, i + 1, line)
                    except SyntaxErrorJam as error:
                        format_n_show_error(error)
                        i += 1
                        continue

                    if expr.startswith("map "):
                        tmp = expr[4:].strip()
                        func_str, _, data_str = tmp.partition("over")
                        data = eval_expr(data_str.strip())

                        fn = func_str.strip()
                        lam = _parse_arrow(fn)

                        if isinstance(data, list) and lam is not None:
                            env[var] = [lam(el) for el in data]
                        else:
                            env[var] = data
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
                lo = int(eval_expr(a))
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
                call = line[5:].strip()
                if "(" in call and call.endswith(")"):
                    name = call[:call.index("(")].strip()
                    args_s = call[call.index("(") + 1:-1].strip()
                    args = [a.strip() for a in args_s.split(",")] if args_s else []
                else:
                    name = call
                    args = []
                if name in functions:
                    params, body = functions[name]
                    local = dict(variables)
                    for pi, ai in zip(params, args):
                        local[pi] = eval_expr(ai)
                    try:
                        run_lines(body, 0, local)
                        variables["last_return"] = None
                    except _JamReturn as r:
                        variables["last_return"] = r.value
                else:
                    fn = variables.get(name)
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
        def __init__(self, value: Any):
            self.value = value

    def _skip_blank(lines: List[str], idx: int) -> int:
        while idx < len(lines):
            s = lines[idx].strip()
            if not s or s.startswith("#"):
                idx += 1
            else:
                break
        return idx

    all_lines = code.splitlines()
    try:
        run_lines(all_lines, 0, None)
    except SyntaxErrorJam as e:
        format_n_show_error(e)
    except Exception as ex:
        print(f"Unexpected Error: {ex}")

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
    print(run_jam_code(jam_code))

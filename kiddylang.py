def run_jam_code(code: str) -> str:
    import io
    import sys
    import random
    import math
    import time
    import pyttsx3

    variables = {}
    lists = {}
    functions = {}
    timer_start = None
    last_return = None

    output = io.StringIO()
    sys.stdout = output

    def say(text):
        print(f"(say): {text}")

    def run_program(lines):
        nonlocal timer_start, last_return
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line == "" or line.startswith("#"):
                i += 1
                continue

            if line.startswith("let "):
                parts = line[4:].split(" = ")
                variables[parts[0].strip()] = eval_expr(parts[1].strip())

            elif line.startswith("print "):
                to_print = line[6:].strip()
                print(eval_expr(to_print))

            elif line.startswith("say "):
                to_say = line[4:].strip()
                say(eval_expr(to_say))

            elif line.startswith("ask "):
                print("ask is not supported in web version")

            elif line.startswith("add "):
                parts = line[4:].split(" and ")
                a = eval_expr(parts[0].strip())
                b, var = parts[1].split(" into ")
                b = eval_expr(b.strip())
                variables[var.strip()] = a + b

            elif line.startswith("multiply "):
                parts = line[9:].split(" and ")
                a = eval_expr(parts[0].strip())
                b, var = parts[1].split(" into ")
                b = eval_expr(b.strip())
                variables[var.strip()] = a * b

            elif line.startswith("length of "):
                name = line[len("length of "):].strip()
                print(len(str(eval_expr(name))))

            elif line.startswith("uppercase "):
                name = line[len("uppercase "):].strip()
                print(str(eval_expr(name)).upper())

            elif line.startswith("lowercase "):
                name = line[len("lowercase "):].strip()
                print(str(eval_expr(name)).lower())

            elif line.startswith("reverse "):
                name = line[len("reverse "):].strip()
                print(str(eval_expr(name))[::-1])

            elif line.startswith("square of "):
                num = eval_expr(line[len("square of "):].strip())
                print(num ** 2)

            elif line.startswith("sqrt of "):
                num = eval_expr(line[len("sqrt of "):].strip())
                print(math.sqrt(num))

            elif line.startswith("random between "):
                parts = line[len("random between "):].split(" and ")
                a = int(eval_expr(parts[0]))
                b = int(eval_expr(parts[1]))
                print(random.randint(a, b))

            elif line.startswith("wait "):
                pass  # skip wait for browser safety

            elif line.startswith("choose from "):
                list_part, var_part = line.split("into")
                items = [s.strip('" ') for s in list_part.split("from")[1].strip().split(",")]
                chosen = random.choice(items)
                variables[var_part.strip()] = chosen

            elif line.startswith("function "):
                name = line.split(" ")[1]
                i += 1
                body = []
                while not lines[i].strip() == "}":
                    body.append(lines[i])
                    i += 1
                functions[name] = body

            elif line.startswith("call "):
                name = line.split(" ")[1]
                run_program(functions[name])
                variables["last_return"] = last_return

            elif line.startswith("repeat "):
                count = int(eval_expr(line.split(" ")[1]))
                i += 1
                block = []
                while not lines[i].strip() == "}":
                    block.append(lines[i])
                    i += 1
                for _ in range(count):
                    run_program(block)

            elif line.startswith("if "):
                condition = line[3:].split("{")[0].strip()
                i += 1
                block = []
                while not lines[i].strip() == "}":
                    block.append(lines[i])
                    i += 1
                if eval_condition(condition):
                    run_program(block)

            elif line.startswith("timer start"):
                timer_start = time.time()

            elif line.startswith("timer stop"):
                if timer_start:
                    elapsed = time.time() - timer_start
                    print(f"Time elapsed: {elapsed:.2f} seconds")

            else:
                print(f"Unknown command: {line}")
            i += 1

    def eval_expr(expr):
        expr = expr.strip()
        if expr in variables:
            return variables[expr]
        elif expr.startswith('"') and expr.endswith('"'):
            return expr.strip('"')
        elif expr == "true":
            return True
        elif expr == "false":
            return False
        elif expr.startswith("[") and expr.endswith("]"):
            return eval(expr)
        else:
            try:
                return int(expr)
            except:
                return expr

    def eval_condition(condition):
        try:
            for var in variables:
                condition = condition.replace(var, repr(variables[var]))
            condition = condition.replace("true", "True").replace("false", "False")
            return eval(condition)
        except:
            return False

    lines = code.strip().splitlines()
    run_program(lines)

    sys.stdout = sys.__stdout__
    return output.getvalue()

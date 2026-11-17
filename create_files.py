#!/usr/bin/env python3
"""Enterprise Project Generator & File Manager (Python, R and text files)."""
from pathlib import Path
import random, re, shutil


ROOT = Path("Enterprise_Business_Platform")
STRUCTURE = {
    "Core_Management": ["System_Configuration", "System_Services"],
    "Data_Management": ["Database_Operations", "Data_Processing"],
    "Business_Operations": ["Business_Workflows", "Business_Services"],
    "Integration_Management": ["External_Integrations", "Internal_Integrations"],
    "Analytics_Management": ["Business_Analytics", "Reporting_Services"],
}
MAINS = list(STRUCTURE)
EXTS = {"1": ("Python", ".py"), "2": ("R", ".R"), "3": ("Text", ".txt")}
ALL_EXTS = [e for _, e in EXTS.values()]
FILE_RE = re.compile(r"_(\d+)\.(py|R|r|txt)$")




# ---------- folders ----------
def create_structure():
    for main, subs in STRUCTURE.items():
        for sub in subs:
            (ROOT/main/sub).mkdir(parents=True, exist_ok=True)
    print("Enterprise folder structure ready:", ROOT.resolve())


def managed_files(folder):
    """Python, R and text files directly inside a folder, in number order."""
    if not folder.exists(): return []
    return sorted((p for p in folder.iterdir()
                   if p.is_file() and p.suffix in (".py", ".R", ".r", ".txt")), key=file_key)


def count_files(folder):
    return len(managed_files(folder))


def show_tree():
    print("\nAvailable folders:")
    for i, main in enumerate(MAINS, 1):
        print(f"  {i}. {main}")
        for sub in STRUCTURE[main]:
            print(f"       - {sub} ({count_files(ROOT/main/sub)} files)")


def ask_choice(prompt, high):
    while True:
        value = input(prompt).strip()
        if value.isdigit() and 1 <= int(value) <= high:
            return int(value)
        print(f"Please enter a number from 1 to {high}.")


def choose_folders(allow_both=False):
    """Pick a main folder, then one sub folder (or both). Returns a list of folders."""
    show_tree()
    main = MAINS[ask_choice("\nSelect main folder number: ", len(MAINS))-1]
    subs = STRUCTURE[main]
    print(f"\nSub folders in {main}:")
    for i, sub in enumerate(subs, 1):
        print(f"  {i}. {sub} ({count_files(ROOT/main/sub)} files)")
    if allow_both:
        print(f"  {len(subs)+1}. Both sub folders")
    pick = ask_choice("Select sub folder number: ", len(subs)+(1 if allow_both else 0))
    chosen = subs if pick > len(subs) else [subs[pick-1]]
    folders = [ROOT/main/s for s in chosen]
    for f in folders: f.mkdir(parents=True, exist_ok=True)
    return folders


def choose_folder():
    return choose_folders()[0]




# ---------- input helpers ----------
def ask_number(prompt, kind=float, minimum=1):
    while True:
        try:
            value = kind(input(prompt).strip())
            if value >= minimum: return value
        except ValueError:
            pass
        print(f"Please enter a valid number (minimum {minimum}).")


def ask_size_kb():
    """Ask for a size in KB or MB and return it in KB."""
    while True:
        unit = input("Size unit - 1) KB  2) MB: ").strip()
        if unit in ("1", "2"): break
        print("Please enter 1 or 2.")
    label = "KB" if unit == "1" else "MB"
    size = ask_number(f"Size of each file in {label}: ", float, 0.001)
    return size if unit == "1" else size*1024


def clean_name(name):
    name = name.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_-]", "", name) or "business_module"




# ---------- numbering (continues across ALL folders) ----------
def next_number():
    nums = [int(m.group(1)) for p in ROOT.rglob("*")
            if p.is_file() and (m := FILE_RE.search(p.name))]
    return max(nums, default=0) + 1




# ---------- varied dummy code ----------
WORDS = ["order", "invoice", "customer", "ticket", "shipment", "payment",
         "report", "account", "contract", "vendor", "product"]
STATUS = ["new", "active", "pending", "approved", "closed", "failed"]


def t_calc(r, i, d):
    return (f"def calc_{d}_{i}(value):\n"
            f'    """Apply a {d} rate of {r.randint(2, 50)}% plus offset {r.randint(1, 9)}."""\n'
            f"    return round(value * {r.randint(2, 50)} / 100 + {r.randint(1, 9)}, 2)\n")


def t_validate(r, i, d):
    n = r.randint(3, 9)
    return (f"def validate_{d}_{i}(text):\n"
            f'    """Text must have at least {n} characters and no spaces."""\n'
            f'    return isinstance(text, str) and len(text) >= {n} and " " not in text\n')


def t_records(r, i, d):
    rows = [{"id": f"{d[:3].upper()}-{r.randint(1000, 9999)}",
             "kind": r.choice(WORDS), "status": r.choice(STATUS),
             "amount": r.randint(10, 9999)} for _ in range(r.randint(2, 4))]
    return f"DATA_{i} = {rows!r}\n"


def t_class(r, i, d):
    f1, f2 = r.sample(WORDS, 2)
    return (f"class {d.title().replace('_', '')}Item{i}:\n"
            f'    """Small {d} holder for {f1} and {f2}."""\n'
            f"    def __init__(self, {f1}, {f2}={r.randint(1, 99)}):\n"
            f"        self.{f1} = {f1}\n"
            f"        self.{f2} = {f2}\n"
            f"    def describe(self):\n"
            f'        return "{d}:" + str(self.{f1}) + ":" + str(self.{f2})\n')


def t_filter(r, i, d):
    return (f"def filter_{d}_{i}(rows, minimum={r.randint(10, 500)}):\n"
            f'    """Keep rows whose amount is at least minimum."""\n'
            f'    return [row for row in rows if row.get("amount", 0) >= minimum]\n')


def t_summary(r, i, d):
    return (f"def summarize_{d}_{i}(numbers):\n"
            f'    """Return count, total and average of numbers."""\n'
            f"    total = sum(numbers)\n"
            f'    return {{"count": len(numbers), "total": total, '
            f'"average": total / len(numbers) if numbers else 0}}\n')


def t_label(r, i, d):
    return (f"def label_{d}_{i}(name):\n"
            f'    """Build a {d} label with prefix {r.choice(WORDS)[:3].upper()}."""\n'
            f'    return "{r.choice(WORDS)[:3].upper()}-" + name.strip().upper() + "-{r.randint(100, 999)}"\n')


def t_loop(r, i, d):
    k = r.randint(2, 5)
    return (f"def total_{d}_{i}(limit={r.randint(5, 40)}):\n"
            f'    """Sum every {k}th number up to limit."""\n'
            f"    return sum(n for n in range(limit) if n % {k} == 0)\n")


TEMPLATES = [t_calc, t_validate, t_records, t_class, t_filter, t_summary, t_label, t_loop]


TOPICS = ["loader", "validator", "scheduler", "parser", "handler", "monitor", "tracker",
          "builder", "mapper", "router", "auditor", "exporter", "importer", "cache",
          "logger", "notifier", "resolver", "formatter", "checker", "processor"]


# ---------- R templates ----------
def r_calc(r, i, d):
    rate, off = r.randint(2, 50), r.randint(1, 9)
    return (f"calc_{d}_{i} <- function(value) {{\n"
            f"  # Apply a {rate}% rate plus an offset of {off}\n"
            f"  round(value * {rate} / 100 + {off}, 2)\n}}\n")


def r_validate(r, i, d):
    n = r.randint(3, 9)
    return (f"validate_{d}_{i} <- function(text) {{\n"
            f"  # Text must have at least {n} characters and no spaces\n"
            f'  is.character(text) && nchar(text) >= {n} && !grepl(" ", text, fixed = TRUE)\n}}\n')


def r_records(r, i, d):
    k = r.randint(2, 4)
    ids = ", ".join(f'"{d[:3].upper()}-{r.randint(1000, 9999)}"' for _ in range(k))
    kinds = ", ".join(f'"{r.choice(WORDS)}"' for _ in range(k))
    status = ", ".join(f'"{r.choice(STATUS)}"' for _ in range(k))
    amounts = ", ".join(str(r.randint(10, 9999)) for _ in range(k))
    return (f"DATA_{i} <- data.frame(\n  id = c({ids}),\n  kind = c({kinds}),\n"
            f"  status = c({status}),\n  amount = c({amounts}),\n  stringsAsFactors = FALSE\n)\n")


def r_item(r, i, d):
    f1, f2 = r.sample(WORDS, 2)
    return (f"new_{d}item{i} <- function({f1}, {f2} = {r.randint(1, 99)}) {{\n"
            f"  list({f1} = {f1}, {f2} = {f2})\n}}\n\n"
            f"describe_{d}item{i} <- function(item) {{\n"
            f'  paste0("{d}:", item${f1}, ":", item${f2})\n}}\n')


def r_filter(r, i, d):
    return (f"filter_{d}_{i} <- function(rows, minimum = {r.randint(10, 500)}) {{\n"
            f"  # Keep rows whose amount is at least minimum\n"
            f"  rows[rows$amount >= minimum, , drop = FALSE]\n}}\n")


def r_summary(r, i, d):
    return (f"summarize_{d}_{i} <- function(numbers) {{\n"
            f"  total <- sum(numbers)\n"
            f"  list(count = length(numbers), total = total,\n"
            f"       average = if (length(numbers) > 0) total / length(numbers) else 0)\n}}\n")


def r_label(r, i, d):
    return (f"label_{d}_{i} <- function(name) {{\n"
            f"  # Build a {d} label with prefix {r.choice(WORDS)[:3].upper()}\n"
            f'  paste0("{r.choice(WORDS)[:3].upper()}-", toupper(trimws(name)), "-{r.randint(100, 999)}")\n}}\n')


def r_loop(r, i, d):
    k = r.randint(2, 5)
    return (f"total_{d}_{i} <- function(limit = {r.randint(5, 40)}) {{\n"
            f"  # Sum every number below limit that divides evenly by {k}\n"
            f"  n <- seq_len(limit) - 1\n"
            f"  sum(n[n %% {k} == 0])\n}}\n")


R_TEMPLATES = [r_calc, r_validate, r_records, r_item, r_filter, r_summary, r_label, r_loop]


def t_text(r, i, d):
    return (f"Entry {i:04d} | {r.choice(WORDS)} | {r.choice(STATUS)} | "
            f"amount {r.randint(10, 9999)} | owner {r.choice(WORDS)}_team\n")




def file_name(folder_name, number, ext=".py"):
    """Folder-based name with a different topic word, e.g. cache_007.py / cache_007.R."""
    topic = TOPICS[(number*7) % len(TOPICS)]
    return f"{topic}_{number:03d}{ext}", topic


def make_content(folder_name, number, size_bytes, ext=".py"):
    """Build a file of exactly size_bytes bytes: valid Python, valid R or plain text."""
    d = clean_name(folder_name).replace("-", "_")
    r = random.Random(f"{d}-{number}")
    topic = file_name(folder_name, number, ext)[1]
    pretty = folder_name.replace("_", " ")
    if ext == ".txt":
        head = f"{topic.capitalize()} notes {number:03d} for {pretty}\n{'=' * 50}\n"
        tail, templates = "", [t_text]
    elif ext in (".R", ".r"):
        head = f"# {topic.capitalize()} script {number:03d} for {pretty}\n\n"
        tail = f'\nif (!interactive()) cat("{d}_{number:03d} loaded\\n")\n'
        templates = R_TEMPLATES
    else:
        head = f'"""Dummy {topic} module {number:03d} for {pretty}."""\n\n'
        tail = f'\nif __name__ == "__main__":\n    print("{d}_{number:03d} loaded")\n'
        templates = TEMPLATES
    sep = "" if ext == ".txt" else "\n"
    parts, size, i = [head], len(head) + len(tail), 1
    while True:
        block = r.choice(templates)(r, i, d) + sep
        if size + len(block) > size_bytes and i > 1: break
        parts.append(block); size += len(block); i += 1
    parts.append(tail)
    code = "".join(parts)
    pad = size_bytes - len(code.encode("utf-8"))
    lines = []
    while pad > 0:
        n = min(pad, 80)
        if n == 1: lines.append("\n")
        elif ext == ".txt": lines.append("".join(r.choices("abcdef0123456789", k=n-1)) + "\n")
        else: lines.append("# " + "".join(r.choices("abcdef0123456789", k=n-3)) + "\n")
        pad -= n
    return code + "".join(lines)


def split_counts(count, exts):
    """Spread count files equally over the file types (extras go to the first types)."""
    base, extra = divmod(count, len(exts))
    return [(e, base + (1 if k < extra else 0)) for k, e in enumerate(exts)]


def create_files(folders, count, kb, exts=(".py",)):
    """Create count files in each folder, spread equally over the types."""
    size = int(kb*1024)
    number = next_number()
    for folder in folders:
        print(f"\n{folder.relative_to(ROOT)}")
        for ext, n in split_counts(count, exts):
            for _ in range(n):
                path = folder/file_name(folder.parent.name, number, ext)[0]
                path.write_bytes(make_content(folder.parent.name, number, size, ext).encode("utf-8"))
                print(f"  Created {path.name} ({path.stat().st_size/1024:.2f} KB)")
                number += 1




# ---------- menu actions ----------
def file_key(path):
    m = FILE_RE.search(path.name)
    return (int(m.group(1)) if m else 10**9, path.name)


def list_files(folder):
    files = managed_files(folder)
    for i, p in enumerate(files, 1): print(f"{i}. {p.name} ({p.stat().st_size/1024:.2f} KB)")
    if not files: print("No Python, R or text files.")
    return files


def select_file(folder):
    files = list_files(folder)
    if not files: return None
    value = input("File number: ").strip()
    return files[int(value)-1] if value.isdigit() and 1 <= int(value) <= len(files) else None


def add_files():
    print("\n--- ADD FILES ---")
    print("Step 1: Choose where to add")
    folders = choose_folders(allow_both=True)
    names = ", ".join(f.name for f in folders)
    print(f"Selected: {names}")
    print("\nStep 2: How many files?")
    label = "per folder " if len(folders) > 1 else ""
    count = ask_number(f"Number of files {label}(e.g. 100): ", int, 1)
    exts = list(ALL_EXTS)   # always spread equally over .py, .R and .txt
    print("  (Files are spread equally over Python, R and text; any extra go to the first types.)")
    print("\nStep 3: File size")
    kb = ask_size_kb()
    start = next_number()
    total = count*len(folders)
    print("\n--- SUMMARY ---")
    n = start
    for f in folders:
        parts = ", ".join(f"{c} x {e}" for e, c in split_counts(count, exts) if c)
        print(f"{f.relative_to(ROOT)}: {parts}  (numbers {n:03d} ... {n+count-1:03d})")
        n += count
    print(f"Total  : {total} files x {kb:g} KB (~{total*kb/1024:.2f} MB)")
    if input("Create these files? (y/n): ").strip().lower() != "y":
        print("Cancelled."); return
    create_files(folders, count, kb, exts)
    print("\nDone.")


def rename_file():
    folder=choose_folder(); old=select_file(folder)
    if not old: return
    m=FILE_RE.search(old.name)
    number=m.group(1) if m else None
    typed=re.sub(r"\.(py|r|txt)$","",input("New name (number and file type are kept automatically, e.g. auditor): ").strip(),flags=re.I)
    word=re.sub(r"_\d+$","",clean_name(typed))
    new=old.with_name(f"{word}_{number}{old.suffix}" if number else f"{word}{old.suffix}")
    if new.exists(): print("Name already exists.")
    else: old.rename(new); print(f"Renamed: {old.name} -> {new.name}")


def delete_file():
    folder=choose_folder(); files=list_files(folder)
    if not files: return
    value=input("File numbers to delete (e.g. 2 or 1,3,5 or 1-4 or all): ").strip().lower()
    picked=set()
    if value=="all": picked=set(range(1,len(files)+1))
    else:
        for part in value.replace(" ","").split(","):
            lo,_,hi=part.partition("-")
            if lo.isdigit() and (not hi or hi.isdigit()):
                picked.update(range(int(lo),int(hi or lo)+1))
    picked={n for n in picked if 1<=n<=len(files)}
    if not picked: print("No valid file numbers."); return
    chosen=[files[n-1] for n in sorted(picked)]
    print("Will delete:", ", ".join(p.name for p in chosen))
    if input(f"Delete {len(chosen)} file(s)? Type YES: ")=="YES":
        for p in chosen: p.unlink()
        print(f"Deleted {len(chosen)} file(s).")
    else: print("Cancelled.")


def read_block():
    """Read typed code until END. Returns a list of lines, or None if cancelled."""
    print("Type your code. Type END on its own line to finish, CANCEL to stop.")
    lines=[]
    while True:
        line=input()
        if line.strip().upper()=="END": return lines
        if line.strip().upper()=="CANCEL": return None
        lines.append(line)


def show_lines(lines, start, end):
    for n in range(start, min(end, len(lines))+1):
        print(f"{n:>5} | {lines[n-1]}")


def ask_line(prompt, low, high):
    while True:
        v=input(prompt).strip()
        if v.isdigit() and low<=int(v)<=high: return int(v)
        print(f"Please enter a number from {low} to {high}.")


def parse_range(text, total):
    """'16' or '16-18' -> (16, 18), or None if invalid."""
    lo,_,hi=text.replace(" ","").partition("-")
    if lo.isdigit() and (not hi or hi.isdigit()):
        x,y=int(lo),int(hi or lo)
        if 1<=x<=y<=total: return x,y
    return None


def modify_file():
    folder=choose_folder(); path=select_file(folder)
    if not path: return
    history=[]       # earlier versions of the file, used by Undo
    redraw=True
    while True:
        lines=path.read_text(encoding="utf-8").split("\n")
        if lines and lines[-1]=="": lines.pop()
        total=len(lines)
        if redraw:
            print(f"\n{path.name} ({total} lines)")
            if total<=60: show_lines(lines,1,total)
            else:
                show_lines(lines,1,40)
                print("   ... only the first 40 lines are shown (use option 4 to see other lines)")
        redraw=True
        print("\nWhat do you want to do?")
        print("  1. Change existing code (replace lines)")
        print("  2. Add new code")
        print("  3. Delete lines")
        print("  4. Show other lines")
        print("  5. Undo last change")
        print("  0. Done")
        c=input("Choose: ").strip()
        if c=="0": return
        if c=="4":
            r=parse_range(input("Show which lines? (e.g. 100-140): "),total)
            if r: show_lines(lines,*r)
            else: print("Invalid line numbers.")
            redraw=False; continue
        if c=="5":
            if not history: print("Nothing to undo."); redraw=False; continue
            path.write_text(history.pop(),encoding="utf-8")
            print("Last change undone."); continue
        if c=="1":
            r=parse_range(input("Which line number do you want to change? (e.g. 16 or 16-18): "),total)
            if not r: print("Invalid line number."); continue
            x,y=r
            print("Current code:"); show_lines(lines,x,y)
            print("Now type the NEW code to put there (type END right away to just remove them).")
            new=read_block()
            if new is None: continue
            lines[x-1:y]=new; msg="Changed"
        elif c=="2":
            v=input("Add after which line number? (press Enter to add at the bottom, 0 = top): ").strip()
            if v=="": x=total
            elif v.isdigit() and 0<=int(v)<=total: x=int(v)
            else: print("Invalid line number."); continue
            new=read_block()
            if new is None: continue
            lines[x:x]=new; msg="Added"
        elif c=="3":
            text=input("Which line(s) do you want to delete? (e.g. 16 or 16-18, or all): ").strip().lower()
            r=(1,total) if text=="all" and total else parse_range(text,total)
            if not r: print("Invalid line number."); continue
            x,y=r
            print("Will delete:"); show_lines(lines,x,min(y,x+19))
            if y>x+19: print(f"   ... and {y-x-19} more line(s)")
            if input(f"Delete {y-x+1} line(s)? (y/n): ").strip().lower()!="y":
                print("Cancelled."); continue
            del lines[x-1:y]; msg="Deleted"
        else: print("Please choose 1, 2, 3, 4, 5 or 0."); continue
        history.append(path.read_text(encoding="utf-8"))
        backup=path.with_name(path.name+".bak"); shutil.copy2(path,backup)
        path.write_text("\n".join(lines)+"\n",encoding="utf-8")
        print(f"{msg} and saved. (Backup: {backup.name}; option 5 undoes it)")


def main():
    create_structure()
    while True:
        print("\n=== ENTERPRISE PROJECT MANAGER ===")
        print("1 Add files")
        print("2 Rename")
        print("3 Delete")
        print("4 Modify")
        print("5 List files")
        print("6 Show folders")
        print("0 Exit")
        option=input("Choose: ").strip()
        try:
            if option=="1": add_files()
            elif option=="2": rename_file()
            elif option=="3": delete_file()
            elif option=="4": modify_file()
            elif option=="5": list_files(choose_folder())
            elif option=="6": show_tree()
            elif option=="0": break
            else: print("Invalid option.")
        except (ValueError,OSError) as e: print("Error:",e)


if __name__=="__main__": main()

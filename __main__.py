import sys
import groq
import pathlib

file_paths = sys.argv[1:]
if not file_paths:
    raise ValueError("At least one file path is required")
entries = []

def read(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

for file_path in file_paths:
    file_content = read(file_path)
    entry = f"{file_path}:\n\n" + "\n".join(
        f"{index}|{line}"
        for index, line in enumerate(file_content.splitlines(), start=1)
    )
    entries.append(entry)

prompt = "\n\n".join(entries) + """\n\nReplace the comment that starts with "x/" with code. Respond in the following format (omit the block of code backticks):

```
script.py:12:15 // Which file the comment is in, what line it begins on and what line it ends at
code that should go as a replacement of the comment
```

Do not annotate your response. Respect the source file's indentation when writing your replacement. When writing line numbers, get them from line number prefixes that are *before* every line (that is, to know a number for a line, look at the number that was *before* the line). The numbers should be inclusive on both ends, so if the first line of the comment is on the line 12 and the last line of the comment is on line 15, you should use 12 and 15 as the line numbers"""

groq_client = groq.Groq(api_key=read(pathlib.Path(__file__).parent/"token.txt").strip())
completion = groq_client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {
            "content": prompt,
            "role": "user"
        }
    ]
)
placement, replacement = completion.choices[0].message.content.split("\n", maxsplit=1)

print(f"Placement: {placement}")
print(f"Replacement:\n{replacement}")
print()
input("Is this fine?")

file_path, start, end = placement.split(":")
start = int(start)
end = int(end)
file_content = read(file_path)
final = []
for line_number, line in enumerate(file_content.split("\n"), start=1):
    if line_number == start:
        final.append(replacement)
    elif start < line_number <= end:
        pass
    else:
        final.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.write("\n".join(final))

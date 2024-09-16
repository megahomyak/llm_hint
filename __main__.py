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
        f"{index} | {line}"
        for index, line in enumerate(file_content.splitlines(), start=1)
    )
    entries.append(entry)

prompt = "\n\n".join(entries) + "\n\nSuggest what to place instead of the comment that starts with \"x/\". The instructions for what you need to do are in the same comment (maybe it spans several lines). Respond only in plain code, no surrounding text (except for explanation comments, if any), no markup, nothing. Just code that can go in place of the comment. Also, immediately before your code response, add one line with the file path and the line number of the comment beginning and end in the format of path/to/file:beginning:end (like main.rs:12:15)"

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
print(replacement)

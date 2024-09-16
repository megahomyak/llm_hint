import sys
import groq
import pathlib
import re

file_paths = sys.argv[1:]
if not file_paths:
    raise ValueError("At least one file path is required")
entries = []

def read(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

for file_path in file_paths:
    file_content = read(file_path)
    entry = "\n".join(
        f"{file_path}:{index}|{line}"
        for index, line in enumerate(file_content.split("\n"), start=1)
    )
    entries.append(entry)

prompt = "\n\n".join(entries) + "\n\nPerfectly recite all the lines with the comment that starts with \"x\" and the comments immediately following it, preserving line prefixes and indentation. After the recital, add lines that resolve the problem from the comment, and only add the lines that will be placed instead of the comment. Do not accidentally add extra lines into your response, only cover the place with comments. Do not commentate your response"

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
replacement = completion.choices[0].message.content

def list_replace(item_number, amount, input_list, replacement_list):
    output_list = input_list.copy()
    index = item_number - 1
    del output_list[index:index+amount]
    for item in replacement_list[::-1]:
        output_list.insert(index, item)
    return output_list

input_lines = []
output_lines = []
file_info = None
input_ended = False
print(replacement)
print()
input("Is this fine?")
print()
for line in replacement.split("\n"):
    match = re.match(r"(.+):(\d+)\|(.+)", line)
    if match:
        if file_info is None:
            file_info = (match.group(1), int(match.group(2)))
        if input_ended:
            output_lines.append(match.group(3))
        else:
            input_lines.append(match.group(3))
    elif input_lines:
        input_ended = True
file_lines = read(file_info[0]).split("\n")
output_lines = list_replace(file_info[1], len(input_lines), file_lines, output_lines)
full_output = "\n".join(output_lines)
with open(file_info[0], "w", encoding="utf-8") as f:
    f.write(full_output)

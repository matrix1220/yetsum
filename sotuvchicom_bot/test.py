import re
match=re.match(r"\A/start (.+)", "/start asd")
print(match.group(1))
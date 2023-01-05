template = """
#custom-vegetable.{idx} {{
	background-image: linear-gradient(
		to right,
		{fg} {idx}%,
		{bg} {idx}.1%
	);
}}
"""
COLOR_FG = "rgba( 42,161,152, 0.8)"
COLOR_BG = "rgba( 42,161,152, 0.2)"
outstr = "/* SHITTY HACK GOES HERE */\n"
for i in range(100):
    outstr += template.format(idx=str(i),fg=COLOR_FG,bg=COLOR_BG)
print(outstr)
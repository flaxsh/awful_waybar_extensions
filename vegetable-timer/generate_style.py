template = """
#custom-vegetable.percentage_{idx} {{
	background-image: linear-gradient(
		to right,
		{fg} {idx}%,
		{bg} {idx}.1%
	);
}}
"""
COLOR_FG = "rgba( 42,161,152, 0.8)"
COLOR_BG = "rgba( 42,161,152, 0.2)"
outstr = """/* 
Put this with your waybar style.css.
Either copy it there and do a @import url("vegetable-timer.css");
or just append it to the style.css
classes for vegetable timer 
*/

/* classes for vegetable-timer module */
#custom-vegetable.alert {
    background: #f53c3c;
}

#custom-vegetable.done {
    background: #2E8B57;
}

/* SHITTY HACK for progress bar goes here */
"""
for i in range(100):
    outstr += template.format(idx=str(i),fg=COLOR_FG,bg=COLOR_BG)
print(outstr)
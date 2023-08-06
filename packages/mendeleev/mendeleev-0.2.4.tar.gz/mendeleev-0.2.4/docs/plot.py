
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html

#output_file("example.html")

x = [1, 2, 3, 4, 5]
y = [6, 7, 6, 4, 5]

p = figure(title="example", plot_width=300, plot_height=300)
p.line(x, y, line_width=2)
p.circle(x, y, size=10, fill_color="white")

html = file_html(p, CDN, "my plot")

with open('plot.html', 'w') as fout:
    fout.write(html)



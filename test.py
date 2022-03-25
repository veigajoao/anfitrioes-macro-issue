from weasyprint import HTML, CSS

y = CSS(string='''
                @page { size: A3; margin: 1cm }
                table {width: 100%}
                td {border: 1px solid;}
                ''')

x = HTML(filename="demo.html")
x.write_pdf('xxx.pdf', stylesheets=[y])

WikiToExcel
-----------


Use is trivial as shown below::

    from wikitoexcel import wikiToExcel
    w2e = wikiToExcel(infile="./wikitbl.txt")
    # print the html representation of wiki markup
    print w2e.getHTML()
    # save excel file to out.xlsx
    w2e.saveExcel(fileName="out.xlsx")

Options are::

    wikiToExcel(wikiContent=<wikistr>, infile=<wikiTextFile>)

Features
--------

wikitoexcel can capture:

- Font styling: bold, underline, strikethrough
- Cell styling: foreground color, background color
- Supports merged cells
- Sheet name is captured as caption of the wiki table
- Multiline cell contents are styled with 'wrap' in excel
- span and div elements are converted to their inner text representation
- HyperLinks are addressed in a way that the hyperlink and display text are presented side by side. This facilitates round-trip between exceltowiki and wikitoexcel. Such as:
  http://yahoo.com Yahoo!

wikitoexcel currently cannot capture anything more complex than the above list. 
Features such as a font styling within a paragraph is not captured.

Notes
-----
If implementing this as a web.py call: 

- You can construct a simple HTML form post with a textarea (below assumes textarea name is 'wikitoexcel')
- Add the following class

.. code-block:: python

    class wikitoexcel():
		def POST(self):
			formdata=web.input()
			w2e=wikiToExcel(wikiContent= formdata['wikitoexcel'])
			sbuf= StringIO.StringIO()
			w2e.saveExcel(fileObj=sbuf)
			web.header('Content-type','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
			return sbuf.getvalue()
Release Notes: 0.1.7
--------------------
Minor update to handling empty cells or with &nbsp;. And some cleanup

Release Notes: 0.1.6
--------------------

Bug found and fixed for creating a worksheet.

Release Notes: 0.1.5
--------------------

Clean up of setup.py and minor changes
			
Release Notes: 0.1.4
--------------------

* Added option to output in inline format using double pipe separator notation vs line by line format.
* Set the package level variable: wikitoexcel.INLINE_FMT=True (default)
* To allow multiline text, a BR tag is replaced for each return character

Release Notes: 0.1.3
--------------------
Added license file
Rewrote parser to retain wikimarkup within cells. This allows an excel user to passthrough wiki markup.


Release Notes: 0.1.2
--------------------
Packaging was not following best practice of examples within the package.

Release Notes: 0.1.1
--------------------
Initial Release

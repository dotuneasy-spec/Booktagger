#set page(width: 6in, height: 9in, margin: 0pt)

#block(width: 100%, height: 100%, clip: true)[
  #image("cover-ayanokoji.png", width: 100%, height: 100%, fit: "cover")
]
#place(bottom + left)[
  #block(
    width: 6in,
    fill: gradient.linear(
      rgb(0, 0, 0, 0%),
      rgb(0, 0, 0, 78%),
      rgb(0, 0, 0, 92%),
      angle: 90deg,
    ),
    inset: (x: 1.15cm, top: 2.4cm, bottom: 1.35cm),
  )[
    #set par(first-line-indent: 0em, justify: false, leading: 0.95em)
    #set text(fill: rgb("#f4efe6"), font: "Liberation Serif")
    #text(size: 11pt, tracking: 3.2pt, fill: rgb("#c9b896"))[A STUDY OF SINGULAR THOUGHT]
    #v(0.55em)
    #text(size: 32pt, weight: "bold")[Thinking as#linebreak()One Being]
    #v(0.45em)
    #text(size: 15pt, weight: "bold", fill: rgb("#e6d7b8"))[The Mind of Ayanokoji]
  ]
]

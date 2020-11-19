import png

r=png.Reader(filename="mr-muscle.png")
width, height, rows, infos = r.read()

b_img = [r for r in rows]
i_img = [list(r) for r in b_img]
rgb_img = []
for r in i_img:
    rgb_img.append([])
    for px in r:
        rgb_img.append(infos["palette"][px])
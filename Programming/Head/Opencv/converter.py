def rgb_to_hsv(r,g,b):
    r,g,b = r/255,b/255,g/255
    print(r,g,b)
    v = max(r,g,b)
    if v == r and g >= b:
        h = 60*((g-b)/(v - min(r,g,b) + 1))
    elif v == r and g < b:
        h = 60*((g-b)/(v - min(r,g,b) +1)) + 360
    elif v == g:
        h = 60*((b - r)/(v - min(r,g,b)+1)) + 120
    elif v == b :
        h = 60*((r-g)/(v - min(r,g,b)+1)) + 240
    if v == 0:
        s = 0
    else:
        s = 1 - (min(r,g,b) / v)
    return [int(h*180/360)%181, int(s*255)%256 , int(v*255)%256]

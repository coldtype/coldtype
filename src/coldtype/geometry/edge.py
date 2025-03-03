from enum import Enum


class Edge(Enum):
    MaxY = 1
    MaxX = 2
    MinY = 3
    MinX = 4
    CenterY = 5
    CenterX = 6

    def PairFromCompass(cmp):
        if isinstance(cmp, Edge):
            return None
        if isinstance(cmp, str):
            cmp = cmp.upper()
        if cmp in ["C", "•"]:
            return (Edge.CenterX, Edge.CenterY)
        elif cmp in ["W", "←"]:
            return (Edge.MinX, Edge.CenterY)
        elif cmp in ["NW", "↖"]:
            return (Edge.MinX, Edge.MaxY)
        elif cmp in ["N", "↑"]:
            return (Edge.CenterX, Edge.MaxY)
        elif cmp in ["NE", "↗"]:
            return (Edge.MaxX, Edge.MaxY)
        elif cmp in ["E", "→"]:
            return (Edge.MaxX, Edge.CenterY)
        elif cmp in ["SE", "↘"]:
            return (Edge.MaxX, Edge.MinY)
        elif cmp in ["S", "↓"]:
            return (Edge.CenterX, Edge.MinY)
        elif cmp in ["SW", "↙"]:
            return (Edge.MinX, Edge.MinY)


def txt_to_edge(txt):
    if isinstance(txt, str):
        txt = txt.lower()
        if txt in ["maxy", "mxy", "n", "⊤", "↑"]:
            return Edge.MaxY
        elif txt in ["maxx", "mxx", "e", "⊣", "→"]:
            return Edge.MaxX
        elif txt in ["miny", "mny", "s", "⊥", "↓"]:
            return Edge.MinY
        elif txt in ["minx", "mnx", "w", "⊢", "←"]:
            return Edge.MinX
        elif txt in ["centery", "cy", "midy", "mdy", "Ｈ"]:
            return Edge.CenterY
        elif txt in ["centerx", "cx", "midx", "mdx", "⌶"]:
            return Edge.CenterX
        else:
            return Edge.PairFromCompass(txt)
    else:
        return txt


def edge_opposite(e):
    if not isinstance(e, Edge):
        return [edge_opposite(_e) for _e in e]
    if e == Edge.MaxY:
        return Edge.MinY
    elif e == Edge.MinY:
        return Edge.MaxY
    elif e == Edge.MaxX:
        return Edge.MinX
    elif e == Edge.MinX:
        return Edge.MaxX
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
        if cmp == "C":
            return (Edge.CenterX, Edge.CenterY)
        elif cmp == "W":
            return (Edge.MinX, Edge.CenterY)
        elif cmp == "NW":
            return (Edge.MinX, Edge.MaxY)
        elif cmp == "N":
            return (Edge.CenterX, Edge.MaxY)
        elif cmp == "NE":
            return (Edge.MaxX, Edge.MaxY)
        elif cmp == "E":
            return (Edge.MaxX, Edge.CenterY)
        elif cmp == "SE":
            return (Edge.MaxX, Edge.MinY)
        elif cmp == "S":
            return (Edge.CenterX, Edge.MinY)
        elif cmp == "SW":
            return (Edge.MinX, Edge.MinY)


def txt_to_edge(txt):
    if isinstance(txt, str):
        txt = txt.lower()
        if txt in ["maxy", "mxy", "n"]:
            return Edge.MaxY
        elif txt in ["maxx", "mxx", "e"]:
            return Edge.MaxX
        elif txt in ["miny", "mny", "s"]:
            return Edge.MinY
        elif txt in ["minx", "mnx", "w"]:
            return Edge.MinX
        elif txt in ["centery", "cy", "midy", "mdy"]:
            return Edge.CenterY
        elif txt in ["centerx", "cx", "midx", "mdx"]:
            return Edge.CenterX
        else:
            return None
    else:
        return txt
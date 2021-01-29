from coldtype import *
import beziers.path
import beziers.point
import glfw
from defcon import Font

# INTERESTING IDEAS BUT A DEAD SCRIPT

ch = "a"

if "__COLDTYPE__" in globals():
    ufo_path = __sibling__("media/test_draw.ufo")

    @renderable(rstate=1, watch_soft=[ufo_path])
    def stub(r, rs):
        if rs.cmd == "rf":
        #if ufo_path not in rs.watch_soft_mods:
            os.system(f"robofont -p {stub.codepath}")

        ufo = Font(str(ufo_path))

        if False:
            return [
                DATPen().glyph(ufo[ch]).f(0).align(r),
                #DATPen().glyph(ufo[ch]).skeleton().s(hsl(0.5, s=1, l=0.3))
            ]

        all_points = [[]]
        for g in rs.input_history.strokes(lambda g: g.action in ["down", "cmd"]):
            if g.action == "cmd":
                if g.position() == glfw.KEY_B:
                    all_points.append([])
                elif g.position() == glfw.KEY_C:
                    try:
                        all_points[-1][-1] = all_points[-1][-1][0:-1]
                        all_points[-1][-1].append(all_points[-1][-1][0].offset(1, 1))
                        #return DATPen().rect(all_points[-1][-1][0].rect(30, 30))
                        all_points.append([])
                    except IndexError:
                        pass
                continue
            if len(g) > 0:
                ps = []
                for p in g:
                    ps.append(p.position)
                all_points[-1].append(ps)
            else:
                #print(g.items)
                pass
        
        for i, points in enumerate(all_points):
            for j, path in enumerate(points):
                for k, pt in enumerate(path):
                    #print(pt.round_to(100))
                    #npt = pt.round_to(100)
                    #print(npt)
                    all_points[i][j][k] = pt.round_to(10)

        dps = DATPenSet()
        for points in all_points:
            out = DATPenSet()
            dp = DATPen()

            for idx, path in enumerate(points):
                if len(path) < 3:
                    for pidx, pt in enumerate(path):
                        if idx == 0 and pidx == 0:
                            dp.moveTo(pt)
                        else:
                            dp.lineTo(pt)
                else:
                    #print(path)
                    try:
                        bpp = beziers.path.BezierPath.fromPoints([beziers.point.Point(p.x, p.y) for p in path], error=1000).smooth().addExtremes()
                        cdp = DATPen.from_cbp([bpp]).s(0).sw(15).f(None)
                        cdp.value = cdp.value[0:-1]
                        mv, mvpts = cdp.value[0]
                        if idx > 0:
                            cdp.value[0] = ("lineTo", mvpts)
                        dp.record(cdp)
                    except IndexError:
                        print(path)
            
            
            #dp = DATPen().f(0).record(out).connect()
            #dp.filter(lambda i, mv, ps: mv not in ["endPath"])
            #dp = out.pen().connect()
            #try:
            #    dp.value[-1] = ("closePath", [])
            #except IndexError:
            #    pass
            dps += dp
            #dps += dp
            #dps += out.pen()
        
        if rs.keylayer == Keylayer.Default:
            return dps.pen().f(0).s(0).sw(5).color_phototype(r, blur=5, cut=150)
        else:
            #print(dps.pen().value[-1])
            #print(len(dps.pen().value))
            if rs.cmd == "save":
                for dp in dps:
                    dp.value.append(("closePath", []))
                #from pprint import pprint
                #pprint(dps.pen().value)
                g = dps.pen().to_glyph()
                ufo.insertGlyph(g, name=ch)
                ufo.save()
                # now the robofont script
            return [
                dps.pen().f(0).s(0).sw(5).color_phototype(r, blur=5, cut=150),
                dps.f(None).s(hsl(0.9, s=1, l=0.8)).sw(3),
                dps.pen().skeleton()
            ]

if __name__ == "__main__":
    cg = CurrentFont()[ch]
    cg.deselect()
    for contour in cg.contours:
        for idx, bp in enumerate(contour.bPoints):
            ix, iy = bp.bcpIn
            ox, oy = bp.bcpOut
            if bp.type == "corner":
                continue
            if abs(ox-ix) > 5 and abs(oy-iy) > 5:
                print(bp.bcpIn, bp.bcpOut)
                bp.selected = True
    
    if True:
        cg.removeSelection(removePoints=True, removeComponents=False, removeAnchors=False, removeImages=False)

        CurrentFont().save()
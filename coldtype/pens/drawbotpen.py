try:
    import drawBot as db
except:
    pass

from drafting.pens.drawbotpen import DrawBotPen as DrawBotPen1

class DrawBotPen(DrawBotPen1):

    #def draw(self, scale=2, style=None):
    #    return super().draw(scale=scale, style=style)

    def Composite1(pens, rect, save_to, paginate=False, scale=2):
        db.newDrawing()
        rect = rect.scale(scale)
        if not paginate:
            db.newPage(rect.w, rect.h)
        for pen in DrawBotPen.FindPens(pens):
            if paginate:
                db.newPage(rect.w, rect.h)
            DrawBotPen(pen, rect).draw(scale=scale)
        db.saveImage(str(save_to))
        db.endDrawing()
    
    def Composite(pens, rect, save_to, scale=2):
        db.newDrawing()
        rect = rect.scale(scale)
        db.newPage(rect.w, rect.h)

        def draw(pen, state, data):
            if state == 0:
                DrawBotPen(pen, rect).draw(scale=scale)
            elif state == -1:
                imgf = pen.data.get("imgf")
                if imgf:
                    im = db.ImageObject()
                    im.lockFocus()
                    db.size(rect.w+300, rect.h+300)
                    db.translate(150, 150)
                    db.scale(scale)
                    pen.data["im"] = im
            elif state == 1:
                imgf = pen.data.get("imgf")
                im = pen.data.get("im")
                if imgf and im:
                    im.unlockFocus()
                    imgf(im)
                    x, y = im.offset()
                    db.translate(-150, -150)
                    db.image(im, (x, y))
        
        if not hasattr(pens, "pens"):
            pens = [pens]
        
        for dps in pens:
            dps.walk(draw)
        
        db.saveImage(str(save_to))
        db.endDrawing()
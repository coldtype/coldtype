from coldtype.pens.misc import BooleanOp, calculate_pathop


class PathopsMixin():
    def _pathop(self, otherPen=None, operation=BooleanOp.XOR):
        if self.val_present():
            self._val.value = calculate_pathop(self, otherPen, operation)
        
        if otherPen is not None or operation == BooleanOp.Simplify:
            for el in self._els:
                el._pathop(otherPen, operation)
        else:
            curr = self._els[0]
            for el in self._els[1:]:
                curr._pathop(el, operation)
            self._els = [curr]

        # if hasattr(self, "pmap"):
        #     return self.pmap(lambda p: p._pathop(otherPen, operation))
        # self.value = calculate_pathop(self, otherPen, operation)
        return self
    
    def difference(self, otherPen=None):
        """Calculate and return the difference of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.Difference)
    
    def union(self, otherPen=None):
        """Calculate and return the union of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.Union)
    
    def xor(self, otherPen=None):
        """Calculate and return the XOR of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.XOR)
    
    def reverseDifference(self, otherPen=None):
        """Calculate and return the reverseDifference of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.ReverseDifference)
    
    def intersection(self, otherPen=None):
        """Calculate and return the intersection of this shape and another."""
        return self._pathop(otherPen=otherPen, operation=BooleanOp.Intersection)
    
    def removeOverlap(self):
        """Remove overlaps within this shape and return itself."""
        return self._pathop(otherPen=None, operation=BooleanOp.Simplify)
    
    remove_overlap = removeOverlap
    ro = removeOverlap
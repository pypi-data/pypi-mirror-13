class T(object):
    def __init__(self, val):
        self.val = val

    def __lt__(self, other):
        return self.val < other.val
    
    def __str__(self):
        return "T({})".format(self.val)
    __repr__ = __str__


if __name__ == "__main__":
    a = T("A")
    b = T("B")
    c = T("C")
    print(a < b)
    l = [a,b,c]
    l.sort()
    print(l)

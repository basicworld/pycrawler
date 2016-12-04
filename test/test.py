class A:
    def __nonzero__(self):
        return True

print bool(A())


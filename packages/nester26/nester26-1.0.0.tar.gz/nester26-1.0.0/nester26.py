def f(l):
    for e in l:
        if(isinstance(e, list)):
            f(e)
        else:
            print(e)

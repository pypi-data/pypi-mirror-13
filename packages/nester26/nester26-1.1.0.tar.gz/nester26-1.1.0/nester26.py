def f(l, lev):
    for e in l:
        if(isinstance(e, list)):
            f(e, lev+1)
        else:
            for t in range(lev):
                print("\t",end='')
            print(e)

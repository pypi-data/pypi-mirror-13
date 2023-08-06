def print_lol(the_list, indy=False, xtra=0):
    for i in the_list:
        if isinstance(i, list):
            print_lol(i, indy, xtra+1)
        else:
            if indy:
                for tab_stop in range(xtra):
                    print ("\t", end="")
            print (i)
            
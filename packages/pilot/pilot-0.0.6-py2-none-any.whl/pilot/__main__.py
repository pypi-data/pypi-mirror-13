import sys

def usage():
    print "Usage:\n    `$ python pilot test`: execute the test suite for pilot"


if len(sys.argv) > 1:
    if sys.argv[1] == 'test':
        import tests
    else:
        usage()

else:
    usage()
import sys
import logging
logging.basicConfig(level = logging.INFO)

log = logging.getLogger('uppermaker')

def main():
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]
    log.info('Hello There, we will take the contents of {}'.format(inputfile))
    log.info('and make them all UPPER CASE!!')
    log.info('Find the result in {}'.format(outputfile))
    with open(inputfile) as inp:
        with open(outputfile,'w') as out:      
            out.write(inp.read().upper())

if __name__ == '__main__':
    main()

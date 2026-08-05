import sys
import nbformat

def main(filename):
    # read notebook from stdin
    nb = nbformat.reads(filename, as_version = 4)

    # prepend a comment to the source of each cell
    for index, cell in enumerate(nb.cells):
        if cell.cell_type == 'code':
            cell.source = "# comment\n" + cell.source

    # write notebook to stdout 
    nbformat.write(nb, sys.stdout)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python my-filter.py <notebook_file>")
        sys.exit(1)
    main(sys.argv[1])
    
    

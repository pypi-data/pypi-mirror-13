from gooey import Gooey, GooeyParser


# @Gooey()
def parse_args(default_name):
    parser = GooeyParser()
    parser.add_argument('data_directory',
                        action='store',
                        default=default_name,
                        widget='DirChooser')
    return parser.parse_args()

if __name__ == '__main__':
    conf = parse_args("/sample")
    print "Done"

from bottle import route, run, template
from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from os import path
import optparse
import sys
import os


TEMPLATE_DIR = path.join(path.dirname(path.realpath(__file__)), "templates")

class BucketList(object):
    def __init__(self, directory):
        self._directory = directory
        
        for filename in os.listdir(directory):
            pass


@route('/')
def list_buckets():
    env = Environment()
    env.loader = FileSystemLoader(TEMPLATE_DIR)
    print(TEMPLATE_DIR)
    tmpl = env.get_template("list_buckets.jinja2")
    
    #handler.send_response(200)
    #handler.send_header('Content-Type', 'application/xml')
    return tmpl.render(buckets=BucketList(path.join(hitchtest.utils.get_hitch_dir(), "s3")))


def main():
    """CLI interface."""
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port", type="int", dest="s3_port", default=10028,
                      help="Specify the port number for the mock S3 server to run on (default: 10028).")
    parser.add_option("-d", "--directory", type="str", dest="directory", default=os.getcwd(),
                      help="Specify the directory to load and save files from.")

    options, _ = parser.parse_args(sys.argv[1:])
    run(host='localhost', port=options.s3_port)


if __name__ == '__main__':
    main()


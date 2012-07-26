
import os
import subprocess


def unix_tail(filename, lines=20):
    if not os.access(filename, os.R_OK):
        raise Exception('Cannot access "%s"' %(filename))
    try:
        args = ['tail', filename, '-n', str(lines)]
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        lines = output.strip().split('\n')
        lines.reverse()
        return lines
    except Exception as e:
        raise Exception('Error performing tail on "%s": %s'
                        %(filename, str(e)))

import subprocess

def beaufort(in_string):
    process = subprocess.Popen(["node", "./beaufort.js", in_string], stdout=subprocess.PIPE)
    return process.communicate()[0].strip().decode("utf-8")

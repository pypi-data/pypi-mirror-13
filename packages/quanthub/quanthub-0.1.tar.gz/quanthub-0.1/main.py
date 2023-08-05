import click
import os
import subprocess
import json
import requests
import commands
import time
# pip install colorama

@click.command()
def hello():
  click.secho('Hello World!', fg='green')
  click.secho('Some more text', bg='blue', fg='white')
  click.secho('ATTENTION', blink=True, bold=True)

def authenticate():
  email = click.prompt('Please enter your email', type=str)
  password = click.prompt('Please enter your password', type=str, hide_input=True)
  r = requests.post("http://localhost:5000/app_login",data=json.dumps({"username":email,"password":password}))
  if "token" in r.json():
    # create a file in ~/.quanthub folder with a file called credentials with the output JSON
    home = os.path.expanduser('~') 
    directory = "{0}/.quanthub".format(home)
    with open('{0}/credentials'.format(directory), 'w') as outfile:
      json.dump(r.json(), outfile)
    click.secho('Successfully Authenticated.', fg='white')
    return r.json()
  else:
    click.secho('There was an error.', fg='white')
    return r.json()

def check_authentication():
  home = os.path.expanduser('~') 
  directory = "{0}/.quanthub".format(home)
  if not os.path.exists(directory):
      os.makedirs(directory)
      click.secho('Creating ~/.quanthub directory', fg='white')
      return authenticate()

  home = os.path.expanduser('~') 
  filename = "{0}/.quanthub/credentials".format(home)
  if not os.path.exists(filename):
      return authenticate()

  return {"status":"OK"}
  #TODO if json file exists but credentials are invalid force authenticate

def dataset_information():
  name = click.prompt('Please enter the dataset name', type=str)
  description = click.prompt('Please enter a small description of the dataset', type=str)
  return {"name":name, "description":description}
  # TODO persist
  # r.table("datasets").create({"name":name,"description":description}).run(conn)
  # requests.post("https://localhost:5000"

def dataset_meta(_file):
  nol = commands.getstatusoutput('wc -l '+_file)[-1].strip().split()[0]
  head = commands.getstatusoutput('head '+_file)[-1]
  tail = commands.getstatusoutput('tail '+_file)[-1]
  size = commands.getstatusoutput('du -sh '+_file)[-1].split("\t")[0].strip()
  ext = _file.split(".")[-1]
  return {"nol": nol, "head":head,"tail":tail, "size":size, "ext":ext}

def dataset_s3upload(_file):
  #cmd = 's3cmd put {0} s3://picobit-quanthub/datasets'.format(_file)
  click.secho('\nUploading Dataset...\n', fg='white')
  cmd = "curl --request PUT -T {0} -# http://s3-us-west-2.amazonaws.com/picobit-quanthub/datasets/ -o output"
  cmd = cmd.format(_file)
  subprocess.call(cmd.split())
  return

def dataset_updatedb():
  print "TODO update db"

@click.command()
@click.argument('arg', nargs=1)
@click.argument('_file', nargs=1)
def cli(arg, _file):
  res = check_authentication()
  if res["status"] != "OK": return


  if arg == "upload":
    # if not authenticated authenticate
    # store json token in file
    #authenticate()
    print dataset_information()
    #TODO validate that same name doesnt exist
    print dataset_meta(_file)
    dataset_s3upload(_file)
    """
    with click.progressbar(range(100)) as bar:
      for i in bar:
        time.sleep(0.1)
    """
  else:   
    click.secho('Invalid Argument', fg='white')

@click.command()
def upload():
  click.echo('Upload File')

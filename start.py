import subprocess
import os
import signal
import sys

def run_flask():
  return subprocess.Popen(['python', 'app.py'])  # Adjust 'app.py' if your Flask file has a different name

def run_react():
  os.chdir('lingolake-frontend')
  return subprocess.Popen(['npm', 'start'])

def main():
  flask_process = run_flask()
  react_process = run_react()

  def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    flask_process.terminate()
    react_process.terminate()
    sys.exit(0)

  signal.signal(signal.SIGINT, signal_handler)
  print('Press Ctrl+C to exit')

  # Wait for processes to complete
  flask_process.wait()
  react_process.wait()

if __name__ == "__main__":
  main()

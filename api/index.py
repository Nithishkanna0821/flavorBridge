import os
import sys

# Ensure root workspace is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app

# Vercel WSGI entrypoint
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

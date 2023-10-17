import os
from app import create_app, db
# from app.models import User

app = create_app('default')
@app.shell_context_processor
def make_shell_context():
    return dict(db=db)

@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

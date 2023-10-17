import db_setup
from entities.User import User

import re

def test_user():
    print("===== TESTING USER ENTITY CREATION =====")
    success = 0
    user = User()
    try:
        user.first_name = "test"
        user.last_name = "user"
        user.email = "test@mail.bark.ca"
        user.password = "Password1234$"
        user.save()
        # user.validate()
        
        success = 1
    except Exception as e:
        print("Something Went Wrong!")
        print(e)
    print(user.to_json())
    if success == 1:
        print("TEST PASSED")
    else:
        print('TEST FAILED')
    print("===== FINISHED USER ENTITY CREATION =====")

    return

def test_regex():
    pattern = "[a-zA-Z \-]+"
    regex = re.compile(pattern)
    res = regex.fullmatch("test")
    print(res)

def test():
    db_setup.db_init()
    test_user()
    db_setup.db_disconnect()
    # test_regex()
    return


test()
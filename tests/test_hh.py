def test_login(app):
    app.login_page.login()

def test_update_resume(app):
    app.resume_page.update_resume()

def test_search_vacancy(app):
    app.search_page.start_search()

def test_update_resume_and_search_vacancy(app):
    test_update_resume(app)
    test_search_vacancy(app)

def test_passing_tests(app):
    app.hh_tests.start_tests()
from devpilot.core.license import validate_license, generate_license

SECRET = "test-secret-formation"

def test_valid_license():
    key = generate_license("student@test.com", 2026, SECRET)
    assert validate_license(key, SECRET) is True

def test_invalid_license():
    assert validate_license("DEVPILOT-FAKEFAKE-2026", SECRET) is False

def test_wrong_format():
    assert validate_license("not-a-license", SECRET) is False

def test_key_structure():
    key = generate_license("joel@test.com", 2026, SECRET)
    parts = key.split("-")
    assert parts[0] == "DEVPILOT"
    assert len(parts[1]) == 8
    assert parts[2] == "2026"

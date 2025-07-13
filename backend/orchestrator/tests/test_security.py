from fastapi import HTTPException
from utils.security import create_access_token, verify_token, require_role

def test_token_verification():
    token = create_access_token("user123", ["create-job"])
    payload = verify_token(token)
    assert payload.user_id == "user123"
    assert "create-job" in payload.roles

def test_role_authorization():
    token = create_access_token("user123", ["view-jobs"])
    
    @require_role("create-job")
    def protected_operation(user):
        return True
    
    try:
        protected_operation(verify_token(token))
        assert False, "Should have raised exception"
    except HTTPException as e:
        assert e.status_code == 403
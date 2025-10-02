from typing import Any, Dict, Optional
import jwt
import json


def normalize_token_string(access_token: Any) -> Optional[str]:
    try:
        if isinstance(access_token, str):
            return access_token
        if isinstance(access_token, dict):
            token_str = access_token.get('access_token') or access_token.get('value')
            if token_str:
                return token_str
            at = access_token.get('accessToken')
            if isinstance(at, dict):
                return at.get('value')
            if isinstance(at, str):
                return at
        return None
    except Exception:
        return None


def extract_member_id_from_access_token(access_token: Any) -> Optional[str]:
    try:
        token_str: Optional[str] = None
        if isinstance(access_token, str):
            token_str = access_token
        elif isinstance(access_token, dict):
            token_str = access_token.get('access_token') or access_token.get('value')
            if not token_str:
                at = access_token.get('accessToken')
                if isinstance(at, dict):
                    token_str = at.get('value')
                elif isinstance(at, str):
                    token_str = at
        if not token_str:
            return None

        if token_str.startswith('OauthNG.JWS.'):
            jwt_part = token_str[12:]
            data = jwt.decode(jwt_part, options={"verify_signature": False, "verify_aud": False})
        else:
            data = jwt.decode(token_str, options={"verify_signature": False, "verify_aud": False})

        data_payload = data.get('data')
        if isinstance(data_payload, str):
            try:
                data_payload = json.loads(data_payload)
            except Exception:
                pass

        if isinstance(data_payload, dict):
            instance = data_payload.get('instance', {})
            if isinstance(instance, dict):
                site_member_id = instance.get('siteMemberId')
                if isinstance(site_member_id, str) and site_member_id:
                    return site_member_id
            for key in ['memberId', 'sub', 'authorizedSubject', 'id', 'siteMemberId']:
                val = data_payload.get(key)
                if isinstance(val, str) and val:
                    return val
            member = data_payload.get('member') or {}
            if isinstance(member, dict):
                val = member.get('id')
                if isinstance(val, str) and val:
                    return val

        for key in ['memberId', 'sub', 'authorizedSubject']:
            val = data.get(key)
            if isinstance(val, str) and val:
                return val
        member = data.get('member') or {}
        if isinstance(member, dict):
            val = member.get('id')
            if isinstance(val, str) and val:
                return val
        return None
    except Exception:
        return None


def decode_wix_token(access_token: str) -> Dict[str, Any]:
    token_str = str(access_token)
    if token_str.startswith('OauthNG.JWS.'):
        jwt_part = token_str[12:]
        return jwt.decode(jwt_part, options={"verify_signature": False, "verify_aud": False})
    return jwt.decode(token_str, options={"verify_signature": False, "verify_aud": False})


def extract_meta_from_token(access_token: str) -> Dict[str, Optional[str]]:
    try:
        payload = decode_wix_token(access_token)
        data_payload = payload.get('data', {})
        if isinstance(data_payload, str):
            try:
                data_payload = json.loads(data_payload)
            except Exception:
                pass
        instance = (data_payload or {}).get('instance', {})
        return {
            'siteMemberId': instance.get('siteMemberId'),
            'metaSiteId': instance.get('metaSiteId'),
            'permissions': instance.get('permissions'),
        }
    except Exception:
        return {'siteMemberId': None, 'metaSiteId': None, 'permissions': None}



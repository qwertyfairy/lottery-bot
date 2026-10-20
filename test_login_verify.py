# 로그인 미인증 상태가 "미당첨"이 아닌 실패로 올라가는지 확인: python test_login_verify.py
from unittest import mock
import requests
import auth, lotto645, win720


def _http_401(*_a, **_k):
    res = requests.Response()
    res.status_code = 401
    raise requests.HTTPError("401", response=res)


def test_verify_raises_permission_error_on_401():
    ctrl = auth.AuthController()
    with mock.patch.object(ctrl.http_client, "get", side_effect=_http_401):
        try:
            ctrl._verify_logged_in()
        except PermissionError:
            return
    raise AssertionError("401인데 PermissionError가 나지 않음")


def test_check_winning_propagates_instead_of_no_win():
    ctrl = auth.AuthController()
    for checker in (lotto645.Lotto645(), win720.Win720()):
        with mock.patch.object(checker.http_client, "get", side_effect=_http_401):
            try:
                checker.check_winning(ctrl)
            except requests.RequestException:
                continue
        raise AssertionError(f"{type(checker).__name__}: 조회 실패가 미당첨으로 삼켜짐")


if __name__ == "__main__":
    test_verify_raises_permission_error_on_401()
    test_check_winning_propagates_instead_of_no_win()
    # 실제 사이트: 로그인 없는 새 세션은 미인증으로 판정돼야 함
    try:
        auth.AuthController()._verify_logged_in()
        raise AssertionError("미로그인 세션이 인증된 것으로 판정됨")
    except PermissionError:
        pass
    print("ok")

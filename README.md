# 소개
동행복권 계정에 예치금을 넣어두면, 로또 645와 연금복권 720+를 자동 구매하고 당첨 여부를 확인해 디스코드로 알려주는 프로젝트입니다.

![check](./.github/images/check.png)

# 디스코드 기반으로 시작하기
## 1) 디스코드 웹훅 만들기
1. 알림을 받을 디스코드 채널을 엽니다.
2. `채널 편집` -> `Integrations` -> `Webhooks`로 이동합니다.
3. 새 웹훅을 생성하고 URL을 복사합니다.

## 2) 환경 변수 설정
1. `.env.sample`을 복사해서 `.env`를 만듭니다.
2. 아래 값을 채웁니다.

```env
USERNAME=동행복권아이디
PASSWORD=동행복권비밀번호
COUNT=5
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

USERNAME_KYU=추가계정아이디
PASSWORD_KYU=추가계정비밀번호
COUNT_KYU=5
DISCORD_WEBHOOK_URL_KYU=https://discord.com/api/webhooks/...
```

- `COUNT`는 로또 자동 구매 게임 수입니다. (`1`~`5`)
- `COUNT_KYU`는 `규람쥐❤️` 계정의 로또 자동 구매 게임 수입니다. (`1`~`5`)
- 디스코드만 쓸 경우 `SLACK_WEBHOOK_URL`은 비워두세요.
- `USERNAME_KYU`와 `PASSWORD_KYU`를 넣으면 `규람쥐❤️` 계정도 같은 스케줄에 함께 구매/당첨확인을 진행합니다.
- 디스코드 알림에는 `하람쥐💛`, `규람쥐❤️` 문구가 앞에 붙어 계정이 구분됩니다.

## 3) 로컬에서 먼저 테스트
```bash
pip3 install -r requirements.txt
make buy
make check
```

필요하면 개별 실행도 가능합니다.
```bash
make buy_lotto
make buy_win720
make check_lotto
make check_win720
```

## 4) GitHub Actions로 자동 실행
1. 레포지토리를 `fork`합니다.
2. `Settings` -> `Secrets and variables` -> `Actions`로 이동합니다.
3. 아래 시크릿을 추가합니다.
   - `USERNAME`
   - `PASSWORD`
   - `COUNT`
   - `DISCORD_WEBHOOK_URL`
   - `USERNAME_KYU`
   - `PASSWORD_KYU`
   - `COUNT_KYU`
   - `DISCORD_WEBHOOK_URL_KYU`

기본 스케줄:
- 구매: 매주 월요일 KST 19:00
- 당첨 확인: 매주 토요일 KST 22:00

워크플로우 파일:
- `.github/workflows/buy_lotto.yml`
- `.github/workflows/check_winning.yml`

# 문제 해결
- 알림이 안 오면 `DISCORD_WEBHOOK_URL`이 정확한지 확인하세요.
- 구매 실패 시 동행복권 계정 잔액과 로그인 정보를 먼저 확인하세요.
- Actions에서 실행 실패 시 로그에서 환경변수 누락 여부를 확인하세요.

# Reference
- https://github.com/roeniss/dhlottery-api

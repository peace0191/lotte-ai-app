# ⚙️ Lotte AI Sales App - 상세 설정 가이드

이 문서는 앱의 핵심 기능(문자 발송, 유튜브 업로드, 카카오 공유 등)을 활성화하기 위한 API 키 발급 및 설정 방법을 안내합니다.

설정 파일 위치: `.streamlit/secrets.toml`

---

## 1. 📱 문자 발송 (Solapi/CoolSMS)
로그인 인증번호(OTP) 발송을 위해 필요합니다.

1. **[Solapi 홈페이지](https://solapi.com/)** 접속 및 회원가입/로그인 via CoolSMS
2. **발신번호 등록**: [발신번호 관리] 메뉴에서 본인 휴대폰 번호를 등록해주세요. (필수)
3. **API Key 발급**:
   - [개발/연동] -> [API Key 관리] -> [새 권한 생성/추가]
   - 생성된 `API Key`와 `API Secret`을 복사합니다.
4. **설정 파일 입력**:
   ```toml
   [solapi]
   api_key = "여기에_API_Key_복사"
   api_secret = "여기에_API_Secret_복사"
   sender_phone = "01012345678"  # 등록된 발신번호 (하이픈 없이 숫자만)
   ```

---

## 2. 💬 카카오톡 공유 (Kakao Developers)
매물 카드 공유 버튼을 활성화합니다.

1. **[Kakao Developers](https://developers.kakao.com/)** 접속 및 로그인
2. **내 애플리케이션** -> [애플리케이션 추가하기]
3. **요약 정보**에서 **`JavaScript 키`**를 복사합니다.
4. **플랫폼 설정**:
   - [플랫폼] -> [Web 플랫폼 등록]
   - 사이트 도메인에 `http://localhost:8501` (로컬 테스트용) 및 실제 배포 도메인(예: `http://3.12.34.56:8501`)을 반드시 추가해야 동작합니다.
5. **설정 파일 입력**:
   ```toml
   [kakao]
   js_key = "여기에_JavaScript_키_복사"
   ```

---

## 3. 📹 유튜브 업로드 (Google Cloud Console)
관리자 권한으로 앱에서 유튜브 채널에 영상을 자동 업로드합니다.

1. **[Google Cloud Console](https://console.cloud.google.com/)** 접속
2. 새 프로젝트 생성 (예: `Lotte-RealEstate-Uploader`)
3. **API 및 서비스** -> [API 라이브러리] -> `YouTube Data API v3` 검색 및 **사용(Enable)** 클릭
4. **OAuth 동의 화면** 설정:
   - User Type: `외부(External)` 선택
   - 앱 이름, 이메일 등 필수 정보 입력
   - **범위(Scope) 추가**: `.../auth/youtube.upload` 선택 및 저장
   - **테스트 사용자**: 본인의 구글 계정(유튜브 채널 계정) 이메일 추가
5. **사용자 인증 정보(Credentials)** 생성:
   - [사용자 인증 정보 만들기] -> **OAuth 클라이언트 ID**
   - 애플리케이션 유형: **데스크톱 앱** (또는 웹 애플리케이션)
   - 생성 완료 후 **`JSON 다운로드`** 클릭
6. **파일 저장**:
   - 다운로드한 JSON 파일 이름을 `youtube_client_secret.json`으로 변경
   - 프로젝트 폴더 내 `assets/system/keys/` 위치에 저장
   - 경로: `assets/system/keys/youtube_client_secret.json`

---

## 4. 🔐 보안 및 관리자 설정
앱 운영을 위한 보안 키와 관리자 번호를 설정합니다.

1. **OTP 보안 키 (Pepper)**:
   - 비밀번호 보안 강화를 위한 임의의 문자열입니다. 아무 긴 문자열이나 입력하세요.
2. **관리자 번호 (Admin Phones)**:
   - 이 번호로 로그인하면 자동으로 **관리자 권한**이 부여됩니다.
   - 여러 명일 경우 쉼표(`,`)로 구분합니다.

```toml
[auth]
admin_phones = "010-1234-5678, 010-9876-5432"
otp_pepper = "random_string_x9d8f7..."
```

---

### ✅ 설정 완료 후
모든 키를 입력했다면 앱을 다시 실행하세요.
```bash
streamlit run app.py
```
로그인 페이지에서 휴대폰 번호를 입력하면 문자가 발송되고, 유튜브 업로드 메뉴가 활성화됩니다.

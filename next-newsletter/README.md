# Next 뉴스레터

새 뉴스레터 화면과 Supabase 연동을 위한 Next.js 프로젝트입니다.

## 실행

```bash
npm install
npm run dev
```

기본 개발 주소:

```text
http://localhost:3000
```

## 환경 변수

`.env.example`을 참고해 `.env.local`을 만듭니다.

```text
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

## DB 스키마

Supabase SQL Editor에서 `supabase/schema.sql`을 실행하면 기본 테이블을 만들 수 있습니다.

현재 스키마는 다음 기능을 기준으로 작성했습니다.

- 단순 사용자 식별
- 최근 수집 기록
- 수집 기록별 기사 목록
- 로그인 사용자 스크랩
- 스크랩 시점의 기사 목록 복사 저장


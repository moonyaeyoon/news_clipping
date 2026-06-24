const recentHistory = [
  "2026.06.24 뉴스 수집",
  "2026.06.23 뉴스 수집",
  "2026.06.22 뉴스 수집",
];

export default function Home() {
  return (
    <main className="shell">
      <header className="topbar">
        <strong className="brand">빗썸 biz</strong>
        <span className="title">뉴스레터</span>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <section>
            <h2>최근 기록</h2>
            <ul>
              {recentHistory.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>

          <section>
            <h2>스크랩</h2>
            <p>로그인 후 저장한 스크랩이 표시됩니다.</p>
          </section>
        </aside>

        <section className="content">
          <div className="panel">
            <h1>Next.js 전환 준비 완료</h1>
            <p>
              새 Figma 화면을 기준으로 이 영역에 검색 조건, 기사 목록, 선택 기사
              정렬, 파일 다운로드, 이메일 템플릿 미리보기를 구현할 예정입니다.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}


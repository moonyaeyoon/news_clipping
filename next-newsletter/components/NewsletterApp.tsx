"use client";

import { useEffect, useMemo, useState } from "react";
import type { NewsArticle } from "@/lib/news";
import type { NewsletterTemplate } from "@/lib/templates";

type HistoryItem = {
  id: string;
  start_date: string | null;
  end_date: string | null;
  article_count: number;
  created_at: string;
};

type NewsSearchResponse = {
  ok: boolean;
  historyId?: string;
  query?: string;
  articles?: NewsArticle[];
  message?: string;
};

type HistoryResponse = {
  ok: boolean;
  histories?: HistoryItem[];
  message?: string;
};

type HtmlResponse = {
  ok: boolean;
  html?: string;
  message?: string;
};

const BIZ_LOGO_URL =
  "https://res.cloudinary.com/dys1jifiy/image/upload/v1781742425/1-2_hg0esz.png";

const templateOptions: Array<{
  value: NewsletterTemplate;
  label: string;
}> = [
  {
    value: "orange-card",
    label: "오렌지 카드",
  },
  {
    value: "blue-basic",
    label: "블루 기본",
  },
];

export function NewsletterApp() {
  const today = new Date().toISOString().slice(0, 10);
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 10);
  const [startDate, setStartDate] = useState(sevenDaysAgo);
  const [endDate, setEndDate] = useState(today);
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [orderedArticles, setOrderedArticles] = useState<NewsArticle[]>([]);
  const [histories, setHistories] = useState<HistoryItem[]>([]);
  const [template, setTemplate] = useState<NewsletterTemplate>("orange-card");
  const [html, setHtml] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");
  const [draggedId, setDraggedId] = useState<string | null>(null);

  const allSelected = articles.length > 0 && selectedIds.size === articles.length;

  const selectedArticles = useMemo(
    () => articles.filter((article) => selectedIds.has(article.id)),
    [articles, selectedIds],
  );

  useEffect(() => {
    loadHistories();
  }, []);

  async function loadHistories() {
    const response = await fetch("/api/history", {
      cache: "no-store",
    });
    const data = (await response.json()) as HistoryResponse;

    if (data.ok) {
      setHistories(data.histories ?? []);
    }
  }

  async function handleSearch() {
    setIsLoading(true);
    setError("");
    setHtml("");

    try {
      const response = await fetch("/api/news/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          startDate,
          endDate,
        }),
      });
      const data = (await response.json()) as NewsSearchResponse;

      if (!data.ok) {
        throw new Error(data.message ?? "뉴스 수집에 실패했습니다.");
      }

      const nextArticles = data.articles ?? [];
      setArticles(nextArticles);
      setSelectedIds(new Set(nextArticles.map((article) => article.id)));
      setOrderedArticles(nextArticles);
      await loadHistories();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "뉴스 수집에 실패했습니다.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  function handleToggleAll() {
    if (allSelected) {
      setSelectedIds(new Set());
      setOrderedArticles([]);
      return;
    }

    setSelectedIds(new Set(articles.map((article) => article.id)));
    setOrderedArticles(articles);
  }

  function handleToggleArticle(article: NewsArticle) {
    const nextSelectedIds = new Set(selectedIds);

    if (nextSelectedIds.has(article.id)) {
      nextSelectedIds.delete(article.id);
    } else {
      nextSelectedIds.add(article.id);
    }

    setSelectedIds(nextSelectedIds);
  }

  function handleApplySelected() {
    setOrderedArticles(selectedArticles);
    setHtml("");
  }

  function handleRemoveSelected(articleId: string) {
    const nextSelectedIds = new Set(selectedIds);
    nextSelectedIds.delete(articleId);
    setSelectedIds(nextSelectedIds);
    setOrderedArticles((current) =>
      current.filter((article) => article.id !== articleId),
    );
  }

  function handleDrop(targetId: string) {
    if (!draggedId || draggedId === targetId) {
      setDraggedId(null);
      return;
    }

    const current = [...orderedArticles];
    const fromIndex = current.findIndex((article) => article.id === draggedId);
    const toIndex = current.findIndex((article) => article.id === targetId);

    if (fromIndex === -1 || toIndex === -1) {
      setDraggedId(null);
      return;
    }

    const [moved] = current.splice(fromIndex, 1);
    current.splice(toIndex, 0, moved);
    setOrderedArticles(current);
    setHtml("");
    setDraggedId(null);
  }

  async function handleGenerateHtml() {
    setIsGenerating(true);
    setError("");

    try {
      const response = await fetch("/api/templates/html", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          template,
          articles: orderedArticles,
        }),
      });
      const data = (await response.json()) as HtmlResponse;

      if (!data.ok || !data.html) {
        throw new Error(data.message ?? "HTML 생성에 실패했습니다.");
      }

      setHtml(data.html);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "HTML 생성에 실패했습니다.",
      );
    } finally {
      setIsGenerating(false);
    }
  }

  function handleDownloadHtml() {
    if (!html) {
      return;
    }

    const blob = new Blob([html], {
      type: "text/html;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${today}_daily_news_email.html`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function handleCopyHtml() {
    if (!html) {
      return;
    }

    await navigator.clipboard.writeText(html);
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <img src={BIZ_LOGO_URL} alt="빗썸 biz" className="brand-logo" />
        <h1>뉴스레터</h1>
      </header>

      <div className="app-layout">
        <aside className="app-sidebar">
          <details open>
            <summary>최근 기록</summary>
            <ul className="history-list">
              {histories.length ? (
                histories.map((history) => (
                  <li key={history.id}>
                    <strong>{formatHistoryDate(history.created_at)}</strong>
                    <span>{history.article_count}건 수집</span>
                  </li>
                ))
              ) : (
                <li className="empty-list">최근 기록이 없습니다.</li>
              )}
            </ul>
          </details>
          <details>
            <summary>스크랩</summary>
            <p className="sidebar-note">로그인 기능 추가 후 사용할 수 있습니다.</p>
          </details>
        </aside>

        <section className="workspace">
          <section className="search-section">
            <button className="section-title" type="button">
              <span aria-hidden>›</span>
              현재 검색 조건
            </button>

            <div className="date-controls">
              <label>
                <span>From</span>
                <input
                  type="date"
                  value={startDate}
                  onChange={(event) => setStartDate(event.target.value)}
                />
              </label>
              <label>
                <span>To</span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(event) => setEndDate(event.target.value)}
                />
              </label>
              <button className="primary-button" type="button" onClick={handleSearch}>
                {isLoading ? "수집 중" : "RUN"}
              </button>
            </div>

            {error && <p className="error-message">{error}</p>}

            <div className="table-toolbar">
              <button
                type="button"
                className="select-toggle"
                onClick={handleToggleAll}
                disabled={!articles.length}
              >
                {allSelected ? "전체 해제" : "전체 선택"}
              </button>
              <span>{articles.length ? `${articles.length}건` : "수집 전"}</span>
            </div>

            <div className="news-table" role="table">
              <div className="news-row news-head" role="row">
                <span />
                <span>날짜</span>
                <span>제목</span>
                <span>출처</span>
                <span>링크</span>
              </div>
              {articles.map((article) => (
                <div className="news-row" role="row" key={article.id}>
                  <label className="check-cell">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(article.id)}
                      onChange={() => handleToggleArticle(article)}
                    />
                  </label>
                  <span>{article.date}</span>
                  <span className="article-title-cell">{article.title}</span>
                  <span>{article.source}</span>
                  <a href={article.link} target="_blank" rel="noreferrer">
                    열기
                  </a>
                </div>
              ))}
            </div>

            <button
              className="primary-button apply-button"
              type="button"
              onClick={handleApplySelected}
              disabled={!selectedIds.size}
            >
              적용
            </button>
          </section>

          <section className="selection-section">
            <div className="sortable-list">
              {orderedArticles.map((article) => (
                <article
                  className="sort-item"
                  draggable
                  key={article.id}
                  onDragStart={() => setDraggedId(article.id)}
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={() => handleDrop(article.id)}
                >
                  <span className="drag-handle" aria-hidden>
                    ⠿
                  </span>
                  <div>
                    <div className="sort-meta">
                      <span>{article.source}</span>
                      <span>{article.date}</span>
                    </div>
                    <strong>{article.title}</strong>
                  </div>
                  <button
                    type="button"
                    className="icon-button"
                    onClick={() => handleRemoveSelected(article.id)}
                    aria-label="선택 기사 삭제"
                  >
                    ⌫
                  </button>
                </article>
              ))}
            </div>
            <p className="selection-count">개수 : {orderedArticles.length}건</p>
          </section>

          <section className="actions-section">
            <label>
              <span>파일 다운로드</span>
              <select disabled>
                <option>HTML</option>
              </select>
            </label>
            <label>
              <span>이메일 템플릿 만들기</span>
              <select
                value={template}
                onChange={(event) =>
                  setTemplate(event.target.value as NewsletterTemplate)
                }
              >
                {templateOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <button
              className="primary-button"
              type="button"
              onClick={handleGenerateHtml}
              disabled={!orderedArticles.length || isGenerating}
            >
              {isGenerating ? "생성 중" : "HTML 생성"}
            </button>
          </section>

          <section className="template-section">
            <div className="code-panel">
              <div className="panel-header">
                <strong>Code Block</strong>
                <button type="button" onClick={handleCopyHtml} disabled={!html}>
                  복사
                </button>
              </div>
              <pre>{html || "HTML 생성 후 코드가 여기에 표시됩니다."}</pre>
            </div>

            <div className="preview-panel">
              <div className="panel-header">
                <strong>Preview</strong>
                <button type="button" onClick={handleDownloadHtml} disabled={!html}>
                  다운로드
                </button>
              </div>
              {html ? (
                <iframe title="email html preview" srcDoc={html} />
              ) : (
                <div className="preview-empty" />
              )}
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}

function formatHistoryDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(
    date.getMinutes(),
  ).padStart(2, "0")}`;
}


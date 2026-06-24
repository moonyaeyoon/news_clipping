"use client";

import { useEffect, useMemo, useState } from "react";
import { DayPicker } from "react-day-picker";
import { ko } from "date-fns/locale";
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
const DEFAULT_QUERY = `(디지털자산 OR 가상자산 OR 코인)
AND
(기업 OR 기관 OR 법인)`;

const templateOptions: Array<{
  value: NewsletterTemplate;
  label: string;
}> = [
  {
    value: "default",
    label: "블루 기본",
  },
  {
    value: "large",
    label: "블루 큰 사이즈",
  },
  {
    value: "orange",
    label: "오렌지 기본",
  },
  {
    value: "orange_no_sidebar",
    label: "오렌지 템플릿 (사이드바 X)",
  },
  {
    value: "orange_card",
    label: "오렌지 카드",
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
  const [template, setTemplate] = useState<NewsletterTemplate>("default");
  const [html, setHtml] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [openDatePicker, setOpenDatePicker] = useState<"start" | "end" | null>(
    null,
  );
  const [hasSearched, setHasSearched] = useState(false);

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
      setSelectedIds(new Set());
      setOrderedArticles([]);
      setHasSearched(true);
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

  function handleToggleAll(checked = !allSelected) {
    if (allSelected) {
      setSelectedIds(new Set());
      setOrderedArticles([]);
      return;
    }

    if (checked) {
      setSelectedIds(new Set(articles.map((article) => article.id)));
      return;
    }

    setSelectedIds(new Set());
    setOrderedArticles([]);
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
            <details className="query-details">
              <summary>설정된 검색 조건 보기</summary>
              <pre>{DEFAULT_QUERY}</pre>
            </details>

            <div className="date-controls">
              <DateField
                label="From"
                value={startDate}
                isOpen={openDatePicker === "start"}
                onOpen={() => setOpenDatePicker("start")}
                onClose={() => setOpenDatePicker(null)}
                onChange={setStartDate}
              />
              <DateField
                label="To"
                value={endDate}
                isOpen={openDatePicker === "end"}
                onOpen={() => setOpenDatePicker("end")}
                onClose={() => setOpenDatePicker(null)}
                onChange={setEndDate}
              />
              <button className="primary-button" type="button" onClick={handleSearch}>
                {isLoading ? "수집 중" : "RUN"}
              </button>
            </div>

            {error && <p className="error-message">{error}</p>}

            {hasSearched && (
              <>
                <div className="table-toolbar">
                  <span>{articles.length}건</span>
                </div>

                <div className="news-table" role="table">
                  <div className="news-row news-head" role="row">
                    <label className="check-cell">
                      <input
                        type="checkbox"
                        checked={allSelected}
                        disabled={!articles.length}
                        onChange={(event) => handleToggleAll(event.target.checked)}
                        aria-label="전체 기사 선택"
                      />
                    </label>
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
              </>
            )}
          </section>

          {hasSearched && (
            <>
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
                      <div className="sort-content">
                        <div className="sort-copy">
                          <span>{article.source}</span>
                          <strong>{article.title}</strong>
                        </div>
                        <span className="sort-date">{article.date}</span>
                      </div>
                      <button
                        type="button"
                        className="icon-button"
                        onClick={() => handleRemoveSelected(article.id)}
                        aria-label="선택 기사 삭제"
                      >
                        <TrashIcon />
                      </button>
                    </article>
                  ))}
                </div>
                <p className="selection-count">개수 : {orderedArticles.length}건</p>
              </section>

              <section className="actions-section">
                <label className="select-field">
                  <span>파일 다운로드</span>
                  <select disabled>
                    <option>HTML</option>
                  </select>
                </label>
                <label className="select-field">
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
            </>
          )}
        </section>
      </div>
    </main>
  );
}

function DateField({
  label,
  value,
  isOpen,
  onOpen,
  onClose,
  onChange,
}: {
  label: string;
  value: string;
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
  onChange: (value: string) => void;
}) {
  const selectedDate = parseDate(value);

  return (
    <label className="date-field">
      <span>{label}</span>
      <button className="date-trigger" type="button" onClick={isOpen ? onClose : onOpen}>
        <CalendarIcon />
        <span>{formatDisplayDate(value)}</span>
        <span className="date-clear" aria-hidden>
          ×
        </span>
      </button>
      {isOpen && (
        <div className="calendar-popover">
          <DayPicker
            mode="single"
            selected={selectedDate}
            defaultMonth={selectedDate}
            locale={ko}
            onSelect={(date) => {
              if (!date) {
                return;
              }

              onChange(toDateInputValue(date));
              onClose();
            }}
          />
        </div>
      )}
    </label>
  );
}

function parseDate(value: string) {
  const [year, month, day] = value.split("-").map(Number);

  if (!year || !month || !day) {
    return undefined;
  }

  return new Date(year, month - 1, day);
}

function toDateInputValue(date: Date) {
  return [
    date.getFullYear(),
    String(date.getMonth() + 1).padStart(2, "0"),
    String(date.getDate()).padStart(2, "0"),
  ].join("-");
}

function formatDisplayDate(value: string) {
  const date = parseDate(value);

  if (!date) {
    return value;
  }

  return `${String(date.getMonth() + 1).padStart(2, "0")}/${String(
    date.getDate(),
  ).padStart(2, "0")}/${date.getFullYear()}`;
}

function CalendarIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
      <path
        d="M5.333 1.333V4M10.667 1.333V4M2.667 6.667H13.333M4 2.667H12C12.736 2.667 13.333 3.264 13.333 4V12C13.333 12.736 12.736 13.333 12 13.333H4C3.264 13.333 2.667 12.736 2.667 12V4C2.667 3.264 3.264 2.667 4 2.667Z"
        stroke="#9CA3AF"
        strokeWidth="1.3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
      <path d="M2 4H14" stroke="#4A5565" strokeWidth="1.33333" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12.6668 4V13.3333C12.6668 14 12.0002 14.6667 11.3335 14.6667H4.66683C4.00016 14.6667 3.3335 14 3.3335 13.3333V4" stroke="#4A5565" strokeWidth="1.33333" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5.3335 3.99998V2.66665C5.3335 1.99998 6.00016 1.33331 6.66683 1.33331H9.3335C10.0002 1.33331 10.6668 1.99998 10.6668 2.66665V3.99998" stroke="#4A5565" strokeWidth="1.33333" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M6.6665 7.33331V11.3333" stroke="#4A5565" strokeWidth="1.33333" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M9.3335 7.33331V11.3333" stroke="#4A5565" strokeWidth="1.33333" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
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

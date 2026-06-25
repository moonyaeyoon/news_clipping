"use client";

import { useEffect, useMemo, useRef, useState } from "react";
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

type HistoryDetailResponse = {
  ok: boolean;
  history?: HistoryItem;
  articles?: NewsArticle[];
  message?: string;
};

type ResolveArticlesResponse = {
  ok: boolean;
  articles?: NewsArticle[];
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
  {
    value: "blue_card",
    label: "블루 카드",
  },
];
const fileOptions = [
  {
    value: "excel",
    label: "Excel",
  },
  {
    value: "word",
    label: "Word",
  },
  {
    value: "pdf",
    label: "PDF",
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
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null);
  const [fileType, setFileType] = useState("excel");
  const [openMenu, setOpenMenu] = useState<"file" | "template" | null>(null);
  const [hasAppliedSelection, setHasAppliedSelection] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const exportSheetRef = useRef<HTMLDivElement>(null);

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
    setActiveHistoryId(null);
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
      setHasAppliedSelection(false);
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

  async function handleLoadHistory(history: HistoryItem) {
    setIsLoading(true);
    setError("");
    setHtml("");

    try {
      const response = await fetch(`/api/history/${history.id}`, {
        cache: "no-store",
      });
      const data = (await response.json()) as HistoryDetailResponse;

      if (!data.ok) {
        throw new Error(data.message ?? "최근 기록을 불러오지 못했습니다.");
      }

      setStartDate(history.start_date ?? "");
      setEndDate(history.end_date ?? "");
      setArticles(data.articles ?? []);
      setSelectedIds(new Set());
      setOrderedArticles([]);
      setHasAppliedSelection(false);
      setActiveHistoryId(history.id);
      setHasSearched(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "최근 기록을 불러오지 못했습니다.",
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
    setHasAppliedSelection(true);
  }

  function handleReset() {
    setArticles([]);
    setSelectedIds(new Set());
    setOrderedArticles([]);
    setHtml("");
    setHasSearched(false);
    setHasAppliedSelection(false);
    setActiveHistoryId(null);
    setOpenDatePicker(null);
    setOpenMenu(null);
  }

  function handleRemoveSelected(articleId: string) {
    const nextSelectedIds = new Set(selectedIds);
    nextSelectedIds.delete(articleId);
    setSelectedIds(nextSelectedIds);
    setOrderedArticles((current) =>
      current.filter((article) => article.id !== articleId),
    );
    setHtml("");
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

  async function handleSaveFile() {
    if (!orderedArticles.length) {
      return;
    }

    try {
      setError("");
      const exportArticles = await resolveArticlesForExport(orderedArticles);
      setOrderedArticles(exportArticles);

      if (fileType === "excel") {
        const XLSX = await import("xlsx");
        const worksheet = XLSX.utils.json_to_sheet(
          exportArticles.map((article) => ({
            날짜: article.date,
            제목: article.title,
            출처: article.source,
            링크: article.link,
          })),
        );
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "뉴스클리핑");
        XLSX.writeFile(workbook, `${today}_daily_news.xlsx`);
        return;
      }

      if (fileType === "word") {
        downloadBlob(
          new Blob([html || ""], {
            type: "application/msword;charset=utf-8",
          }),
          `${today}_daily_news.doc`,
        );
        return;
      }

      if (fileType === "pdf") {
        await downloadPdfFromArticles(exportArticles, today);
      }
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "파일 저장에 실패했습니다.",
      );
    }
  }

  async function handleCopyHtml() {
    if (!html) {
      return;
    }

    await navigator.clipboard.writeText(html);
    setIsCopied(true);
    window.setTimeout(() => setIsCopied(false), 1300);
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <button className="brand-button" type="button" onClick={handleReset}>
          <img src={BIZ_LOGO_URL} alt="빗썸 biz" className="brand-logo" />
        </button>
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
                    <button type="button" onClick={() => handleLoadHistory(history)}>
                      <strong>{formatHistoryDate(history.created_at)}</strong>
                      <span>{history.article_count}건 수집</span>
                    </button>
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
            <details className="query-details">
              <summary>현재 검색 조건</summary>
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
                disabled={Boolean(activeHistoryId)}
              />
              <DateField
                label="To"
                value={endDate}
                isOpen={openDatePicker === "end"}
                onOpen={() => setOpenDatePicker("end")}
                onClose={() => setOpenDatePicker(null)}
                onChange={setEndDate}
                disabled={Boolean(activeHistoryId)}
              />
              {!activeHistoryId && (
                <button
                  className="primary-button"
                  type="button"
                  onClick={handleSearch}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <span className="button-spinner" aria-hidden />
                      <span>수집 중</span>
                    </>
                  ) : (
                    "RUN"
                  )}
                </button>
              )}
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

              {hasAppliedSelection && (
              <section className="actions-section">
                <div className="action-row">
                  <CustomDropdown
                    label="파일 다운로드"
                    value={fileType}
                    options={fileOptions}
                    isOpen={openMenu === "file"}
                    onToggle={() => setOpenMenu(openMenu === "file" ? null : "file")}
                    onChange={(nextValue) => {
                      setFileType(nextValue);
                      setOpenMenu(null);
                    }}
                  />
                  <button
                    className="primary-button action-button"
                    type="button"
                    onClick={handleSaveFile}
                    disabled={!orderedArticles.length}
                  >
                    저장
                  </button>
                </div>
                <div className="action-row">
                  <CustomDropdown
                    label="이메일 템플릿"
                    value={template}
                    options={templateOptions}
                    isOpen={openMenu === "template"}
                    onToggle={() =>
                      setOpenMenu(openMenu === "template" ? null : "template")
                    }
                    onChange={(nextValue) => {
                      setTemplate(nextValue as NewsletterTemplate);
                      setOpenMenu(null);
                    }}
                  />
                  <button
                    className="primary-button action-button"
                    type="button"
                    onClick={handleGenerateHtml}
                    disabled={!orderedArticles.length || isGenerating}
                  >
                    {isGenerating ? "생성 중" : "만들기"}
                  </button>
                </div>
              </section>
              )}

              {html && (
              <section className="template-section">
                <div className="code-panel">
                  <div className="panel-header">
                    <strong>Code Block</strong>
                    <button
                      className={`copy-button ${isCopied ? "is-copied" : ""}`}
                      type="button"
                      onClick={handleCopyHtml}
                      disabled={!html}
                      aria-label="HTML 코드 복사"
                    >
                      <CopyIcon />
                      {isCopied && <span>Copied</span>}
                    </button>
                  </div>
                  <pre>{html || "HTML 생성 후 코드가 여기에 표시됩니다."}</pre>
                </div>

                <div className="preview-panel">
                  <div className="panel-header">
                    <strong>Preview</strong>
                    <button
                      className="download-button"
                      type="button"
                      onClick={handleDownloadHtml}
                      disabled={!html}
                      aria-label="HTML 다운로드"
                    >
                      <img src="/icons/download.svg" alt="" />
                    </button>
                  </div>
                  {html ? (
                    <iframe title="email html preview" srcDoc={html} />
                  ) : (
                    <div className="preview-empty" />
                  )}
                </div>
              </section>
              )}

              <div className="pdf-export-stage" aria-hidden>
                <div className="pdf-export-sheet" ref={exportSheetRef}>
                  <div className="pdf-export-title">빗썸 BIZ 뉴스레터</div>
                  <div className="pdf-export-date">{formatKoreanDate(today)}</div>
                  <table>
                    <thead>
                      <tr>
                        <th>날짜</th>
                        <th>제목</th>
                        <th>출처</th>
                        <th>링크</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orderedArticles.map((article) => (
                        <tr key={article.id}>
                          <td>{article.date}</td>
                          <td>{article.title}</td>
                          <td>{article.source}</td>
                          <td>{article.link}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  );
}

async function resolveArticlesForExport(articles: NewsArticle[]) {
  const response = await fetch("/api/news/resolve", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      articles,
    }),
  });
  const data = (await response.json()) as ResolveArticlesResponse;

  if (!data.ok) {
    throw new Error(data.message ?? "기사 링크 정리에 실패했습니다.");
  }

  return data.articles ?? articles;
}

function CustomDropdown({
  label,
  value,
  options,
  isOpen,
  onToggle,
  onChange,
}: {
  label: string;
  value: string;
  options: Array<{
    value: string;
    label: string;
  }>;
  isOpen: boolean;
  onToggle: () => void;
  onChange: (value: string) => void;
}) {
  const selectedOption = options.find((option) => option.value === value);

  return (
    <div className="custom-select">
      <span className="custom-select-label">{label}</span>
      <button className="custom-select-trigger" type="button" onClick={onToggle}>
        <span>{selectedOption?.label ?? ""}</span>
        <span className="dropdown-arrow" aria-hidden />
      </button>
      {isOpen && (
        <div className="custom-select-menu">
          {options.map((option) => (
            <button
              className={option.value === value ? "is-selected" : ""}
              key={option.value}
              type="button"
              onClick={() => onChange(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function DateField({
  label,
  value,
  isOpen,
  onOpen,
  onClose,
  onChange,
  disabled = false,
}: {
  label: string;
  value: string;
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
  onChange: (value: string) => void;
  disabled?: boolean;
}) {
  const selectedDate = parseDate(value);

  return (
    <label className="date-field">
      <span>{label}</span>
      <button
        className="date-trigger"
        type="button"
        onClick={isOpen ? onClose : onOpen}
        disabled={disabled}
      >
        <CalendarIcon />
        <span>{formatDisplayDate(value)}</span>
        <img src="/icons/clear.png" alt="" aria-hidden className="date-clear" />
      </button>
      {isOpen && !disabled && (
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

function CopyIcon() {
  return (
    <svg width="17" height="23" viewBox="0 0 17 23" fill="none" aria-hidden>
      <path fillRule="evenodd" clipRule="evenodd" d="M10.625 4.70655e-07H7.24467C5.71319 -2.02995e-05 4.50016 -3.07488e-05 3.55082 0.159038C2.5738 0.322728 1.78301 0.667638 1.15937 1.44482C0.535734 2.22201 0.258967 3.2075 0.127617 4.42507C-2.45745e-05 5.60815 -1.6289e-05 7.11984 3.7763e-07 9.02836V15.318C3.7763e-07 17.2623 1.14338 18.8739 2.63793 19.1654C2.7529 19.9588 2.97294 20.636 3.41529 21.1874C3.91689 21.8124 4.54845 22.0813 5.29854 22.207C6.02102 22.328 6.93958 22.328 8.07925 22.328H10.6707C11.8104 22.328 12.729 22.328 13.4515 22.207C14.2016 22.0813 14.8331 21.8124 15.3347 21.1874C15.8363 20.5622 16.0521 19.7752 16.1529 18.8404C16.25 17.9401 16.25 16.7953 16.25 15.375V10.0685C16.25 8.64823 16.25 7.50346 16.1529 6.60311C16.0521 5.66833 15.8363 4.88128 15.3347 4.25618C14.8923 3.70492 14.3489 3.4307 13.7122 3.28741C13.4783 1.42489 12.1852 4.70655e-07 10.625 4.70655e-07ZM12.3994 3.13752C12.1471 2.2185 11.448 1.55777 10.625 1.55777H7.29167C5.70265 1.55777 4.57376 1.55942 3.71738 1.70291C2.87897 1.84338 2.39593 2.10682 2.04325 2.54632C1.69058 2.98583 1.47918 3.5878 1.36647 4.63264C1.25133 5.69987 1.25 7.10671 1.25 9.08696V15.318C1.25 16.3437 1.7802 17.2149 2.51764 17.5293C2.49998 16.8959 2.49999 16.1797 2.5 15.375V10.0685C2.49998 8.64823 2.49997 7.50346 2.5971 6.60311C2.69795 5.66833 2.91369 4.88128 3.41529 4.25618C3.91689 3.63108 4.54845 3.36222 5.29854 3.23654C6.02102 3.11549 6.93958 3.11551 8.07925 3.11553H10.6707C11.3164 3.11552 11.8912 3.11551 12.3994 3.13752ZM4.29918 5.35768C4.52981 5.07027 4.85363 4.88287 5.4651 4.78042C6.09456 4.67495 6.92883 4.6733 8.125 4.6733H10.625C11.8212 4.6733 12.6554 4.67495 13.2849 4.78042C13.8964 4.88287 14.2202 5.07027 14.4508 5.35768C14.6815 5.6451 14.8318 6.04865 14.9141 6.81067C14.9987 7.59511 15 8.63478 15 10.1255V15.318C15 16.8087 14.9987 17.8484 14.9141 18.6328C14.8318 19.3949 14.6815 19.7984 14.4508 20.0858C14.2202 20.3733 13.8964 20.5606 13.2849 20.6631C12.6554 20.7685 11.8212 20.7702 10.625 20.7702H8.125C6.92883 20.7702 6.09456 20.7685 5.4651 20.6631C4.85363 20.5606 4.52981 20.3733 4.29918 20.0858C4.06854 19.7984 3.91817 19.3949 3.83596 18.6328C3.75133 17.8484 3.75 16.8087 3.75 15.318V10.1255C3.75 8.63478 3.75133 7.59511 3.83596 6.81067C3.91817 6.04865 4.06854 5.6451 4.29918 5.35768Z" fill="#5E5E5E" />
    </svg>
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
  return <img src="/icons/calendar.png" alt="" aria-hidden className="field-icon" />;
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

function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

async function downloadPdfFromExportSheet(
  element: HTMLDivElement | null,
  today: string,
) {
  if (!element) {
    return;
  }

  const [{ jsPDF }, html2canvasModule] = await Promise.all([
    import("jspdf"),
    import("html2canvas"),
  ]);
  const html2canvas = html2canvasModule.default;
  const canvas = await html2canvas(element, {
    scale: 2,
    backgroundColor: "#ffffff",
    useCORS: true,
  });
  const imageData = canvas.toDataURL("image/png");
  const pdf = new jsPDF({
    orientation: "p",
    unit: "mm",
    format: "a4",
  });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const imageWidth = pageWidth;
  const imageHeight = (canvas.height * imageWidth) / canvas.width;
  let remainingHeight = imageHeight;
  let y = 0;

  pdf.addImage(imageData, "PNG", 0, y, imageWidth, imageHeight);
  remainingHeight -= pageHeight;

  while (remainingHeight > 0) {
    y -= pageHeight;
    pdf.addPage();
    pdf.addImage(imageData, "PNG", 0, y, imageWidth, imageHeight);
    remainingHeight -= pageHeight;
  }

  pdf.save(`${today}_daily_news.pdf`);
}

async function downloadPdfFromArticles(articles: NewsArticle[], today: string) {
  const stage = document.createElement("div");
  stage.className = "pdf-export-stage";
  stage.setAttribute("aria-hidden", "true");
  stage.innerHTML = `
    <div class="pdf-export-sheet">
      <div class="pdf-export-title">빗썸 BIZ 뉴스레터</div>
      <div class="pdf-export-date">${formatKoreanDate(today)}</div>
      <table>
        <thead>
          <tr>
            <th>날짜</th>
            <th>제목</th>
            <th>출처</th>
            <th>링크</th>
          </tr>
        </thead>
        <tbody>
          ${articles
            .map(
              (article) => `
                <tr>
                  <td>${escapeHtml(article.date)}</td>
                  <td>${escapeHtml(article.title)}</td>
                  <td>${escapeHtml(article.source)}</td>
                  <td>${escapeHtml(article.link)}</td>
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
  document.body.appendChild(stage);

  try {
    await downloadPdfFromExportSheet(
      stage.querySelector(".pdf-export-sheet") as HTMLDivElement,
      today,
    );
  } finally {
    stage.remove();
  }
}

function escapeHtml(value = "") {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatKoreanDate(value: string) {
  const date = parseDate(value);

  if (!date) {
    return value;
  }

  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`;
}

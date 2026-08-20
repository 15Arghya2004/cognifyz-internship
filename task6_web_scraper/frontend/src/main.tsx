import { useEffect, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowDownToLine,
  Check,
  ChevronDown,
  CircleAlert,
  Database,
  ExternalLink,
  FileSearch,
  Filter,
  Gauge,
  Globe2,
  LoaderCircle,
  Play,
  RefreshCw,
  Search,
  Server,
  SlidersHorizontal,
  Sparkles,
  Waypoints,
  X,
} from "lucide-react";
import "./styles.css";

type Source = {
  id: string;
  name: string;
  base_url: string;
  domain: string;
  type: string;
  max_pages: number;
  verified: boolean;
};
type RecordItem = Record<string, string | number | string[] | null>;
type Stats = {
  pages_requested: number;
  http_requests: number;
  records_found: number;
  valid_records: number;
  invalid_records: number;
  elapsed_seconds: number;
  average_price_inr?: number | null;
  average_rating?: number | null;
  available_records?: number;
};
type HealthStep = { ok: boolean; label: string };
type Currency = {
  display_currency: string;
  rate: number | null;
  updated_at: string | null;
  available: boolean;
};
// One place that decides where the API lives. An empty base means "same
// origin", which lets the Vite dev proxy in vite.config.ts forward /api to
// the backend on port 8000.
const API_BASE = "";

const api = async (path: string, options?: RequestInit) => {
  let response: Response;
  try {
    response = await fetch(API_BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    // fetch itself rejected: nothing listening, connection reset, DNS failure.
    throw new Error(
      "Backend unavailable. Make sure the scraper API is running on port 8000.",
    );
  }

  // Read the body as text first. Calling response.json() straight away turns
  // every empty or non-JSON reply into "Unexpected end of JSON input" and
  // throws the real HTTP status away. A dev-proxy 502 has a zero-byte body.
  const raw = await response.text();
  let data: any = null;
  if (raw.trim()) {
    try {
      data = JSON.parse(raw);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const backendMessage = data && (data.message || data.detail);
    if (typeof backendMessage === "string" && backendMessage) {
      throw new Error(backendMessage);
    }
    if (data === null && response.status >= 500) {
      throw new Error(
        "Backend unavailable. Make sure the scraper API is running on port 8000.",
      );
    }
    throw new Error(
      response.status >= 500
        ? `Backend error (HTTP ${response.status}).`
        : `Request failed (HTTP ${response.status}).`,
    );
  }

  if (data === null) {
    throw new Error(
      `Backend returned an unreadable response (HTTP ${response.status}).`,
    );
  }
  return data;
};

function App() {
  const [sources, setSources] = useState<Source[]>([]),
    [sourceId, setSourceId] = useState("1"),
    [records, setRecords] = useState<RecordItem[]>([]),
    [stats, setStats] = useState<Stats | null>(null),
    [verified, setVerified] = useState(false),
    [healthSteps, setHealthSteps] = useState<HealthStep[]>([]),
    [currency, setCurrency] = useState<Currency | null>(null),
    [loading, setLoading] = useState(false),
    [error, setError] = useState(""),
    [query, setQuery] = useState(""),
    [mode, setMode] = useState("current"),
    [pages, setPages] = useState(2),
    [filters, setFilters] = useState({
      author: "",
      tag: "",
      max_price: "",
      min_rating: "",
      only_stock: false,
      category: "",
    }),
    [probe, setProbe] = useState<Record<string, unknown> | null>(null),
    [exported, setExported] = useState(""),
    [showTechnical, setShowTechnical] = useState(false);
  const source = sources.find((item) => item.id === sourceId),
    books = source?.type === "books";
  const sourceLabel = (item: Source) => item.type === "books" ? "Global Books" : item.name;
  useEffect(() => {
    api("/api/sources")
      .then((data) => {
        setSources(data.sources);
        setSourceId(data.current_source);
      })
      .catch((e) => setError(e.message));
  }, []);
  const run = async (work: () => Promise<void>) => {
    setLoading(true);
    setError("");
    setExported("");
    try {
      await work();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };
  const switchSource = (id: string) => {
    setSourceId(id);
    setRecords([]);
    setStats(null);
    setVerified(false);
    setHealthSteps([]);
    setCurrency(null);
    setQuery("");
    setProbe(null);
    setFilters({
      author: "",
      tag: "",
      max_price: "",
      min_rating: "",
      only_stock: false,
      category: "",
    });
    setError("");
    api(`/api/sources/${id}/verify`, { method: "POST" })
      .then((data) => {
        setVerified(data.verified);
        setHealthSteps(data.steps);
        setCurrency(data.currency || null);
      })
      .catch((e) => setError(e.message));
  };
  const verify = () =>
    run(async () => {
      const data = await api(`/api/sources/${sourceId}/verify`, {
        method: "POST",
      });
      setVerified(data.verified);
      setHealthSteps(data.steps);
    });
  const scrape = () =>
    run(async () => {
      const data = await api("/api/scrape", {
        method: "POST",
        body: JSON.stringify({
          source_id: sourceId,
          mode,
          pages: mode === "custom" ? pages : null,
        }),
      });
      setRecords(data.records);
      setStats(data.stats);
      setVerified(true);
      setCurrency(data.currency || null);
    });
  const filter = () =>
    run(async () => {
      const data = await api("/api/filter", {
        method: "POST",
        body: JSON.stringify({
          source_id: sourceId,
          query,
          ...filters,
          max_price: filters.max_price ? Number(filters.max_price) : null,
          min_rating: filters.min_rating ? Number(filters.min_rating) : null,
        }),
      });
      setRecords(data.records);
      setStats(data.stats || stats);
      setCurrency(data.currency || currency);
    });
  const clearFilters = () =>
    run(async () => {
      const data = await api("/api/filter", {
        method: "POST",
        body: JSON.stringify({ source_id: sourceId }),
      });
      setQuery("");
      setFilters({ author: "", tag: "", max_price: "", min_rating: "", only_stock: false, category: "" });
      setRecords(data.records);
      setStats(data.stats || stats);
      setCurrency(data.currency || currency);
    });
  const exportFile = (format: string) =>
    run(async () => {
      const data = await api("/api/export", {
        method: "POST",
        body: JSON.stringify({ format }),
      });
      setExported(data.download_url);
    });
  const doProbe = () =>
    run(async () =>
      setProbe(
        await api("/api/probe", {
          method: "POST",
          body: JSON.stringify({ source_id: sourceId }),
        }),
      ),
    );
  return (
    <div className="app-shell">
      <aside className="rail">
        <div className="brand">
          <div className="brand-mark">
            <Waypoints size={19} />
          </div>
          <div>
            <strong>COGNIFYZ</strong>
            <span>WEB SCRAPER</span>
          </div>
        </div>
        <div className="rail-label">SOURCE</div>
        <div className="source-list">
          {sources.map((item) => (
            <button
              className={item.id === sourceId ? "source active" : "source"}
              key={item.id}
              onClick={() => switchSource(item.id)}
            >
              <span className="source-dot" />
              <span>
                <b>{sourceLabel(item)}</b>
                <small>{item.type === "books" ? "Books to Scrape" : item.domain}</small>
              </span>
              <ChevronDown size={14} />
            </button>
          ))}
        </div>
        <div className="rail-panel">
          <div className="eyebrow">
            SOURCE PROFILE <Globe2 size={13} />
          </div>
          <h3>{source ? sourceLabel(source) : "Loading source"}</h3>
          <a href={source?.base_url} target="_blank">
            {source?.base_url} <ExternalLink size={12} />
          </a>
          <div className="profile-row">
            <span>parser</span>
            <b>{source?.type || "—"}</b>
          </div>
          <div className="profile-row">
            <span>page ceiling</span>
            <b>{source?.max_pages || "—"}</b>
          </div>
        </div>
        <div className="rail-panel scrape-panel">
          <div className="eyebrow">
            SCRAPE CONTROL <SlidersHorizontal size={13} />
          </div>
          <div className="segmented">
            {[
              ["current", "CURRENT"],
              ["custom", "PAGES"],
              ["all", "ALL"],
            ].map(([key, label]) => (
              <button
                key={key}
                className={mode === key ? "selected" : ""}
                onClick={() => setMode(key)}
              >
                {label}
              </button>
            ))}
          </div>
          {mode === "custom" && (
            <label className="field compact">
              Pages
              <input
                type="number"
                min="1"
                max={source?.max_pages || 50}
                value={pages}
                onChange={(e) => setPages(Number(e.target.value))}
              />
            </label>
          )}
          <button
            className="primary-button"
            onClick={scrape}
            disabled={loading}
          >
            <Play size={15} fill="currentColor" />{" "}
            {loading ? "Working" : "Run scrape"}
          </button>
        </div>
        <div className="rail-foot">
          <span>
            <Server size={14} /> API online
          </span>
          <span className="mono">v1.0 / JSON</span>
        </div>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div>
            <div className="kicker">OPERATIONS / COLLECTIONS / 06</div>
            <h1>
              Web Scraper <span>Control Room</span>
            </h1>
          </div>
          <div className="header-actions">
            <div className={verified ? "connection good" : "connection"}>
              <span className="pulse" />
              {verified ? "SOURCE VERIFIED" : "SOURCE UNVERIFIED"}
            </div>
            <button
              className="icon-button"
              title="Verify source"
              onClick={verify}
              disabled={loading}
            >
              <RefreshCw size={17} />
            </button>
          </div>
        </header>
        {error && (
          <div className="error-banner">
            <CircleAlert size={18} />
            <span>{error}</span>
            <button onClick={() => setError("")}>
              <X size={15} />
            </button>
          </div>
        )}
        <section className="status-strip">
          <div className="status-copy">
            <div className="status-icon">
              <Activity size={22} />
            </div>
            <div>
              <span className="eyebrow">COLLECTION STATUS</span>
              <h2>
                {!stats
                  ? "Awaiting a collection run"
                  : records.length
                    ? "Dataset ready for review"
                    : `${stats.valid_records} records collected \u00b7 0 matching the current filter`}
              </h2>
              <p>
                {!stats
                  ? "Verify the source, then run a scrape to populate the workspace."
                  : records.length
                    ? `${records.length} validated records in the active result set.`
                    : "The collection ran successfully. Widen or clear the filter to bring the records back."}
              </p>
            </div>
          </div>
          <div className="status-meta">
            <span>
              ACTIVE SOURCE <b>{source?.type?.toUpperCase() || "—"}</b>
            </span>
            <span>
              REQUEST POLICY <b>POLITE / HTTPS</b>
            </span>
          </div>
        </section>
        <section className="kpis">
          <Kpi
            icon={<Database />}
            label="RESULTS"
            value={records.length ? String(records.length) : "—"}
            note={stats ? `${stats.valid_records} valid` : "No current set"}
          />
          <Kpi
            icon={<Check />}
            label="AVAILABLE"
            value={stats?.available_records != null ? String(stats.available_records) : "N/A"}
            note={stats ? "In stock" : "Awaiting run"}
          />
          <Kpi
            icon={<Sparkles />}
            label="AVERAGE PRICE"
            value={stats?.average_price_inr != null ? `₹${stats.average_price_inr.toFixed(0)}` : "N/A"}
            note={currency?.available ? "Live GBP → INR" : "INR unavailable"}
          />
          <Kpi
            icon={<Gauge />}
            label="AVERAGE RATING"
            value={stats?.average_rating != null ? `${stats.average_rating.toFixed(1)} / 5` : "N/A"}
            note={stats ? "Validated records" : "Awaiting run"}
          />
          <Kpi
            icon={<Database />}
            label="PAGES"
            value={stats ? String(stats.pages_requested) : "—"}
            note={stats ? `${stats.http_requests} requests` : "Awaiting run"}
          />
        </section>
        <div className="content-grid">
          <section className="results-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">RESULT REGISTER</span>
                <h2>
                  {books ? "Books" : "Quotes"}{" "}
                  <span>
                    {records.length ? `· ${records.length} rows` : "· empty"}
                  </span>
                </h2>
              </div>
              <div className="table-actions">
                <label className="search">
                  <Search size={16} />
                  <input
                    placeholder={books ? "Search titles" : "Search quotes"}
                    value={query}
                    disabled={!stats}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && filter()}
                  />
                </label>
                <button
                  className="filter-button"
                  disabled={!stats}
                  onClick={filter}
                >
                  <Filter size={15} /> Filter
                </button>
              </div>
            </div>
            {records.length ? (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      {books ? (
                        <>
                          <th>Title</th>
                          <th>Price</th>
                          <th>Rating</th>
                          <th>Availability</th>
                          <th>Category</th>
                          <th>Source</th>
                        </>
                      ) : (
                        <>
                          <th>Quote</th>
                          <th>Author</th>
                          <th>Tags</th>
                          <th>Source</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((item, index) => (
                      <tr key={index}>
                        {books ? (
                          <>
                            <td className="strong">{String(item.title)}</td>
                            <td className="price">
                              £{Number(item.price).toFixed(2)}
                            </td>
                            <td>
                              <span className="rating">
                                {"★".repeat(Number(item.rating))}
                                {"☆".repeat(5 - Number(item.rating))}
                              </span>
                            </td>
                            <td>
                              <span className="stock">
                                <span /> {String(item.availability)}
                              </span>
                            </td>
                            <td>{String(item.category || "—")}</td>
                            <td><a className="record-link" href={String(item.url)} target="_blank" rel="noreferrer">Open</a></td>
                          </>
                        ) : (
                          <>
                            <td className="quote">{String(item.quote)}</td>
                            <td className="strong">{String(item.author)}</td>
                            <td>
                              {(item.tags as string[]).map((tag) => (
                                <span className="tag" key={tag}>
                                  {tag}
                                </span>
                              ))}
                            </td>
                            <td><a className="record-link" href={String(item.author_url)} target="_blank" rel="noreferrer">Author</a></td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty">
                <div className="empty-icon">
                  <FileSearch size={27} />
                </div>
                <h3>
                  {stats
                    ? "0 matching records"
                    : "Your result register is empty"}
                </h3>
                <p>
                  {stats
                    ? `The collection ran and returned ${stats.valid_records} records, but none match the current filter. Widen or clear the filter to see them again.`
                    : `Run the ${books ? "Books to Scrape" : "Quotes to Scrape"} collection from the left rail. Records will appear here with live validation and source-aware fields.`}
                </p>
                {stats ? (
                  <button className="text-button" onClick={clearFilters}>
                    <X size={15} /> Clear filters
                  </button>
                ) : (
                  <button className="text-button" onClick={scrape}>
                    <Play size={15} /> Start collection
                  </button>
                )}
              </div>
            )}
          </section>
          <aside className="utility">
            <Utility title="Health checklist" icon={<Check />}>
              {healthSteps.length ? (
                healthSteps.map((step) => (
                  <div className="health-line" key={step.label}>
                    <span className={step.ok ? "check" : "pending"}>
                      {step.ok ? <Check size={12} /> : <CircleAlert size={12} />}
                    </span>
                    <span>
                      <b>{step.label}</b>
                      <small>{step.ok ? "Passed" : "Failed"}</small>
                    </span>
                  </div>
                ))
              ) : (
                <div className="health-line">
                  <span className="pending">
                    <LoaderCircle size={12} />
                  </span>
                  <span>
                    <b>Source verification</b>
                    <small>Run verify before scraping</small>
                  </span>
                </div>
              )}
              <div className="health-line">
                <span className={records.length ? "check" : "pending"}>
                  {records.length ? (
                    <Check size={12} />
                  ) : (
                    <LoaderCircle size={12} />
                  )}
                </span>
                <span>
                  <b>Record validation</b>
                  <small>
                    {records.length
                      ? "Current result set is available"
                      : "No records in memory"}
                  </small>
                </span>
              </div>
            </Utility>
            <Utility title="Exports" icon={<ArrowDownToLine />}>
              <p className="utility-copy">
                Download the active result set in an analyst-ready format.
              </p>
              <div className="export-row">
                <button
                  disabled={!records.length}
                  onClick={() => exportFile("csv")}
                >
                  CSV <ArrowDownToLine size={13} />
                </button>
                <button
                  disabled={!records.length}
                  onClick={() => exportFile("json")}
                >
                  JSON <ArrowDownToLine size={13} />
                </button>
                <button
                  disabled={!records.length}
                  onClick={() => exportFile("pdf")}
                >
                  PDF <ArrowDownToLine size={13} />
                </button>
              </div>
              {exported && (
                <a className="download-link" href={exported}>
                  Download latest export <ArrowDownToLine size={13} />
                </a>
              )}
            </Utility>
            <Utility title="Structure probe" icon={<FileSearch />}>
              <p className="utility-copy">
                Inspect headings, links, and pagination on the active source.
              </p>
              <button
                className="probe-button"
                onClick={doProbe}
                disabled={loading}
              >
                <FileSearch size={14} /> Probe source
              </button>
              {probe && (
                <div className="probe-result">
                  <b>{String(probe.title)}</b>
                  <span>
                    {String(probe.status)} · {String(probe.links)} links ·{" "}
                    {probe.pagination ? "pagination found" : "no pagination"}
                  </span>
                </div>
              )}
            </Utility>
          </aside>
        </div>
        <button
          className="technical-toggle"
          onClick={() => setShowTechnical(!showTechnical)}
        >
          {showTechnical ? "Hide technical details" : "View technical details"}
        </button>
        {showTechnical && (
          <section className="technical-details">
            <div>
              <span className="eyebrow">REQUEST DETAILS</span>
              <p>
                {stats
                  ? `${stats.pages_requested} pages · ${stats.http_requests} requests · ${stats.elapsed_seconds.toFixed(2)}s`
                  : "No scrape recorded"}
              </p>
            </div>
            <div>
              <span className="eyebrow">CURRENCY</span>
              <p>
                {currency?.available
                  ? `1 GBP = INR ${currency.rate?.toFixed(2)}`
                  : "INR conversion unavailable"}
              </p>
            </div>
            <div>
              <span className="eyebrow">SOURCE</span>
              <p>{source?.base_url || "No source selected"}</p>
            </div>
          </section>
        )}
        <section className="filter-band">
          <div>
            <span className="eyebrow">SOURCE FILTERS</span>
            <h2>
              {books ? "Tune the book register" : "Tune the quote register"}
            </h2>
          </div>
          {books ? (
            <>
              <Field
                label="Max price"
                value={filters.max_price}
                onChange={(value) =>
                  setFilters({ ...filters, max_price: value })
                }
                placeholder="Any price"
              />
              <Field
                label="Min rating"
                value={filters.min_rating}
                onChange={(value) =>
                  setFilters({ ...filters, min_rating: value })
                }
                placeholder="1—5"
              />
              <Field
                label="Category"
                value={filters.category}
                onChange={(value) => setFilters({ ...filters, category: value })}
                placeholder="Any category"
              />
              <label className="check-control">
                <input
                  type="checkbox"
                  checked={filters.only_stock}
                  onChange={(e) =>
                    setFilters({ ...filters, only_stock: e.target.checked })
                  }
                />{" "}
                In stock only
              </label>
            </>
          ) : (
            <>
              <Field
                label="Author"
                value={filters.author}
                onChange={(value) => setFilters({ ...filters, author: value })}
                placeholder="Any author"
              />
              <Field
                label="Tag"
                value={filters.tag}
                onChange={(value) => setFilters({ ...filters, tag: value })}
                placeholder="Any tag"
              />
            </>
          )}
          <button
            className="apply-button"
            disabled={!stats}
            onClick={filter}
          >
            Apply filters
          </button>
          <button
            className="clear-button"
            disabled={!stats}
            onClick={clearFilters}
          >
            Clear filters
          </button>
        </section>
      </main>
    </div>
  );
}
function Kpi({
  icon,
  label,
  value,
  note,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  note: string;
}) {
  return (
    <div className="kpi">
      <span className="kpi-icon">{icon}</span>
      <div>
        <span className="eyebrow">{label}</span>
        <strong>{value}</strong>
        <small>{note}</small>
      </div>
    </div>
  );
}
function Utility({
  title,
  icon,
  children,
}: {
  title: string;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="utility-block">
      <div className="utility-title">
        <span>{icon}</span>
        <h3>{title}</h3>
      </div>
      {children}
    </section>
  );
}
function Field({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}) {
  return (
    <label className="field">
      {label}
      <input
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
export default App;

createRoot(document.getElementById("root")!).render(<App />);

const STATUS_LABELS: Record<string, string> = {
  submitted: "Submitted",
  under_review: "Under review",
  assigned: "Assigned",
  investigating: "Investigating",
  escalated: "Escalated",
  contained: "Contained",
  remediated: "Remediated",
  recovered: "Recovered",
  closed: "Closed",
};

const CATEGORY_LABELS: Record<string, string> = {
  phishing: "Phishing",
  fake_portal: "Fake portal",
  impersonation: "Impersonation",
  payment_fraud: "Payment fraud",
  malware: "Malware",
  fake_result: "False result claim",
  other: "Other",
};

const CHANNEL_LABELS: Record<string, string> = {
  email: "Email",
  sms: "SMS",
  whatsapp: "WhatsApp",
  web_form: "Web form",
  phone: "Phone",
  other: "Other",
};

export function statusLabel(value: string): string {
  return STATUS_LABELS[value] ?? humanise(value);
}

export function categoryLabel(value: string): string {
  return CATEGORY_LABELS[value] ?? humanise(value);
}

export function channelLabel(value: string): string {
  return CHANNEL_LABELS[value] ?? humanise(value);
}

export function humanise(value: string): string {
  return value.replace(/[_-]+/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function relativeTime(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  const seconds = Math.round((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days < 30) return `${days}d ago`;
  return formatDateTime(value).split(",")[0];
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(kb >= 10 ? 0 : 1)} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

export function shortHash(hash: string | null | undefined, size = 10): string {
  if (!hash) return "—";
  return hash.length <= size * 2 ? hash : `${hash.slice(0, size)}…${hash.slice(-4)}`;
}

export function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

export function evidenceKind(contentType: string): string {
  if (contentType.startsWith("image/")) return "Image";
  if (contentType === "application/pdf") return "PDF";
  if (contentType === "message/rfc822") return "Email";
  if (contentType === "text/plain") return "Text";
  return "File";
}

export function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

const INDICATOR_KIND_LABELS: Record<string, string> = {
  url: "URL",
  domain: "Domain",
  ipv4: "IPv4",
  sha256: "SHA-256",
  md5: "MD5",
};

export function indicatorKindLabel(value: string): string {
  return INDICATOR_KIND_LABELS[value] ?? humanise(value);
}

export function formatShortDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

export function formatDay(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

export function formatHours(hours: number | null | undefined): string {
  if (hours === null || hours === undefined) return "—";
  if (hours < 1) return `${Math.round(hours * 60)} min`;
  if (hours < 48) return `${hours.toFixed(1)} h`;
  return `${(hours / 24).toFixed(1)} d`;
}

export function compactNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  if (Math.abs(value) < 1000) return String(value);
  return new Intl.NumberFormat("en-GB", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

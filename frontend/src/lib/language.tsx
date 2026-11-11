import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import en, { type TranslationKey } from "./locales/en";
import ha from "./locales/ha";
import yo from "./locales/yo";
import ig from "./locales/ig";

export type Lang = "en" | "ha" | "yo" | "ig";

export type Language = {
  code: Lang;
  /** English label, used for documentation and fallbacks. */
  label: string;
  /** Endonym shown in the switcher, written in the language itself. */
  native: string;
  short: string;
};

export const languages: Language[] = [
  { code: "en", label: "English", native: "English", short: "EN" },
  { code: "ha", label: "Hausa", native: "Hausa", short: "HA" },
  { code: "yo", label: "Yoruba", native: "Yorùbá", short: "YO" },
  { code: "ig", label: "Igbo", native: "Igbo", short: "IG" },
];

const dictionaries: Record<Lang, Record<TranslationKey, string>> = { en, ha, yo, ig };

const LOCALE_TAGS: Record<Lang, string> = {
  en: "en-GB",
  ha: "ha-NG",
  yo: "yo-NG",
  ig: "ig-NG",
};

export function localeTag(lang: Lang): string {
  return LOCALE_TAGS[lang];
}

const STORAGE_KEY = "votex.lang";
const DEFAULT_LANG: Lang = "en";

export type Translate = (
  key: TranslationKey,
  vars?: Record<string, string | number>,
) => string;

function isLang(value: string | null): value is Lang {
  return value !== null && value in dictionaries;
}

function readStoredLang(): Lang {
  if (typeof window === "undefined") return DEFAULT_LANG;
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return isLang(stored) ? stored : DEFAULT_LANG;
  } catch {
    return DEFAULT_LANG;
  }
}

/** Replaces `{name}` tokens; unknown tokens are left untouched rather than dropped. */
function interpolate(template: string, vars?: Record<string, string | number>): string {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (match, name: string) =>
    Object.prototype.hasOwnProperty.call(vars, name) ? String(vars[name]) : match,
  );
}

type LanguageContextValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: Translate;
  languages: Language[];
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(readStoredLang);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = "ltr";
    try {
      window.localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      // Storage can be disabled; the in-memory choice still works for this session.
    }
  }, [lang]);

  const setLang = useCallback((next: Lang) => {
    setLangState(next);
  }, []);

  const t = useCallback<Translate>(
    (key, vars) => {
      const value = dictionaries[lang][key] ?? en[key] ?? key;
      return interpolate(value, vars);
    },
    [lang],
  );

  const value = useMemo<LanguageContextValue>(
    () => ({ lang, setLang, t, languages }),
    [lang, setLang, t],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useI18n(): LanguageContextValue {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useI18n must be used inside a LanguageProvider.");
  }
  return context;
}

/**
 * Locale-aware relative time used by the queue and overview. Kept beside the
 * provider so every screen shares one wording instead of duplicating English.
 */
export function formatRelative(
  t: Translate,
  value: string | null | undefined,
  lang: Lang = "en",
): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  const seconds = Math.round((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return t("time.justNow");
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return t("time.minutesAgo", { count: minutes });
  const hours = Math.round(minutes / 60);
  if (hours < 24) return t("time.hoursAgo", { count: hours });
  const days = Math.round(hours / 24);
  if (days < 30) return t("time.daysAgo", { count: days });
  return date.toLocaleDateString(localeTag(lang), { day: "numeric", month: "short" });
}

export type { TranslationKey };

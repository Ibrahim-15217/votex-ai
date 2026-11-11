import { languages, type Lang } from "../lib/i18n";

type Props = {
  lang: Lang;
  onChange: (lang: Lang) => void;
  label: string;
};

/**
 * Four-language switcher. Each target is at least 28×32 CSS pixels so it clears
 * the WCAG 2.2 target-size minimum on touch screens, and the endonym is exposed
 * to assistive technology and on hover.
 */
export function LanguageSwitcher({ lang, onChange, label }: Props) {
  return (
    <div
      role="group"
      aria-label={label}
      className="inline-flex items-center gap-0.5 rounded-full border border-line bg-surface/80 p-0.5"
    >
      {languages.map((language) => {
        const active = language.code === lang;

        return (
          <button
            key={language.code}
            type="button"
            onClick={() => onChange(language.code)}
            aria-pressed={active}
            aria-label={language.native}
            title={language.native}
            lang={language.code}
            className={[
              "inline-flex min-h-[28px] min-w-[32px] items-center justify-center rounded-full px-2 text-[11px] font-semibold tracking-[0.1em] transition",
              active
                ? "bg-brand/15 text-brand shadow-[inset_0_0_0_1px_rgba(34,211,238,0.3)]"
                : "text-muted hover:bg-surface-2 hover:text-text",
            ].join(" ")}
          >
            {language.short}
          </button>
        );
      })}
    </div>
  );
}

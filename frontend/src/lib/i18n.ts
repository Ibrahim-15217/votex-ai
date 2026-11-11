/**
 * Public entry point for interface localisation.
 *
 * The copy itself lives in `./locales/*`, and the React provider lives in
 * `./language`. Import from here so screens never reach into the dictionaries.
 */
export {
  LanguageProvider,
  formatRelative,
  languages,
  localeTag,
  useI18n,
  type Lang,
  type Language,
  type Translate,
  type TranslationKey,
} from "./language";

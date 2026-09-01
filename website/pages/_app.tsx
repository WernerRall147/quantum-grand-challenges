import type { AppProps } from 'next/app';

export default function App({ Component, pageProps }: AppProps) {
  // The Clarity tag is in <head> via _document.tsx, so it records from first
  // paint rather than from after hydration. Nothing to load here.
  return <Component {...pageProps} />;
}

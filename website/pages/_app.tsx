import { useEffect } from 'react';
import type { AppProps } from 'next/app';
import { loadClarity } from '../lib/clarity';

export default function App({ Component, pageProps }: AppProps) {
  // After mount, so the tag never blocks first paint. No-ops unless
  // NEXT_PUBLIC_CLARITY_PROJECT_ID was set at build time.
  useEffect(() => {
    loadClarity();
  }, []);

  return <Component {...pageProps} />;
}

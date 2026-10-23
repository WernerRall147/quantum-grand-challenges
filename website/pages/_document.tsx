import { Html, Head, Main, NextScript } from 'next/document';
import { CLARITY_PROJECT_ID } from '../lib/clarity';

// Microsoft's snippet, verbatim, in <head> as their install page specifies.
//
// It lives here rather than in _app.tsx on purpose. Injecting it after React
// mounts means Clarity starts recording after hydration and misses the initial
// page load - the first paint, the first scroll, and any rage clicks on a slow
// load, which is exactly the part worth seeing. _document renders at build time
// for a static export, so this ends up literally in the exported HTML and runs
// before the app does.
//
// The project id is inlined from NEXT_PUBLIC_CLARITY_PROJECT_ID at build time.
// Unset, the whole <script> is omitted - see website/lib/clarity.ts.
const clarityScript = `(function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "${CLARITY_PROJECT_ID}");`;

// Inline, so the icon cannot 404 under the GitHub Pages base path.
const favicon = `data:image/svg+xml,${encodeURIComponent(
  "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>" +
    "<rect width='64' height='64' rx='14' fill='#1a1a4e'/>" +
    "<g fill='none' stroke='#a5b4fc' stroke-width='3'>" +
    "<ellipse cx='32' cy='32' rx='24' ry='9'/>" +
    "<ellipse cx='32' cy='32' rx='24' ry='9' transform='rotate(60 32 32)'/>" +
    "<ellipse cx='32' cy='32' rx='24' ry='9' transform='rotate(120 32 32)'/>" +
    "</g><circle cx='32' cy='32' r='5' fill='#818cf8'/></svg>",
)}`;

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <link rel="icon" href={favicon} />
        {CLARITY_PROJECT_ID ? (
          <script
            type="text/javascript"
            dangerouslySetInnerHTML={{ __html: clarityScript }}
          />
        ) : null}
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}

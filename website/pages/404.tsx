export default function Custom404() {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <h1 style={{ fontSize: '4rem', margin: 0 }}>404</h1>
      <p style={{ fontSize: '1.5rem', color: '#666' }}>Page Not Found</p>
      <a href="/" style={{ marginTop: '2rem', color: '#0070f3', textDecoration: 'none', fontSize: '1.1rem' }}>
        ← Back to Home
      </a>
    </div>
  );
}

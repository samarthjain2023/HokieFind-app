// HokieFind primitive components — NavBar, Button, Field, Card, Badge, Message
// Pulled from the patterns actually present in frontend/*.html — just cleanly factored.

function NavBar({ route, go, authed = true, isAdmin = false, onLogout }) {
  return (
    <div className="hf-nav">
      <div className="hf-nav-left">
        <div className="hf-nav-mark">HF</div>
        <div className="hf-nav-wordmark" onClick={() => go(authed ? "listings" : "login")} style={{cursor:"pointer"}}>
          HokieFind
        </div>
      </div>
      <div className="hf-nav-right">
        {!authed ? (
          <>
            <button className="hf-btn hf-btn-nav" onClick={() => go("signup")}>Sign Up</button>
          </>
        ) : (
          <>
            <button className="hf-btn hf-btn-nav" onClick={() => go("listings")}>Home</button>
            <button className="hf-btn hf-btn-nav" onClick={() => go("account")}>Account</button>
            <button className="hf-btn hf-btn-nav" onClick={() => go("reports")}>Reports</button>
            {isAdmin && (
              <button className="hf-btn hf-btn-nav" onClick={() => go("admin")}>Admin</button>
            )}
            <button type="button" className="hf-btn hf-btn-nav ghost" onClick={() => onLogout && onLogout()}>
              Logout
            </button>
          </>
        )}
      </div>
    </div>
  );
}

function Field({ label, name, type = "text", placeholder, value, onChange, required }) {
  return (
    <div className="hf-field-group">
      {label && <label className="hf-label" htmlFor={name}>{label}</label>}
      <input
        id={name}
        name={name}
        type={type}
        placeholder={placeholder}
        required={required}
        className="hf-field"
        value={value || ""}
        onChange={e => onChange && onChange(e.target.value)}
      />
    </div>
  );
}

function TextArea({ label, name, placeholder, value, onChange, required }) {
  return (
    <div className="hf-field-group">
      {label && <label className="hf-label" htmlFor={name}>{label}</label>}
      <textarea
        id={name}
        name={name}
        placeholder={placeholder}
        required={required}
        className="hf-field hf-textarea"
        value={value || ""}
        onChange={e => onChange && onChange(e.target.value)}
      />
    </div>
  );
}

function Card({ title, intro, children }) {
  return (
    <div className="hf-card">
      {title && <h2 className="hf-card-title">{title}</h2>}
      {intro && <p className="hf-card-intro">{intro}</p>}
      {children}
    </div>
  );
}

function Badge({ kind = "active", children }) {
  return <span className={`hf-badge hf-badge-${kind}`}>{children}</span>;
}

function Message({ kind = "error", children }) {
  return <div className={`hf-msg hf-msg-${kind}`}>{children}</div>;
}

function PageHeader({ title, sub }) {
  return (
    <>
      <h1 className="hf-page-title">{title}</h1>
      {sub && <p className="hf-page-sub">{sub}</p>}
    </>
  );
}

Object.assign(window, { NavBar, Field, TextArea, Card, Badge, Message, PageHeader });

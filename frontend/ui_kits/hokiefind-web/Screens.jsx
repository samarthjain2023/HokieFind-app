// HokieFind screens — wired to Flask `/api/*` (session cookies).

/** Maps DB `claim_status.status_name` to `Badge` / `.hf-badge-*` kind. */
function claimStatusBadgeKind(statusName) {
  const s = (statusName || "").trim().toLowerCase();
  if (s === "approved") return "returned";
  if (s === "pending") return "pending";
  if (s.includes("review")) return "review";
  if (s === "rejected") return "rejected";
  if (s === "closed") return "closed";
  return "pending";
}

function LoginScreen({ go, setAuthed, setRole, setUserProfile, setState, flash }) {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [err, setErr] = React.useState(null);
  const [busy, setBusy] = React.useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);
    if (!email || !password) {
      setErr("Hmm, looks like a few fields are missing — mind filling them in?");
      return;
    }
    setBusy(true);
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setErr(data.error === "invalid" ? "That email or password does not match our records." : "Could not sign you in.");
        return;
      }
      setAuthed(true);
      setRole(data.role || "user");
      const meRes = await fetch("/api/me", { credentials: "same-origin" });
      const me = await meRes.json();
      if (me.authenticated) setUserProfile(me);
      const lr = await fetch("/api/listings", { credentials: "same-origin" });
      const lj = await lr.json();
      if (lr.ok) setState((s) => ({ ...s, listings: lj.listings || [] }));
      go("listings");
    } catch (_) {
      setErr("Network error — try again?");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="hf-container-sm">
      <div className="hf-card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="hf-login-hero">
          <div className="display">Find what&apos;s lost.</div>
          <p className="sub">Sign in with your VT email — help a fellow Hokie out.</p>
        </div>
        <div style={{ padding: "24px" }}>
          {flash && <Message kind={flash.kind}>{flash.msg}</Message>}
          {err && <Message kind="error">{err}</Message>}
          <form onSubmit={submit}>
            <Field label="Email" name="email" placeholder="you@vt.edu" value={email} onChange={setEmail} />
            <Field label="Password" name="password" type="password" placeholder="••••••••" value={password} onChange={setPassword} />
            <button type="submit" className="hf-btn hf-btn-primary" style={{ width: "100%", justifyContent: "center" }} disabled={busy}>
              {busy ? "Signing in…" : "Login"}
            </button>
          </form>
          <div style={{ marginTop: 16, fontSize: 14, color: "var(--fg-muted)" }}>
            Don&apos;t have an account?{" "}
            <a className="hf-link" onClick={() => go("signup")}>Sign Up</a>
          </div>
        </div>
      </div>
    </div>
  );
}

function SignUpScreen({ go, setFlash }) {
  const [first, setFirst] = React.useState("");
  const [last, setLast] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [err, setErr] = React.useState(null);
  const [busy, setBusy] = React.useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);
    if (!first || !last || !email || !password) {
      setErr("Please fill in every field.");
      return;
    }
    setBusy(true);
    try {
      const res = await fetch("/api/signup", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ first, last, email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setErr(data.error === "user_exists" ? "That email is already registered." : "Could not create account.");
        return;
      }
      setFlash({ kind: "success", msg: "Account created — you can sign in now." });
      go("login");
    } catch (_) {
      setErr("Network error — try again?");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="hf-container-sm">
      <Card title="Create your account">
        {err && <Message kind="error">{err}</Message>}
        <form onSubmit={submit}>
          <div style={{ display: "flex", gap: 12 }}>
            <div style={{ flex: 1 }}><Field label="First name" name="first" placeholder="Alex" value={first} onChange={setFirst} /></div>
            <div style={{ flex: 1 }}><Field label="Last name" name="last" placeholder="Nguyen" value={last} onChange={setLast} /></div>
          </div>
          <Field label="Email" name="email" placeholder="you@vt.edu" value={email} onChange={setEmail} />
          <Field label="Password" name="password" type="password" placeholder="••••••••" value={password} onChange={setPassword} />
          <button type="submit" className="hf-btn hf-btn-primary" style={{ width: "100%", justifyContent: "center" }} disabled={busy}>
            {busy ? "Creating…" : "Create account"}
          </button>
        </form>
        <div style={{ marginTop: 14, fontSize: 14, color: "var(--fg-muted)" }}>
          Already have an account? <a className="hf-link" onClick={() => go("login")}>Login</a>
        </div>
      </Card>
    </div>
  );
}

function ListingsScreen({ go, state, setState, flash, setFlash, loadListings }) {
  const [title, setTitle] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [location, setLocation] = React.useState("");
  const [imageUrl, setImageUrl] = React.useState("");
  const [imageFile, setImageFile] = React.useState(null);
  const [imagePreview, setImagePreview] = React.useState(null);
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    loadListings();
  }, [loadListings]);

  const handleFile = (file) => {
    if (!file) { setImageFile(null); setImagePreview(null); return; }
    if (file.size > 5 * 1024 * 1024) {
      setFlash({ kind: "error", msg: "That file's a bit big (5 MB max). Try a smaller one?" });
      return;
    }
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target.result);
    reader.readAsDataURL(file);
  };

  const add = async (e) => {
    e.preventDefault();
    if (!title || !description || !location) {
      setFlash({ kind: "error", msg: "Hmm, a few fields are missing — mind filling them in?" });
      return;
    }
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("title", title);
      fd.append("description", description);
      fd.append("location", location);
      if (imageFile) fd.append("image_file", imageFile);
      else if (imageUrl.trim()) fd.append("image", imageUrl.trim());
      const res = await fetch("/api/listings", { method: "POST", body: fd, credentials: "same-origin" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (data.error === "invalid_image") setFlash({ kind: "error", msg: "Image type not allowed (PNG, JPG, GIF, WebP)." });
        else if (res.status === 413) setFlash({ kind: "error", msg: "File too large (5 MB max)." });
        else setFlash({ kind: "error", msg: "Could not post listing." });
        return;
      }
      await loadListings();
      setTitle(""); setDescription(""); setLocation(""); setImageUrl(""); setImageFile(null); setImagePreview(null);
      setFlash({ kind: "success", msg: "Posted! Thanks for helping a fellow Hokie out." });
    } catch (_) {
      setFlash({ kind: "error", msg: "Network error — try again?" });
    } finally {
      setBusy(false);
    }
  };

  const del = async (id) => {
    if (!window.confirm("Remove this listing?")) return;
    try {
      const res = await fetch(`/api/listings/${id}`, { method: "DELETE", credentials: "same-origin" });
      if (!res.ok) { setFlash({ kind: "error", msg: "Could not delete." }); return; }
      setState((s) => ({ ...s, listings: (s.listings || []).filter((l) => l.id !== id) }));
      setFlash({ kind: "success", msg: "Listing removed." });
    } catch (_) {
      setFlash({ kind: "error", msg: "Network error." });
    }
  };

  return (
    <div className="hf-container">
      <PageHeader title="What's been found" sub="Items your fellow Hokies have spotted around campus." />
      {flash && <Message kind={flash.kind}>{flash.msg}</Message>}

      <Card title="Post something you found" intro="Found something on campus? Help a fellow Hokie out — it only takes a sec.">
        <form onSubmit={add}>
          <Field label="Item Title" name="title" placeholder="e.g. Blue Hydro Flask" value={title} onChange={setTitle} />
          <Field label="Description" name="description" placeholder="Color, condition, distinguishing marks" value={description} onChange={setDescription} />
          <Field label="Where you found it" name="location" placeholder="e.g. Newman Library, 2nd floor" value={location} onChange={setLocation} />

          <div className="hf-field-group">
            <label className="hf-label">Add a photo (optional, but it really helps)</label>
            {imagePreview
              ? <div className="hf-upload-preview">
                  <img src={imagePreview} alt="" />
                  <button type="button" className="hf-upload-remove" onClick={() => { setImageFile(null); setImagePreview(null); }}>Remove</button>
                </div>
              : <label className="hf-btn hf-btn-secondary" style={{ cursor: "pointer" }}>
                  <span>+ Upload a photo</span>
                  <input type="file" accept="image/png,image/jpeg,image/gif,image/webp" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files[0])} />
                </label>
            }
            {!imagePreview && (
              <div style={{ fontSize: 12, color: "var(--fg-muted)", marginTop: 6 }}>PNG, JPG, GIF, or WebP · up to 5 MB</div>
            )}
          </div>

          {!imagePreview && (
            <Field label="…or paste an image URL" name="imageUrl" placeholder="https://…" value={imageUrl} onChange={setImageUrl} />
          )}

          <button type="submit" className="hf-btn hf-btn-primary" disabled={busy}>{busy ? "Posting…" : "Post It"}</button>
        </form>
      </Card>

      <Card title="All listings">
        {(!state.listings || state.listings.length === 0)
          ? <div className="hf-empty">No listings yet — be the first to post one!</div>
          : state.listings.map((item) => (
              <ListingRow
                key={item.id}
                item={item}
                showActions={item.mine ? "owner" : "public"}
                onEdit={() => { setState((s) => ({ ...s, editingListingId: item.id })); go("editListing"); }}
                onDelete={() => del(item.id)}
                onClaim={() => { setState((s) => ({ ...s, activeListingId: item.id })); go("claim"); }}
                onViewClaims={() => { setState((s) => ({ ...s, activeListingId: item.id })); go("claimsList"); }}
              />
            ))
        }
      </Card>
    </div>
  );
}

function ClaimFormScreen({ go, state, setFlash, loadListings }) {
  const [message, setMessage] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const item = (state.listings || []).find((l) => l.id === state.activeListingId) || (state.listings || [])[0];

  const submit = async (e) => {
    e.preventDefault();
    if (!message.trim() || !state.activeListingId) return;
    setBusy(true);
    try {
      const res = await fetch(`/api/listings/${state.activeListingId}/claims`, {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok) { setFlash({ kind: "error", msg: "Could not submit claim." }); return; }
      setFlash({ kind: "success", msg: "Claim submitted." });
      await loadListings();
      go("listings");
    } catch (_) {
      setFlash({ kind: "error", msg: "Network error." });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="hf-container">
      <PageHeader title="Claim Item" sub={item ? `Claim "${item.title}"` : ""} />
      <Card title="Submit a claim" intro="Tell us why this item is yours — a distinguishing detail helps the finder verify.">
        <form onSubmit={submit}>
          <TextArea name="message" placeholder="It's my navy blue Hydro Flask — has a sticker of Enter Sandman on the bottom." value={message} onChange={setMessage} />
          <div style={{ display: "flex", gap: 10 }}>
            <button type="submit" className="hf-btn hf-btn-accent" disabled={busy}>{busy ? "Submitting…" : "Submit Claim"}</button>
            <button type="button" className="hf-btn hf-btn-secondary" onClick={() => go("listings")}>Back to Listings</button>
          </div>
        </form>
      </Card>
    </div>
  );
}

function ClaimsListScreen({ go, state }) {
  const [claims, setClaims] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!state.activeListingId) { setLoading(false); return; }
      try {
        const res = await fetch(`/api/listings/${state.activeListingId}/claims`, { credentials: "same-origin" });
        const j = await res.json();
        if (!cancelled && res.ok) setClaims(j.claims || []);
      } catch (_) {
        if (!cancelled) setClaims([]);
      }
      if (!cancelled) setLoading(false);
    })();
    return () => { cancelled = true; };
  }, [state.activeListingId]);

  return (
    <div className="hf-container">
      <PageHeader title="Claims" />
      <Card title="Submitted claims">
        {loading ? <div className="hf-empty">Loading…</div>
          : claims.length === 0
            ? <div className="hf-empty">No claims yet.</div>
            : claims.map((c) => <ClaimRow key={c.id} claim={c} />)
        }
        <div style={{ marginTop: 14 }}>
          <a className="hf-link" onClick={() => go("listings")}>← Back to Listings</a>
        </div>
      </Card>
    </div>
  );
}

function AccountScreen({ userProfile, setFlash, go, setState }) {
  const [mine, setMine] = React.useState([]);
  const [curPw, setCurPw] = React.useState("");
  const [newPw, setNewPw] = React.useState("");
  const [pwBusy, setPwBusy] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/account/listings", { credentials: "same-origin" });
        const j = await res.json();
        if (!cancelled && res.ok) setMine(j.listings || []);
      } catch (_) {
        if (!cancelled) setMine([]);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const changePassword = async (e) => {
    e.preventDefault();
    setPwBusy(true);
    try {
      const res = await fetch("/api/account/password", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_password: curPw, new_password: newPw }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (data.error === "wrong_password") setFlash({ kind: "error", msg: "Current password is incorrect." });
        else setFlash({ kind: "error", msg: "Could not update password." });
        return;
      }
      setCurPw(""); setNewPw("");
      setFlash({ kind: "success", msg: "Password updated." });
    } catch (_) {
      setFlash({ kind: "error", msg: "Network error." });
    } finally {
      setPwBusy(false);
    }
  };

  const delMine = async (id) => {
    if (!window.confirm("Remove this listing?")) return;
    try {
      const res = await fetch(`/api/listings/${id}`, { method: "DELETE", credentials: "same-origin" });
      if (!res.ok) return;
      setMine((m) => m.filter((l) => l.id !== id));
      setState((s) => ({ ...s, listings: (s.listings || []).filter((l) => l.id !== id) }));
      setFlash({ kind: "success", msg: "Listing deleted." });
    } catch (_) {}
  };

  const name = userProfile ? `${userProfile.first_name || ""} ${userProfile.last_name || ""}`.trim() : "";
  const email = userProfile && userProfile.email;

  return (
    <div className="hf-container">
      <PageHeader title="Account" />
      <Card title="Account info">
        <p style={{ margin: 0, lineHeight: 1.7 }}>
          <strong>Name:</strong> {name || "—"}<br />
          <strong>Email:</strong> {email || "—"}<br />
        </p>
      </Card>

      <Card title="Your listings">
        {mine.length === 0
          ? <div className="hf-empty">No listings yet.</div>
          : mine.map((item) => (
              <ListingRow
                key={item.id}
                item={item}
                showActions="owner"
                onEdit={() => { setState((s) => ({ ...s, editingListingId: item.id })); go("editListing"); }}
                onDelete={() => delMine(item.id)}
              />
            ))
        }
      </Card>

      <Card title="Change password">
        <form onSubmit={changePassword}>
          <Field label="Current password" name="current" type="password" placeholder="••••••••" value={curPw} onChange={setCurPw} />
          <Field label="New password" name="new" type="password" placeholder="••••••••" value={newPw} onChange={setNewPw} />
          <button type="submit" className="hf-btn hf-btn-primary" disabled={pwBusy}>{pwBusy ? "Saving…" : "Update Password"}</button>
        </form>
      </Card>
    </div>
  );
}

function ReportsScreen() {
  const [finders, setFinders] = React.useState([]);
  const [claims, setClaims] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/reports", { credentials: "same-origin" });
        const j = await res.json();
        if (!cancelled && res.ok) {
          setFinders(j.most_active_finders || []);
          setClaims(j.active_claims || []);
        }
      } catch (_) {
        if (!cancelled) { setFinders([]); setClaims([]); }
      }
      if (!cancelled) setLoading(false);
    })();
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="hf-container">
      <PageHeader title="Reports" sub="Hokies helping Hokies — by the numbers." />

      <Card title="Most Active Finders" intro="The Hokies who've helped the most by posting found items. A little credibility for the people doing the work.">
        {loading ? <div className="hf-empty">Loading…</div>
          : finders.length === 0
            ? <div className="hf-empty">No finder activity yet.</div>
            : (
              <table className="hf-table">
                <thead><tr><th>First name</th><th>Last name</th><th>Total listings</th></tr></thead>
                <tbody>
                  {finders.map((r, i) => (
                    <tr key={i}><td>{r.first_name}</td><td>{r.last_name}</td><td className="mono">{r.total_listings}</td></tr>
                  ))}
                </tbody>
              </table>
              )
        }
      </Card>

      <Card title="Active Claims Status" intro="Open claims and where they stand. Helps everyone keep tabs end-to-end.">
        {loading ? <div className="hf-empty">Loading…</div>
          : claims.length === 0
            ? <div className="hf-empty">No claims match this report (claims need a listing with an item and a status).</div>
            : (
              <table className="hf-table">
                <thead><tr><th>First</th><th>Last</th><th>Item</th><th>Status</th><th>Submitted</th></tr></thead>
                <tbody>
                  {claims.map((c, i) => (
                    <tr key={i}>
                      <td>{c.first_name}</td>
                      <td>{c.last_name}</td>
                      <td>{c.item_name}</td>
                      <td><Badge kind={claimStatusBadgeKind(c.status_name)}>{c.status_name}</Badge></td>
                      <td className="mono">{c.claim_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              )
        }
      </Card>
    </div>
  );
}

function AdminScreen({ setFlash, flash }) {
  const [first, setFirst] = React.useState("");
  const [last, setLast] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [busy, setBusy] = React.useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const res = await fetch("/api/admin/users", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ first, last, email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (res.status === 403) setFlash({ kind: "error", msg: "Admin only." });
        else setFlash({ kind: "error", msg: data.error === "user_exists" ? "User exists." : "Could not create user." });
        return;
      }
      setFirst(""); setLast(""); setEmail(""); setPassword("");
      setFlash({ kind: "success", msg: "User created." });
    } catch (_) {
      setFlash({ kind: "error", msg: "Network error." });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="hf-container-sm">
      <PageHeader title="Admin Panel" />
      {flash && <Message kind={flash.kind}>{flash.msg}</Message>}
      <Card title="Create new user">
        <form onSubmit={submit}>
          <div style={{ display: "flex", gap: 12 }}>
            <div style={{ flex: 1 }}><Field label="First name" name="first" placeholder="Alex" value={first} onChange={setFirst} /></div>
            <div style={{ flex: 1 }}><Field label="Last name" name="last" placeholder="Nguyen" value={last} onChange={setLast} /></div>
          </div>
          <Field label="Email" name="email" placeholder="you@vt.edu" value={email} onChange={setEmail} />
          <Field label="Password" name="password" type="password" placeholder="temporary password" value={password} onChange={setPassword} />
          <button type="submit" className="hf-btn hf-btn-primary" disabled={busy}>{busy ? "Creating…" : "Create User"}</button>
        </form>
      </Card>
    </div>
  );
}

function EditListingScreen({ go, state, setState, setFlash, loadListings }) {
  const id = state.editingListingId;
  const [location, setLocation] = React.useState("");
  const [imageUrl, setImageUrl] = React.useState("");
  const [imageFile, setImageFile] = React.useState(null);
  const [imagePreview, setImagePreview] = React.useState(null);
  const [currentPhoto, setCurrentPhoto] = React.useState(null);
  const [title, setTitle] = React.useState("");
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!id) { go("listings"); return; }
      try {
        const res = await fetch(`/api/listings/${id}`, { credentials: "same-origin" });
        const j = await res.json();
        if (cancelled || !res.ok) return;
        const L = j.listing;
        setLocation(L.location || "");
        setImageUrl(L.photo || "");
        setCurrentPhoto(L.photo || null);
        setTitle(L.title || "");
      } catch (_) {
        go("listings");
      }
    })();
    return () => { cancelled = true; };
  }, [id]);

  const handleFile = (file) => {
    if (!file) { setImageFile(null); setImagePreview(null); return; }
    if (file.size > 5 * 1024 * 1024) {
      setFlash({ kind: "error", msg: "File too large (5 MB max)." });
      return;
    }
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target.result);
    reader.readAsDataURL(file);
  };

  const save = async (e) => {
    e.preventDefault();
    if (!id || !location.trim()) return;
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("location", location.trim());
      if (imageFile) fd.append("image_file", imageFile);
      else fd.append("image", imageUrl.trim());
      const res = await fetch(`/api/listings/${id}`, { method: "PATCH", body: fd, credentials: "same-origin" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (data.error === "invalid_image") setFlash({ kind: "error", msg: "Invalid image." });
        else if (res.status === 413) setFlash({ kind: "error", msg: "File too large." });
        else setFlash({ kind: "error", msg: "Could not save." });
        return;
      }
      await loadListings();
      setFlash({ kind: "success", msg: "Listing updated." });
      go("listings");
    } catch (_) {
      setFlash({ kind: "error", msg: "Network error." });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="hf-container">
      <PageHeader title="Edit listing" sub={title ? `“${title}”` : ""} />
      <Card title="Update location & photo">
        {(currentPhoto && !imagePreview) && (
          <div style={{ marginBottom: 16 }}>
            <p className="hf-card-intro" style={{ marginTop: 0 }}>Current image</p>
            <img src={currentPhoto} alt="" style={{ maxWidth: 220, borderRadius: 8 }} />
          </div>
        )}
        <form onSubmit={save}>
          <Field label="Location found" name="location" value={location} onChange={setLocation} />
          <div className="hf-field-group">
            <label className="hf-label">Replace image (optional)</label>
            {imagePreview
              ? <div className="hf-upload-preview">
                  <img src={imagePreview} alt="" />
                  <button type="button" className="hf-upload-remove" onClick={() => { setImageFile(null); setImagePreview(null); }}>Remove</button>
                </div>
              : <label className="hf-btn hf-btn-secondary" style={{ cursor: "pointer" }}>
                  <span>+ Upload</span>
                  <input type="file" accept="image/png,image/jpeg,image/gif,image/webp" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files[0])} />
                </label>
            }
          </div>
          {!imagePreview && (
            <Field label="Image URL" name="image" placeholder="/static/uploads/… or https://…" value={imageUrl} onChange={setImageUrl} />
          )}
          <div style={{ display: "flex", gap: 10 }}>
            <button type="submit" className="hf-btn hf-btn-primary" disabled={busy}>{busy ? "Saving…" : "Save"}</button>
            <button type="button" className="hf-btn hf-btn-secondary" onClick={() => go("listings")}>Cancel</button>
          </div>
        </form>
      </Card>
    </div>
  );
}

Object.assign(window, {
  LoginScreen,
  SignUpScreen,
  ListingsScreen,
  ClaimFormScreen,
  ClaimsListScreen,
  AccountScreen,
  ReportsScreen,
  AdminScreen,
  EditListingScreen,
});

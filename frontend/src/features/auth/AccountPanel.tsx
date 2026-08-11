import { useState } from "react";
import type { FormEvent } from "react";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { useAuth } from "./AuthContext";

export function AccountPanel() {
  const { user, login, register, logout } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) {
    return (
      <Card title="Account">
        <p className="muted">Signed in as <strong>{user.email}</strong>{user.is_admin ? " (admin)" : ""}.</p>
        <Button variant="ghost" onClick={logout}>Sign out</Button>
      </Card>
    );
  }

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password);
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card title={mode === "login" ? "Sign in" : "Create account"}>
      <form className="account-form" onSubmit={submit}>
        <input className="loc-search__input" type="email" placeholder="Email" required
          value={email} onChange={(e) => setEmail(e.target.value)} aria-label="Email" />
        <input className="loc-search__input" type="password" placeholder="Password (min 6)" required minLength={6}
          value={password} onChange={(e) => setPassword(e.target.value)} aria-label="Password" />
        {error && <p className="state--error">{error}</p>}
        <div className="account-form__actions">
          <Button type="submit" disabled={busy}>{mode === "login" ? "Sign in" : "Register"}</Button>
          <Button type="button" variant="ghost" onClick={() => setMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "Need an account?" : "Have an account?"}
          </Button>
        </div>
      </form>
    </Card>
  );
}

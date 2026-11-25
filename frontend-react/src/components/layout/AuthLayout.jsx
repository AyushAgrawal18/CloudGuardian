import { Activity, ShieldCheck } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

export default function AuthLayout({ children }) {
  const location = useLocation();
  const isSignup = location.pathname === "/signup";

  return (
    <main className={`auth-shell ${isSignup ? "signup-mode" : "login-mode"}`}>
      <aside className="auth-visual">
        <Link to="/login" className="visual-brand">
          <Activity size={27} />
          <span>
            Cloud<span>Guardian</span>
          </span>
        </Link>

        <div className="visual-message">
          <span className="visual-line" />
          <h1>
            {isSignup ? (
              <>
                Secure Your <br /> Infrastructure
              </>
            ) : (
              <>
                Welcome <br /> Back
              </>
            )}
          </h1>
          <p>
            {isSignup
              ? "Create your account and take control of your infrastructure health."
              : "Monitor smarter. Detect earlier. Keep your infrastructure healthy."}
          </p>
        </div>

        <div className="visual-footer">
          <ShieldCheck size={17} />
          <span>Built for infrastructure reliability</span>
        </div>
      </aside>

      <section className="auth-form-area">
        <div className="auth-form-card">{children}</div>

        <div className="auth-security">
          <ShieldCheck size={16} />
          <span>Your data is secure with us</span>
        </div>
      </section>
    </main>
  );
}

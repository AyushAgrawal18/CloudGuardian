import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { User, Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import AuthLayout from "../components/layout/AuthLayout";

export default function Signup() {
  const navigate = useNavigate();
  const { signup } = useAuth();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.password.length < 12) {
      setError("Password must contain at least 12 characters.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await signup({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
      });

      navigate("/login", {
        state: { message: "Account created successfully. Please sign in." },
      });
    } catch (err) {
      setError(err.message || "Unable to create your account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="auth-form-heading">
        <div className="auth-emblem">
          <User size={27} />
        </div>

        <h2>Create Account</h2>
        <p>Join CloudGuardian and monitor your infrastructure</p>
      </div>

      {error && <div className="auth-error">{error}</div>}

      <form onSubmit={handleSubmit} className="auth-form">
        <label htmlFor="full_name">Full Name</label>

        <div className="auth-input-wrap">
          <User size={19} />
          <input
            id="full_name"
            name="full_name"
            placeholder="Your full name"
            value={form.full_name}
            onChange={handleChange}
            minLength={2}
            maxLength={150}
            required
          />
        </div>

        <label htmlFor="email">Email Address</label>

        <div className="auth-input-wrap">
          <Mail size={19} />
          <input
            id="email"
            name="email"
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={handleChange}
            required
          />
        </div>

        <label htmlFor="password">Password</label>

        <div className="auth-input-wrap">
          <Lock size={19} />
          <input
            id="password"
            name="password"
            type={showPassword ? "text" : "password"}
            placeholder="At least 12 characters"
            value={form.password}
            onChange={handleChange}
            minLength={12}
            maxLength={128}
            required
          />

          <button
            type="button"
            className="auth-icon-button"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
          </button>
        </div>

        <label htmlFor="confirmPassword">Confirm Password</label>

        <div className="auth-input-wrap">
          <Lock size={19} />
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            placeholder="Re-enter your password"
            value={form.confirmPassword}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" className="auth-submit" disabled={loading}>
          <span>{loading ? "Creating account..." : "Create Account"}</span>
          <ArrowRight size={21} />
        </button>
      </form>

      <div className="auth-switch">
        Already have an account?
        <Link to="/login">Sign in</Link>
      </div>
    </AuthLayout>
  );
}

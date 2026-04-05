"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { createClient, isSupabaseConfigured } from "@/lib/supabase";
import type { User, Session } from "@supabase/supabase-js";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  configured: boolean;
  signUp: (email: string, password: string) => Promise<{ error: string | null; confirmed: boolean }>;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: string | null }>;
  updatePassword: (newPassword: string) => Promise<{ error: string | null }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isSupabaseConfigured) {
      setLoading(false);
      return;
    }

    const supabase = createClient()!;

    supabase.auth.getSession().then(({ data: { session: s } }) => {
      setSession(s);
      setUser(s?.user ?? null);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, s) => {
      setSession(s);
      setUser(s?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signUp = async (email: string, password: string) => {
    if (!isSupabaseConfigured) return { error: "Supabase не настроен", confirmed: false };
    const supabase = createClient()!;
    const { data, error } = await supabase.auth.signUp({ email, password });
    const confirmed = !!data?.session;
    return { error: error?.message ?? null, confirmed };
  };

  const signIn = async (email: string, password: string) => {
    if (!isSupabaseConfigured) return { error: "Supabase не настроен" };
    const supabase = createClient()!;
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return { error: error?.message ?? null };
  };

  const signOut = async () => {
    if (!isSupabaseConfigured) return;
    const supabase = createClient()!;
    await supabase.auth.signOut();
  };

  const resetPassword = async (email: string) => {
    if (!isSupabaseConfigured) return { error: "Supabase не настроен" };
    const supabase = createClient()!;
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset`,
    });
    return { error: error?.message ?? null };
  };

  const updatePassword = async (newPassword: string) => {
    if (!isSupabaseConfigured) return { error: "Supabase не настроен" };
    const supabase = createClient()!;
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    return { error: error?.message ?? null };
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, configured: isSupabaseConfigured, signUp, signIn, signOut, resetPassword, updatePassword }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

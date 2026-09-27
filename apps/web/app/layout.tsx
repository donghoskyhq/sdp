import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "Sky Dev Platform",
  description: "Internal self-service software delivery platform for Sky teams.",
};

const navigation = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/status", label: "Status" },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-white/10 bg-slate-950/40 backdrop-blur">
          <nav
            aria-label="Primary navigation"
            className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5"
          >
            <Link className="font-semibold tracking-tight" href="/">
              SDP
            </Link>
            <div className="flex gap-6 text-sm text-slate-300">
              {navigation.map((item) => (
                <Link className="transition hover:text-emerald-300" href={item.href} key={item.href}>
                  {item.label}
                </Link>
              ))}
            </div>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}

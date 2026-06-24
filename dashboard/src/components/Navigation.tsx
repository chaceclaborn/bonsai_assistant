"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Settings, LineChart } from "lucide-react";
import clsx from "clsx";

const tabs = [
  { href: "/", label: "Home", Icon: Home },
  { href: "/history", label: "History", Icon: LineChart },
  { href: "/settings", label: "Settings", Icon: Settings },
];

export default function Navigation() {
  const pathname = usePathname();
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-[var(--bg-card)] border-t border-[var(--border)] pb-[env(safe-area-inset-bottom)]">
      <div className="mx-auto max-w-md flex">
        {tabs.map(({ href, label, Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex-1 flex flex-col items-center justify-center py-3 gap-1 transition-colors",
                active ? "text-[var(--green)]" : "text-[var(--text-muted)]"
              )}
            >
              <Icon size={22} />
              <span className="text-xs font-medium">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

import type { Metadata, Viewport } from "next";
import Navigation from "@/components/Navigation";
import ChatWidget from "@/components/ChatWidget";
import ThemeApplier from "@/components/ThemeApplier";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bonsai Assistant",
  description: "Live bonsai care monitoring",
  // The app ships its own dark/light themes, so tell Dark Reader (and similar
  // extensions) not to rewrite the DOM. Also removes the false-positive
  // hydration warnings those extensions cause.
  other: { "darkreader-lock": "darkreader-lock" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#0d1410",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <ThemeApplier />
        <main className="mx-auto max-w-md min-h-screen pb-24">
          {children}
        </main>
        <ChatWidget />
        <Navigation />
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VaaniShield — Real-Time Voice Authenticity Engine",
  description: "AI-powered detection of cloned and synthetic voices in live calls.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#090B10] text-[#EDEFF3] font-body">
        {children}
      </body>
    </html>
  );
}

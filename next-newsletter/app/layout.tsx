import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Service Access",
  description: "Internal service access",
  robots: {
    index: false,
    follow: false,
    nocache: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}

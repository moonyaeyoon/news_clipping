import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "빗썸 BIZ 뉴스레터",
  description: "디지털자산 뉴스 수집 및 이메일 템플릿 생성 도구",
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


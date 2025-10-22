import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
})

export const metadata: Metadata = {
  title: "Loglytics AI - Intelligent Log Analysis Platform",
  description: "Advanced log analysis and monitoring platform with AI-powered insights, real-time streaming, and intelligent alerting.",
  keywords: ["log analysis", "monitoring", "AI", "analytics", "observability", "devops"],
  authors: [{ name: "Loglytics AI Team" }],
  creator: "Loglytics AI",
  publisher: "Loglytics AI",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"),
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "/",
    title: "Loglytics AI - Intelligent Log Analysis Platform",
    description: "Advanced log analysis and monitoring platform with AI-powered insights, real-time streaming, and intelligent alerting.",
    siteName: "Loglytics AI",
  },
  twitter: {
    card: "summary_large_image",
    title: "Loglytics AI - Intelligent Log Analysis Platform",
    description: "Advanced log analysis and monitoring platform with AI-powered insights, real-time streaming, and intelligent alerting.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    google: "your-google-verification-code",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={true}
          disableTransitionOnChange={false}
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
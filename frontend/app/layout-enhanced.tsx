import './globals.css'
import type { Metadata, Viewport } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from 'sonner'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Analytics } from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'NSAI Orchestrator MCP | Elite Multi-Agent Platform',
  description: 'World-class production-ready multi-agent orchestration platform with intelligent task routing, advanced memory management, and real-time collaboration.',
  keywords: ['AI', 'orchestration', 'multi-agent', 'MCP', 'Claude', 'Codex', 'enterprise', 'production'],
  authors: [{ name: 'NSAI Team' }],
  creator: 'NSAI Team',
  publisher: 'NSAI',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://nsai-orchestrator.vercel.app',
    title: 'NSAI Orchestrator MCP',
    description: 'Elite Multi-Agent Orchestration Platform',
    siteName: 'NSAI Orchestrator',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'NSAI Orchestrator MCP',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'NSAI Orchestrator MCP',
    description: 'Elite Multi-Agent Orchestration Platform',
    images: ['/twitter-image.png'],
    creator: '@nsai_tech',
  },
  manifest: '/manifest.json',
  alternates: {
    canonical: 'https://nsai-orchestrator.vercel.app',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#000000' },
  ],
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      gcTime: 5 * 60 * 1000, // 5 minutes
      retry: (failureCount, error) => {
        if (error instanceof Error) {
          // Don't retry on 4xx errors
          if (error.message.includes('4')) return false
        }
        return failureCount < 3
      },
      refetchOnWindowFocus: false,
    },
  },
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html 
      lang="en" 
      className={`${inter.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="theme-color" content="#000000" />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <QueryClientProvider client={queryClient}>
            <div className="relative flex min-h-screen flex-col">
              <div className="flex-1">
                {children}
              </div>
            </div>
            
            <Toaster 
              richColors
              closeButton
              position="bottom-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--background)',
                  color: 'var(--foreground)',
                  border: '1px solid var(--border)',
                },
              }}
            />
            
            {process.env.NODE_ENV === 'development' && (
              <ReactQueryDevtools initialIsOpen={false} />
            )}
          </QueryClientProvider>
        </ThemeProvider>
        
        <Analytics />
        <SpeedInsights />
        
        {/* Accessibility Skip Links */}
        <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-background focus:px-4 focus:py-2 focus:outline-none focus:ring-2 focus:ring-ring">
          Skip to main content
        </a>
        
        {/* PWA Update Banner */}
        <div id="pwa-update-banner" className="hidden fixed bottom-0 left-0 right-0 z-50 bg-primary p-4 text-primary-foreground">
          <div className="container mx-auto flex items-center justify-between">
            <p className="text-sm font-medium">A new version is available!</p>
            <button
              onClick={() => window.location.reload()}
              className="rounded-md bg-primary-foreground px-3 py-1 text-xs font-medium text-primary hover:bg-primary-foreground/90"
            >
              Update Now
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}
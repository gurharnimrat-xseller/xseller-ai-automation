import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import ClientLayout from './components/ClientLayout';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'Xseller.ai - Social Media Automation Dashboard',
    description: 'AI-powered social media content generation and scheduling platform',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <ClientLayout>{children}</ClientLayout>
            </body>
        </html>
    );
}


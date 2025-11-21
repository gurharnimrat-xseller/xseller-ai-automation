import { Header } from "@/components/layout/Header"
import { Sidebar } from "@/components/layout/Sidebar"

interface MainLayoutProps {
    children: React.ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
    return (
        <div className="flex min-h-screen flex-col md:flex-row">
            <Sidebar className="hidden w-64 flex-shrink-0 md:block" />
            <div className="flex flex-1 flex-col">
                <Header />
                <main className="flex-1 p-6 bg-muted/10">{children}</main>
            </div>
        </div>
    )
}
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/utils/cn";

export function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Predictor", href: "/predict" },
    { name: "Analytics", href: "/analytics" },
    { name: "Players", href: "/players" },
    { name: "Fantasy", href: "/fantasy" },
    { name: "Venues", href: "/venues" },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4 bg-white/5 backdrop-blur-lg border-b border-white/5 transition-all duration-300">
      <Link href="/" className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600 hover:opacity-80 transition-opacity">
        IPL Analytics
      </Link>
      
      <div className="flex gap-8">
        {navItems.map((item) => (
          <Link 
            key={item.name} 
            href={item.href}
            className={cn(
              "text-sm font-medium transition-colors hover:text-white",
              pathname === item.href ? "text-white neon-text" : "text-gray-400"
            )}
          >
            {item.name}
          </Link>
        ))}
      </div>
    </nav>
  );
}

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-8 bg-[url('https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2605&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat bg-fixed">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/40 z-0" />
      
      <div className="relative z-10 w-full max-w-6xl space-y-12">
          <div className="flex flex-col items-center justify-center space-y-6 pt-20">
            <h1 className="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-br from-blue-400 via-purple-400 to-emerald-400 animate-in fade-in slide-in-from-bottom-4 duration-1000 tracking-tight">
              IPL Advanced Analytics
            </h1>
            <p className="text-xl md:text-2xl text-gray-200 max-w-2xl mx-auto font-light leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
              Leveraging <span className="text-cyan-400 font-semibold">Machine Learning</span> to predict outcomes, analyze player performance, and uncover hidden patterns in cricket data.
            </p>
            
            <div className="pt-8 animate-in fade-in zoom-in duration-1000 delay-300">
              <Link href="/predict">
                 <Button className="h-14 px-8 text-lg bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-md text-white rounded-full transition-all duration-300 hover:scale-105 hover:shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] group">
                  Start Predicting 
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </div>
          </div>
      </div>
    </div>
  );
}

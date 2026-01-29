import { Download } from "lucide-react";
import YouTubeDownloader from "@/components/YouTubeDownloader";

const Index = () => {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-accent/5 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-12 md:py-20">
        {/* Header */}
        <div className="text-center mb-12 md:mb-16 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent mb-6 shadow-glow">
            <Download className="h-8 w-8 text-primary-foreground" />
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4">
            <span className="gradient-text">YouTube</span>{" "}
            <span className="text-foreground">Downloader</span>
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-md mx-auto">
            Download videos and playlists in MP3 or MP4 format with ease
          </p>
        </div>

        {/* Downloader Component */}
        <YouTubeDownloader />

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-16 max-w-3xl mx-auto">
          {[
            { title: "Fast Downloads", desc: "Optimized for speed and efficiency" },
            { title: "Multiple Formats", desc: "Support for MP3 audio and MP4 video" },
            { title: "Playlist Support", desc: "Download entire playlists at once" },
          ].map((feature, i) => (
            <div
              key={i}
              className="text-center p-6 rounded-xl bg-card/50 border border-border/30 hover:border-primary/30 transition-all duration-300 animate-fade-in"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <h3 className="font-semibold text-foreground mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Index;

import { useState, useEffect } from "react";
import { Download, Music, Video, Link, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

type DownloadStatus = "idle" | "downloading" | "ready" | "error";

const YouTubeDownloader = () => {
  const [url, setUrl] = useState("");
  const [format, setFormat] = useState<"mp3" | "mp4">("mp3");
  const [quality, setQuality] = useState("192");
  const [status, setStatus] = useState<DownloadStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");

  const audioQualities = ["128", "192", "320"];
  const videoQualities = ["360p", "480p", "720p", "1080p"];

  const isValidUrl = (input: string) => {
    return input.includes("youtube.com") || input.includes("youtu.be");
  };

  const startRealDownload = async () => {
    if (!url || !isValidUrl(url)) {
      setStatus("error");
      setStatusMessage("Please enter a valid YouTube URL");
      toast.error("Invalid URL");
      return;
    }

    setStatus("downloading");
    setProgress(0);
    setStatusMessage("Connecting to backend...");

    try {
      // 1. Send request to FastAPI backend
      const response = await fetch("http://127.0.0.1:8000/start-download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          url: url, 
          quality: quality, 
          file_format: format 
        }),
      });

      if (!response.ok) throw new Error("Failed to start download");

      // 2. Poll for progress every second
      const interval = setInterval(async () => {
        try {
          const res = await fetch("http://127.0.0.1:8000/progress");
          const data = await res.json();

          setProgress(data.percentage);
          setStatusMessage(data.status);

          if (data.status === "ready") {
            clearInterval(interval);
            setStatus("ready");
            setStatusMessage("✅ Download Complete! Your ZIP is ready.");
            toast.success("Ready for download!");
          } else if (data.status.includes("error")) {
            clearInterval(interval);
            setStatus("error");
            setStatusMessage(data.status);
            toast.error("Download failed");
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 1000);

    } catch (error) {
      setStatus("error");
      setStatusMessage("Could not connect to backend. Ensure Python app is running.");
      toast.error("Backend Connection Failed");
    }
  };

  const handleDownloadZip = () => {
    // 3. Trigger the actual file download from Python server
    window.location.href = "http://127.0.0.1:8000/get-zip";
    
    // Reset UI after a short delay
    setTimeout(() => {
      setStatus("idle");
      setProgress(0);
      setUrl("");
    }, 2000);
  };

  return (
    <div className="w-full max-w-2xl mx-auto animate-fade-in">
      <div className="glass rounded-2xl p-8 shadow-lg">
        {/* URL Input */}
        <div className="space-y-3 mb-8">
          <Label htmlFor="url" className="text-sm font-medium text-muted-foreground">
            YouTube URL
          </Label>
          <div className="relative">
            <Link className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              id="url"
              type="text"
              placeholder="https://www.youtube.com/playlist?list=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="pl-12 h-14 bg-muted/50 border-border/50 text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary/20 rounded-xl text-base"
            />
          </div>
        </div>

        {/* Format & Quality Selection */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="space-y-3">
            <Label className="text-sm font-medium text-muted-foreground">Format</Label>
            <RadioGroup
              value={format}
              onValueChange={(value: "mp3" | "mp4") => {
                setFormat(value);
                setQuality(value === "mp3" ? "192" : "720p");
              }}
              className="flex gap-3"
            >
              <Label
                htmlFor="mp3"
                className={cn(
                  "flex-1 flex items-center justify-center gap-3 p-4 rounded-xl cursor-pointer transition-all duration-200 border",
                  format === "mp3"
                    ? "bg-primary/10 border-primary text-primary"
                    : "bg-muted/30 border-border/50 text-muted-foreground hover:bg-muted/50"
                )}
              >
                <RadioGroupItem value="mp3" id="mp3" className="sr-only" />
                <Music className="h-5 w-5" />
                <span className="font-medium">MP3</span>
              </Label>
              <Label
                htmlFor="mp4"
                className={cn(
                  "flex-1 flex items-center justify-center gap-3 p-4 rounded-xl cursor-pointer transition-all duration-200 border",
                  format === "mp4"
                    ? "bg-primary/10 border-primary text-primary"
                    : "bg-muted/30 border-border/50 text-muted-foreground hover:bg-muted/50"
                )}
              >
                <RadioGroupItem value="mp4" id="mp4" className="sr-only" />
                <Video className="h-5 w-5" />
                <span className="font-medium">MP4</span>
              </Label>
            </RadioGroup>
          </div>

          <div className="space-y-3">
            <Label className="text-sm font-medium text-muted-foreground">
              {format === "mp3" ? "Bitrate (kbps)" : "Max Resolution"}
            </Label>
            <Select value={quality} onValueChange={setQuality}>
              <SelectTrigger className="h-14 bg-muted/30 border-border/50 rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-card border-border">
                {(format === "mp3" ? audioQualities : videoQualities).map((q) => (
                  <SelectItem key={q} value={q} className="cursor-pointer">
                    {q}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Progress Section */}
        {status !== "idle" && (
          <div className="mb-8 p-5 rounded-xl bg-muted/30 border border-border/50 animate-scale-in">
            <div className="flex items-center gap-3 mb-4">
              {status === "downloading" && (
                <Loader2 className="h-5 w-5 text-primary animate-spin" />
              )}
              {status === "ready" && (
                <CheckCircle className="h-5 w-5 text-green-500" />
              )}
              {status === "error" && (
                <AlertCircle className="h-5 w-5 text-destructive" />
              )}
              <span className={cn(
                "text-sm font-medium",
                status === "ready" && "text-green-500",
                status === "error" && "text-destructive",
                status === "downloading" && "text-foreground"
              )}>
                {statusMessage}
              </span>
            </div>
            {status === "downloading" && (
              <div className="space-y-2">
                <Progress value={progress} className="h-2" />
                <p className="text-xs text-muted-foreground text-right">{Math.round(progress)}%</p>
              </div>
            )}
          </div>
        )}

        {/* Action Button */}
        {status === "ready" ? (
          <Button
            variant="default"
            size="lg"
            className="w-full h-14 rounded-xl bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-opacity"
            onClick={handleDownloadZip}
          >
            <Download className="h-5 w-5 mr-2" />
            Download ZIP File
          </Button>
        ) : (
          <Button
            variant="default"
            size="lg"
            className="w-full h-14 rounded-xl bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-opacity"
            onClick={startRealDownload}
            disabled={status === "downloading"}
          >
            {status === "downloading" ? (
              <>
                <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                Processing Playlist...
              </>
            ) : (
              <>
                <Download className="h-5 w-5 mr-2" />
                Start Download
              </>
            )}
          </Button>
        )}
      </div>

      <p className="text-center text-sm text-muted-foreground mt-6">
        Note: Large playlists may take a few minutes to process. Please don't refresh the page.
      </p>
    </div>
  );
};

export default YouTubeDownloader;
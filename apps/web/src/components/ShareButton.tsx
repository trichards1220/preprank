"use client";

import { useState } from "react";

interface ShareButtonProps {
  title: string;
  text: string;
  url: string;
}

export default function ShareButton({ title, text, url }: ShareButtonProps) {
  const [copied, setCopied] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const fullUrl = `${url}${url.includes("?") ? "&" : "?"}utm_source=share&utm_medium=direct`;

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({ title, text, url: fullUrl });
      } catch {}
    } else {
      setShowMenu(!showMenu);
    }
  };

  const copyLink = async () => {
    await navigator.clipboard.writeText(fullUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    setShowMenu(false);
  };

  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(fullUrl + "&utm_medium=twitter")}`;
  const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(fullUrl + "&utm_medium=facebook")}`;

  return (
    <div className="relative inline-block">
      <button
        onClick={handleNativeShare}
        className="rounded border border-steel-gray px-3 py-1.5 text-sm text-steel-gray hover:text-white hover:border-crimson transition-colors flex items-center gap-1.5"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
        {copied ? "Copied!" : "Share"}
      </button>

      {showMenu && (
        <div className="absolute right-0 top-full mt-2 z-50 rounded-lg border border-steel-gray/30 bg-charcoal shadow-lg py-2 min-w-[180px]">
          <button onClick={copyLink}
            className="w-full px-4 py-2 text-left text-sm text-steel-gray hover:text-white hover:bg-crimson/10 transition-colors">
            Copy Link
          </button>
          <a href={twitterUrl} target="_blank" rel="noopener noreferrer"
            className="block px-4 py-2 text-sm text-steel-gray hover:text-white hover:bg-crimson/10 transition-colors">
            Share to X / Twitter
          </a>
          <a href={facebookUrl} target="_blank" rel="noopener noreferrer"
            className="block px-4 py-2 text-sm text-steel-gray hover:text-white hover:bg-crimson/10 transition-colors">
            Share to Facebook
          </a>
        </div>
      )}
    </div>
  );
}

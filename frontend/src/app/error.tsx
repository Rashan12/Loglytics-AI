'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Global error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0A0E14]">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-4">Something went wrong!</h2>
        <p className="text-gray-400 mb-6">{error.message}</p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"
        >
          Try again
        </button>
      </div>
    </div>
  );
}

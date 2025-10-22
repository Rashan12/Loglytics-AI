export default function SkeletonCard() {
  return (
    <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6 animate-pulse">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-12 h-12 bg-[#0F1419] rounded-lg" />
        <div className="flex-1">
          <div className="h-6 bg-[#0F1419] rounded w-3/4 mb-2" />
          <div className="h-4 bg-[#0F1419] rounded w-full" />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="h-16 bg-[#0F1419] rounded-lg" />
        <div className="h-16 bg-[#0F1419] rounded-lg" />
        <div className="h-16 bg-[#0F1419] rounded-lg" />
      </div>
      <div className="h-4 bg-[#0F1419] rounded w-1/2" />
    </div>
  );
}

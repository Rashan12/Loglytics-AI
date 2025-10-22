export default function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-8 h-8 border-2',
    md: 'w-16 h-16 border-4',
    lg: 'w-24 h-24 border-4'
  };

  return (
    <div className="flex items-center justify-center">
      <div className={`${sizeClasses[size]} border-blue-600 border-t-transparent rounded-full animate-spin`} />
    </div>
  );
}

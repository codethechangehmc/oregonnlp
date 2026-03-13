import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex items-center justify-center py-28 animate-fade-in">
      <Card className="p-8 max-w-md text-center">
        <div className="w-12 h-12 rounded-full bg-warm-red-dim border border-warm-red/20 flex items-center justify-center mx-auto mb-5">
          <svg
            width="20"
            height="20"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            className="text-warm-red"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"
            />
          </svg>
        </div>
        <h3 className="font-display text-lg font-medium italic text-text-primary mb-2">
          Analysis failed
        </h3>
        <p className="text-sm text-text-muted mb-6 leading-relaxed">{message}</p>
        <Button variant="secondary" onClick={onRetry}>
          Try again
        </Button>
      </Card>
    </div>
  );
}

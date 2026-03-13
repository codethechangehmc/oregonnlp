export default function SampleResponse({ text }: { text: string }) {
  return (
    <li className="text-sm w-full text-text-secondary leading-relaxed py-2 border-b border-border/50 last:border-0 pl-3 relative">
      <span className="left-0 top-3 h-1 rounded-full bg-text-muted/40 w-full" />
      {text}
    </li>
  );
}
